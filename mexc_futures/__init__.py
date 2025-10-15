"""
MEXC Futures Python SDK

A Python SDK for MEXC Futures trading with REST API support.
"""

from .client import MexcFuturesClient, MexcFuturesClientSync, MexcFuturesClientConfig
from .types.orders import (
    SubmitOrderRequest,
    SubmitOrderResponse,
    OrderHistoryParams,
    OrderHistoryResponse,
)
from .types.account import (
    AccountAssetResponse,
    OpenPositionsResponse,
)
from .types.market import (
    TickerResponse,
    ContractDetailResponse,
    ContractDepthResponse,
)
from .utils.errors import (
    MexcFuturesError,
    MexcAuthenticationError,
    MexcSignatureError,
    MexcApiError,
    MexcNetworkError,
    MexcValidationError,
    MexcRateLimitError,
)

__version__ = "1.0.0"
__all__ = [
    "MexcFuturesClient",
    "MexcFuturesClientSync", 
    "MexcFuturesClientConfig",
    "SubmitOrderRequest", 
    "SubmitOrderResponse",
    "OrderHistoryParams",
    "OrderHistoryResponse",
    "AccountAssetResponse",
    "OpenPositionsResponse", 
    "TickerResponse",
    "ContractDetailResponse",
    "ContractDepthResponse",
    "MexcFuturesError",
    "MexcAuthenticationError",
    "MexcSignatureError",
    "MexcApiError",
    "MexcNetworkError",
    "MexcValidationError",
    "MexcRateLimitError",
]