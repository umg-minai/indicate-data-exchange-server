from contextlib import contextmanager
from datetime import datetime
from typing import List

import sqlalchemy.engine.create
from sqlalchemy import select, delete
from sqlalchemy.orm import Session

from indicate_data_exchange_server.config.configuration import DatabaseConfiguration
from indicate_data_exchange_server.db.model import AggregatedResult
from indicate_data_exchange_server.models.attributed_quality_indicator_result import AttributedQualityIndicatorResult
from indicate_data_exchange_server.models.provider_results_post_request import ProviderResultsPostRequest


@contextmanager
def transaction(configuration: DatabaseConfiguration):
    database_url = f'postgresql://{configuration.user}:{configuration.password}@{configuration.host}:{configuration.port}/{configuration.database}'
    connect_args = {"options": f"-csearch_path={configuration.dbschema}"}
    engine = sqlalchemy.create_engine(database_url, connect_args=connect_args)
    with Session(engine) as session:
        yield session
        session.commit()

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

def read_results(session, aggregation_kind, period_start: None | datetime = None) \
        -> List[AttributedQualityIndicatorResult]:
    statement = (select(AggregatedResult)
                 .where(AggregatedResult.aggregation_kind == aggregation_kind))
    if period_start is not None:
        statement = statement.where(AggregatedResult.period_start >= period_start)
    return [
        AttributedQualityIndicatorResult(
            provider_id=aggregated_result.provider_id,
            aggregation_period_start=aggregated_result.period_start,
            indicator_id=aggregated_result.indicator_concept_id,
            average_value=aggregated_result.average_value,
            observation_count=aggregated_result.observation_count
        )
        for aggregated_result in session.scalars(statement)
    ]


