import logging
from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import List

import sqlalchemy.engine.create
from sqlalchemy import select, delete
from sqlalchemy.orm import Session

import indicate_data_exchange_server.db.model
from indicate_data_exchange_server.config.configuration import DatabaseConfiguration
from indicate_data_exchange_server.db.model import AggregatedResult
from indicate_data_exchange_server.models.aggregation_period_kind import AggregationPeriodKind
from indicate_data_exchange_server.models.attributed_quality_indicator_result import AttributedQualityIndicatorResult
from indicate_data_exchange_server.models.indicator_info import IndicatorInfo
from indicate_data_exchange_server.models.provider_results_post_request import ProviderResultsPostRequest

logger = logging.getLogger("database")


@contextmanager
def transaction(configuration: DatabaseConfiguration):
    database_url = sqlalchemy.engine.url.URL.create(
        drivername="postgresql",
        username=configuration.user,
        password=configuration.password,
        host=configuration.host,
        port=configuration.port,
        database=configuration.database,
    )
    connect_args = {"options": f"-csearch_path={configuration.dbschema}"}
    engine = sqlalchemy.create_engine(database_url, connect_args=connect_args)
    with Session(engine) as session:
        yield session
        session.commit()

def read_indicator_info(session):
    return [
        IndicatorInfo(
            concept_id=indicator_info.concept_id,
            title=indicator_info.title,
            description=indicator_info.description,
        )
        for indicator_info in session.scalars(select(indicate_data_exchange_server.db.model.IndicatorInfo))
    ]

def write_results(session, provider_results: ProviderResultsPostRequest):
    provider_id = provider_results.provider_id
    upload_time = datetime.now()
    # Delete all old results for this data provider.
    session.execute(delete(AggregatedResult).where(AggregatedResult.provider_id == provider_id))
    # Write the new results.
    for result in provider_results.results:
        session.add(
            AggregatedResult(
                provider_id=provider_id,
                indicator_concept_id=result.indicator_id,
                aggregation_kind=result.aggregation_period_kind,
                period_start=result.aggregation_period_start,
                average_value=result.average_value,
                observation_count=result.observation_count,
                upload_time=upload_time
        ))

def read_results(session,
                 aggregation_kind,
                 period_start: None | datetime = None,
                 period_end: None | datetime = None,
                 data_provider_count_threshold: None | int = None) \
        -> List[AttributedQualityIndicatorResult]:
    statement = (select(AggregatedResult)
                 .where(AggregatedResult.aggregation_kind == aggregation_kind))
    if period_start is not None:
        statement = statement.where(AggregatedResult.period_start >= period_start)
    if period_end is not None:
        if aggregation_kind == AggregationPeriodKind.WEEKLY:
            period_duration = timedelta(days=7)
        elif aggregation_kind == AggregationPeriodKind.MONTHLY:
            period_duration = timedelta(days=30)
        elif aggregation_kind == AggregationPeriodKind.YEARLY:
            period_duration = timedelta(days=365)
        statement = statement.where(AggregatedResult.period_start <= period_end - period_duration)
    # Group aggregated results by the start of the aggregation period.
    by_indicator_and_period_start = {}
    for aggregated_result in session.scalars(statement):
        key = (aggregated_result.indicator_concept_id, aggregated_result.period_start)
        period_results = by_indicator_and_period_start.get(key, None)
        if period_results is None:
            period_results = []
            by_indicator_and_period_start[key] = period_results
        period_results.append(aggregated_result)
    # Collect results that should be returned by skipping period with data from too few providers.
    usable_results = []
    skip_count = 0
    for period_results in by_indicator_and_period_start.values():
        if data_provider_count_threshold is None or len(period_results) >= data_provider_count_threshold:
            for period_result in period_results:
                usable_results.append(
                    AttributedQualityIndicatorResult(
                        provider_id=period_result.provider_id,
                        aggregation_period_start=period_result.period_start,
                        indicator_id=period_result.indicator_concept_id,
                        average_value=period_result.average_value,
                        observation_count=period_result.observation_count
                    )
                )
        else:
            skip_count += 1
    if skip_count > 0:
        logger.info(f"For {aggregation_kind.name} aggregation, skipped {skip_count} periods with data from fewer than {data_provider_count_threshold} data providers")
    return usable_results
