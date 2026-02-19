# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from datetime import datetime
from pydantic import Field
from typing import Any, List, Optional
from typing_extensions import Annotated
from indicate_data_exchange_server.models.aggregation_period_kind import AggregationPeriodKind
from indicate_data_exchange_server.models.attributed_quality_indicator_result import AttributedQualityIndicatorResult
from indicate_data_exchange_server.models.provider_results_post_request import ProviderResultsPostRequest
from indicate_data_exchange_server.models.results_get400_response import ResultsGet400Response


class BaseDefaultApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseDefaultApi.subclasses = BaseDefaultApi.subclasses + (cls,)
    async def results_get(
        self,
        aggregation_kind: Annotated[AggregationPeriodKind, Field(description="This required parameter control from which aggregation kind the returned data is taken. ")],
        period_start: Optional[datetime],
    ) -> List[AttributedQualityIndicatorResult]:
        ...


    async def provider_results_post(
        self,
        provider_results_post_request: ProviderResultsPostRequest,
    ) -> None:
        ...
