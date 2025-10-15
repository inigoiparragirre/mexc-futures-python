"""Main MEXC Futures REST API client."""

import asyncio
from typing import Dict, List, Optional, Union

import httpx
from pydantic import BaseModel, ValidationError

from .types.account import (
    AccountAssetResponse,
    AccountResponse,
    FeeRate,
    OpenPositionsResponse,
    PositionHistoryParams,
    PositionHistoryResponse,
    RiskLimit,
)
from .types.market import (
    ContractDepthResponse,
    ContractDetailResponse,
    TickerResponse,
)
from .types.orders import (
    CancelAllOrdersRequest,
    CancelAllOrdersResponse,
    CancelOrderByExternalIdRequest,
    CancelOrderByExternalIdResponse,
    CancelOrderResponse,
    GetOrderResponse,
    OrderDealsParams,
    OrderDealsResponse,
    OrderHistoryParams,
    OrderHistoryResponse,
    SubmitOrderRequest,
    SubmitOrderResponse,
)
from .utils.constants import API_BASE_URL, ENDPOINTS
from .utils.errors import (
    MexcValidationError,
    format_error_for_logging,
    parse_httpx_error,
)
from .utils.headers import SDKOptions, generate_headers
from .utils.logger import Logger, LogLevelString


class MexcFuturesClientConfig(BaseModel):
    """Configuration for MEXC Futures SDK."""
    auth_token: str  # WEB authentication key (starts with "WEB...")
    base_url: Optional[str] = API_BASE_URL
    timeout: Optional[int] = 30
    user_agent: Optional[str] = None
    custom_headers: Optional[Dict[str, str]] = None
    log_level: Optional[LogLevelString] = "WARN"


