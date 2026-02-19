# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from indicate_data_exchange_server.apis.default_api_base import BaseDefaultApi
import indicate_data_exchange_server.impl

from fastapi import (  # noqa: F401
    APIRouter,
    Body,
    Cookie,
    Depends,
    Form,
    Header,
    HTTPException,
    Path,
    Query,
    Response,
    Security,
    status,
)

from indicate_data_exchange_server.models.extra_models import TokenModel  # noqa: F401
from datetime import datetime
from pydantic import Field
from typing import Any, List, Optional
from typing_extensions import Annotated
from indicate_data_exchange_server.models.aggregation_period_kind import AggregationPeriodKind
from indicate_data_exchange_server.models.attributed_quality_indicator_result import AttributedQualityIndicatorResult
from indicate_data_exchange_server.models.indicator_info import IndicatorInfo
from indicate_data_exchange_server.models.indicator_info_get400_response import IndicatorInfoGet400Response
from indicate_data_exchange_server.models.provider_results_post_request import ProviderResultsPostRequest


router = APIRouter()

ns_pkg = indicate_data_exchange_server.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.get(
    "/indicator-info",
    responses={
        200: {"model": List[IndicatorInfo], "description": "Return to valid query which contains a of information elements for all defined indicators. "},
        400: {"model": IndicatorInfoGet400Response, "description": "Bad Request - Invalid data or missing required fields "},
        500: {"model": IndicatorInfoGet400Response, "description": "Internal Server Error - Unexpected error "},
    },
    tags=["default"],
    summary="Retrieve information such as OMOP Concept ID and a textual description about all defined quality indicators. ",
    response_model_by_alias=True,
)
async def indicator_info_get(
) -> List[IndicatorInfo]:
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().indicator_info_get()


@router.get(
    "/results",
    responses={
        200: {"model": List[AttributedQualityIndicatorResult], "description": "Response to valid query which contains the aggregated quality indicator results for the requested aggregation kind and time period. "},
        400: {"model": IndicatorInfoGet400Response, "description": "Bad Request - Invalid data or missing required fields "},
        500: {"model": IndicatorInfoGet400Response, "description": "Internal Server Error - Unexpected error "},
    },
    tags=["default"],
    summary="Retrieve aggregated quality indicator results without identifying information except pseudonymous data providers ids.  A data provider should be able to recognize the data it uploaded earlier based on the provider id.  The request must specify an aggregation kind and only results aggregated according to the selected aggregation kind will be returned.  The request can be restricted to a certain time period but the corresponding parameters are optional. If they are not supplied, all data is returned. ",
    response_model_by_alias=True,
)
async def results_get(
    aggregation_kind: Annotated[AggregationPeriodKind, Field(description="This required parameter control from which aggregation kind the returned data is taken. ")] = Query(None, description="This required parameter control from which aggregation kind the returned data is taken. ", alias="aggregation_kind"),
    period_start: Optional[datetime] = Query(None, description="", alias="period_start"),
    period_end: Optional[datetime] = Query(None, description="", alias="period_end"),
) -> List[AttributedQualityIndicatorResult]:
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().results_get(aggregation_kind, period_start, period_end)


@router.post(
    "/provider-results",
    responses={
        200: {"description": "Successfully uploaded data"},
        400: {"model": IndicatorInfoGet400Response, "description": "Bad Request - Invalid data or missing required fields "},
        500: {"model": IndicatorInfoGet400Response, "description": "Internal Server Error - Unexpected error "},
    },
    tags=["default"],
    summary="Upload aggregated quality indicator results from one data provider to the hub.  Each invocation of this operation uploads the entirety of the aggregated indicator result data that the data provider has produced so far. The intention is that the hub replaces all data for that data provider with each invocation of this operation. ",
    response_model_by_alias=True,
)
async def provider_results_post(
    provider_results_post_request: ProviderResultsPostRequest = Body(None, description=""),
) -> None:
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().provider_results_post(provider_results_post_request)
