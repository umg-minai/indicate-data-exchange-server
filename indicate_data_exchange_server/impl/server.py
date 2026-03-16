import logging
from datetime import datetime
from typing import List

from pydantic import StrictStr

import indicate_data_exchange_server.db.database as database
from indicate_data_exchange_server.apis.default_api_base import BaseDefaultApi
from indicate_data_exchange_server.config.configuration import load_configuration
from indicate_data_exchange_server.models.aggregation_period_kind import AggregationPeriodKind
from indicate_data_exchange_server.models.attributed_quality_indicator_result import AttributedQualityIndicatorResult
from indicate_data_exchange_server.models.provider_results_post_request import ProviderResultsPostRequest
from indicate_data_exchange_server.models.indicator_info import IndicatorInfo

logger = logging.getLogger("uvicorn.error")

configuration = load_configuration()

class Server(BaseDefaultApi):

    async def indicator_info_get(
        self,
    ) -> List[IndicatorInfo]:
        with database.transaction(configuration.database) as session:
            return database.read_indicator_info(session)

    async def provider_results_post(
        self,
        provider_results_post_request: ProviderResultsPostRequest,
    ) -> None:
        provider_id = provider_results_post_request.provider_id
        logger.info("[Provider %s] Received results", provider_id)
        counts = dict()
        for result in provider_results_post_request.results:
            kind = result.aggregation_period_kind
            counts[kind] = counts.get(kind, 0) + 1
        order = {AggregationPeriodKind.WEEKLY: 0,
                 AggregationPeriodKind.MONTHLY: 1,
                 AggregationPeriodKind.YEARLY: 2}
        for period_kind, count in sorted(counts.items(), key=lambda pair: order[pair[0]]):
            logger.info("[Provider %s] for %7s aggregation, got %6d result(s)",
                              provider_id,
                              period_kind.name,
                              count)

        with database.transaction(configuration.database) as session:
            database.write_results(session, provider_results_post_request)


    async def results_get(
        self,
        aggregation_kind: StrictStr,
        period_start: None | datetime,
        period_end: None | datetime
    ) -> List[AttributedQualityIndicatorResult]:
        with database.transaction(configuration.database) as session:
            return database.read_results(session, aggregation_kind, period_start, period_end)