class MexcFuturesClient:
    """MEXC Futures SDK for Python."""
    
    def __init__(self, config: Union[MexcFuturesClientConfig, dict]) -> None:
        """
        Initialize MEXC Futures client.
        
        Args:
            config: Configuration object or dictionary
        """
        if isinstance(config, dict):
            self.config = MexcFuturesClientConfig(**config)
        else:
            self.config = config
            
        self.logger = Logger(self.config.log_level)
        
        # Create SDK options for header generation
        self.sdk_options = SDKOptions(
            auth_token=self.config.auth_token,
            user_agent=self.config.user_agent,
            custom_headers=self.config.custom_headers or {},
        )
        
        # Create HTTP client
        self.client = httpx.AsyncClient(
            base_url=self.config.base_url,
            timeout=self.config.timeout,
        )
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()
    
    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        json_data: Optional[Dict] = None,
        require_auth: bool = True,
    ) -> dict:
        """
        Make HTTP request to MEXC API.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            params: Query parameters
            json_data: JSON body data
            require_auth: Whether authentication is required
            
        Returns:
            Response data as dictionary
        """
        try:
            # Generate headers
            headers = generate_headers(
                self.sdk_options,
                include_auth=require_auth,
                request_body=json_data,
            )
            
            self.logger.debug(f"🌐 {method.upper()} {self.config.base_url}{endpoint}")
            if json_data:
                self.logger.debug(f"📦 Request body: {json_data}")
            
            # Make request
            response = await self.client.request(
                method=method,
                url=endpoint,
                params=params,
                json=json_data,
                headers=headers,
            )
            
            self.logger.debug(f"✅ {response.status_code} {response.reason_phrase}")
            
            # Raise for HTTP errors
            response.raise_for_status()
            
            # Parse JSON response
            return response.json()
            
        except Exception as error:
            # Parse error and log user-friendly message
            mexc_error = parse_httpx_error(error, endpoint, method.upper())
            self.logger.error(mexc_error.get_user_friendly_message())
            
            # Log detailed error in debug mode
            if self.logger.is_debug_enabled():
                self.logger.debug("Detailed error info:", format_error_for_logging(mexc_error))
            
            raise mexc_error
    
    # ==================== ORDER METHODS ====================
    
    async def submit_order(self, order_params: Union[SubmitOrderRequest, dict]) -> SubmitOrderResponse:
        """
        Submit order using /api/v1/private/order/submit endpoint.
        
        Args:
            order_params: Order parameters
            
        Returns:
            Submit order response
        """
        if isinstance(order_params, dict):
            try:
                order_params = SubmitOrderRequest(**order_params)
            except ValidationError as e:
                raise MexcValidationError(f"Invalid order parameters: {e}")
        
        self.logger.info("🚀 Submitting order using /submit endpoint")
        self.logger.debug(f"📦 Order parameters: {order_params.model_dump()}")
        
        response_data = await self._request(
            method="POST",
            endpoint=ENDPOINTS.SUBMIT_ORDER,
            json_data=order_params.model_dump(),
            require_auth=True,
        )
        
        self.logger.debug(f"🔍 Order response: {response_data}")
        return SubmitOrderResponse(**response_data)
    
    async def cancel_order(self, order_ids: List[int]) -> CancelOrderResponse:
        """
        Cancel orders by order IDs (up to 50 orders at once).
        
        Args:
            order_ids: List of order IDs to cancel
            
        Returns:
            Cancel order response
        """
        if not order_ids:
            raise MexcValidationError("Order IDs list cannot be empty", "order_ids")
        if len(order_ids) > 50:
            raise MexcValidationError("Cannot cancel more than 50 orders at once", "order_ids")
        
        response_data = await self._request(
            method="POST",
            endpoint=ENDPOINTS.CANCEL_ORDER,
            json_data=order_ids,
            require_auth=True,
        )
        
        self.logger.debug(f"🔍 Cancel order response: {response_data}")
        return CancelOrderResponse(**response_data)
    
    async def cancel_order_by_external_id(
        self, params: Union[CancelOrderByExternalIdRequest, dict]
    ) -> CancelOrderByExternalIdResponse:
        """
        Cancel order by external order ID.
        
        Args:
            params: Cancel parameters with symbol and external order ID
            
        Returns:
            Cancel order response
        """
        if isinstance(params, dict):
            params = CancelOrderByExternalIdRequest(**params)
        
        response_data = await self._request(
            method="POST",
            endpoint=ENDPOINTS.CANCEL_ORDER_BY_EXTERNAL_ID,
            json_data=params.model_dump(),
            require_auth=True,
        )
        
        self.logger.debug(f"🔍 Cancel order by external ID response: {response_data}")
        return CancelOrderByExternalIdResponse(**response_data)
    
    async def cancel_all_orders(
        self, params: Optional[Union[CancelAllOrdersRequest, dict]] = None
    ) -> CancelAllOrdersResponse:
        """
        Cancel all orders under a contract (or all orders if no symbol provided).
        
        Args:
            params: Optional parameters with symbol filter
            
        Returns:
            Cancel all orders response
        """
        if params is None:
            params = CancelAllOrdersRequest()
        elif isinstance(params, dict):
            params = CancelAllOrdersRequest(**params)
        
        response_data = await self._request(
            method="POST",
            endpoint=ENDPOINTS.CANCEL_ALL_ORDERS,
            json_data=params.model_dump(),
            require_auth=True,
        )
        
        return CancelAllOrdersResponse(**response_data)
    
    async def get_order_history(
        self, params: Union[OrderHistoryParams, dict]
    ) -> OrderHistoryResponse:
        """
        Get order history.
        
        Args:
            params: Order history query parameters
            
        Returns:
            Order history response
        """
        if isinstance(params, dict):
            params = OrderHistoryParams(**params)
        
        response_data = await self._request(
            method="GET",
            endpoint=ENDPOINTS.ORDER_HISTORY,
            params=params.model_dump(),
            require_auth=True,
        )
        
        return OrderHistoryResponse(**response_data)
    
    async def get_order_deals(
        self, params: Union[OrderDealsParams, dict]
    ) -> OrderDealsResponse:
        """
        Get all transaction details of the user's orders.
        
        Args:
            params: Order deals query parameters
            
        Returns:
            Order deals response
        """
        if isinstance(params, dict):
            params = OrderDealsParams(**params)
        
        response_data = await self._request(
            method="GET",
            endpoint=ENDPOINTS.ORDER_DEALS,
            params=params.model_dump(),
            require_auth=True,
        )
        
        return OrderDealsResponse(**response_data)
    
    async def get_order(self, order_id: Union[int, str]) -> GetOrderResponse:
        """
        Get order information by order ID.
        
        Args:
            order_id: Order ID to query
            
        Returns:
            Detailed order information
        """
        response_data = await self._request(
            method="GET",
            endpoint=f"{ENDPOINTS.GET_ORDER}/{order_id}",
            require_auth=True,
        )
        
        self.logger.debug(f"🔍 Order response: {response_data}")
        return GetOrderResponse(**response_data)
    
    async def get_order_by_external_id(
        self, symbol: str, external_oid: str
    ) -> GetOrderResponse:
        """
        Get order information by external order ID.
        
        Args:
            symbol: Contract symbol (e.g., "BTC_USDT")
            external_oid: External order ID
            
        Returns:
            Detailed order information
        """
        response_data = await self._request(
            method="GET",
            endpoint=f"{ENDPOINTS.GET_ORDER_BY_EXTERNAL_ID}/{symbol}/{external_oid}",
            require_auth=True,
        )
        
        return GetOrderResponse(**response_data)
    
    # ==================== ACCOUNT METHODS ====================
    
    async def get_risk_limit(self) -> AccountResponse[Dict[str, List[RiskLimit]]]:
        """
        Get risk limits for account.
        
        Returns:
            Risk limit information organized by symbol
        """
        response_data = await self._request(
            method="GET",
            endpoint=ENDPOINTS.RISK_LIMIT,
            require_auth=True,
        )
        
        return AccountResponse[Dict[str, List[RiskLimit]]](**response_data)
    
    async def get_fee_rate(self) -> AccountResponse[List[FeeRate]]:
        """
        Get fee rates for contracts.
        
        Returns:
            Fee rate information
        """
        response_data = await self._request(
            method="GET",
            endpoint=ENDPOINTS.FEE_RATE,
            require_auth=True,
        )
        
        return AccountResponse[List[FeeRate]](**response_data)
    
    async def get_account_asset(self, currency: str) -> AccountAssetResponse:
        """
        Get user's single currency asset information.
        
        Args:
            currency: Currency symbol (e.g., "USDT", "BTC")
            
        Returns:
            Account asset information for the specified currency
        """
        response_data = await self._request(
            method="GET",
            endpoint=f"{ENDPOINTS.ACCOUNT_ASSET}/{currency}",
            require_auth=True,
        )
        
        return AccountAssetResponse(**response_data)
    
    async def get_open_positions(self, symbol: Optional[str] = None) -> OpenPositionsResponse:
        """
        Get user's current holding positions.
        
        Args:
            symbol: Optional specific contract symbol to filter positions
            
        Returns:
            List of open positions
        """
        params = {"symbol": symbol} if symbol else None
        
        response_data = await self._request(
            method="GET",
            endpoint=ENDPOINTS.OPEN_POSITIONS,
            params=params,
            require_auth=True,
        )
        
        return OpenPositionsResponse(**response_data)
    
    async def get_position_history(
        self, params: Union[PositionHistoryParams, dict]
    ) -> PositionHistoryResponse:
        """
        Get user's history position information.
        
        Args:
            params: Parameters for filtering position history
            
        Returns:
            List of historical positions
        """
        if isinstance(params, dict):
            params = PositionHistoryParams(**params)
        
        response_data = await self._request(
            method="GET",
            endpoint=ENDPOINTS.POSITION_HISTORY,
            params=params.model_dump(),
            require_auth=True,
        )
        
        return PositionHistoryResponse(**response_data)
    
    # ==================== MARKET DATA METHODS ====================
    
    async def get_ticker(self, symbol: str) -> TickerResponse:
        """
        Get ticker data for a specific symbol.
        
        Args:
            symbol: Contract symbol (e.g., "BTC_USDT")
            
        Returns:
            Ticker data response
        """
        response_data = await self._request(
            method="GET",
            endpoint=ENDPOINTS.TICKER,
            params={"symbol": symbol},
            require_auth=False,
        )
        
        return TickerResponse(**response_data)
    
    async def get_contract_detail(self, symbol: Optional[str] = None) -> ContractDetailResponse:
        """
        Get contract information.
        
        Args:
            symbol: Optional specific contract symbol. If not provided, returns all contracts
            
        Returns:
            Contract details for specified symbol or all contracts
        """
        params = {"symbol": symbol} if symbol else None
        
        response_data = await self._request(
            method="GET",
            endpoint=ENDPOINTS.CONTRACT_DETAIL,
            params=params,
            require_auth=False,
        )
        
        return ContractDetailResponse(**response_data)
    
    async def get_contract_depth(
        self, symbol: str, limit: Optional[int] = None
    ) -> ContractDepthResponse:
        """
        Get contract's depth information (order book).
        
        Args:
            symbol: Contract symbol (e.g., "BTC_USDT")
            limit: Optional depth tier limit
            
        Returns:
            Order book with bids and asks
        """
        params = {"limit": limit} if limit else None
        
        response_data = await self._request(
            method="GET",
            endpoint=f"{ENDPOINTS.CONTRACT_DEPTH}/{symbol}",
            params=params,
            require_auth=False,
        )
        
        return ContractDepthResponse(**response_data)
    
    # ==================== UTILITY METHODS ====================
    
    async def test_connection(self) -> bool:
        """
        Test connection to the API (using public endpoint).
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            await self.get_ticker("BTC_USDT")
            return True
        except Exception:
            return False


# Synchronous wrapper class
class MexcFuturesClientSync:
    """Synchronous wrapper for MexcFuturesClient."""
    
    def __init__(self, config: Union[MexcFuturesClientConfig, dict]) -> None:
        """Initialize synchronous client."""
        self.async_client = MexcFuturesClient(config)
    
    def _run_async(self, coro):
        """Run async coroutine synchronously."""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(coro)
    
    def close(self) -> None:
        """Close the client."""
        self._run_async(self.async_client.close())
    
    def submit_order(self, order_params: Union[SubmitOrderRequest, dict]) -> SubmitOrderResponse:
        """Submit order synchronously."""
        return self._run_async(self.async_client.submit_order(order_params))
    
    def cancel_order(self, order_ids: List[int]) -> CancelOrderResponse:
        """Cancel orders synchronously."""
        return self._run_async(self.async_client.cancel_order(order_ids))
    
    def get_ticker(self, symbol: str) -> TickerResponse:
        """Get ticker synchronously."""
        return self._run_async(self.async_client.get_ticker(symbol))
    
    def get_account_asset(self, currency: str) -> AccountAssetResponse:
        """Get account asset synchronously."""
        return self._run_async(self.async_client.get_account_asset(currency))
    
    def get_open_positions(self, symbol: Optional[str] = None) -> OpenPositionsResponse:
        """Get open positions synchronously."""
        return self._run_async(self.async_client.get_open_positions(symbol))
    
    def test_connection(self) -> bool:
        """Test connection synchronously."""
        return self._run_async(self.async_client.test_connection())