"""Order-related type definitions."""

from typing import List, Literal, Optional, Union

from pydantic import BaseModel, field_validator


class OrderHistoryParams(BaseModel):
    """Parameters for order history query."""
    category: int
    page_num: int
    page_size: int
    states: int
    symbol: str


class Order(BaseModel):
    """Order information."""
    id: str
    symbol: str
    side: int
    type: str
    vol: float
    price: str
    leverage: int
    status: str
    createTime: int
    updateTime: int


class OrderHistoryData(BaseModel):
    """Order history data wrapper."""
    orders: List[Order]
    total: int


class OrderHistoryResponse(BaseModel):
    """Response for order history query."""
    success: bool
    code: int
    data: Optional[OrderHistoryData] = None
    
    @field_validator('data', mode='before')
    @classmethod
    def validate_data(cls, v):
        """Handle the case where data is an empty list instead of OrderHistoryData."""
        if v == []:
            return OrderHistoryData(orders=[], total=0)
        return v


class OrderDealsParams(BaseModel):
    """Parameters for order deals query."""
    symbol: str
    start_time: Optional[int] = None  # timestamp in milliseconds
    end_time: Optional[int] = None    # timestamp in milliseconds
    page_num: int
    page_size: int


class OrderDeal(BaseModel):
    """Order deal (transaction) information."""
    id: int
    symbol: str
    side: int  # 1 open long, 2 close short, 3 open short, 4 close long
    vol: str  # transaction volume
    price: str  # transaction price
    fee: str  # fee amount
    feeCurrency: str  # fee currency
    profit: str  # profit
    isTaker: bool  # is taker order
    category: int  # 1 limit order, 2 system take-over delegate, 3 close delegate, 4 ADL reduction
    orderId: int  # order id
    timestamp: int  # transaction timestamp


class OrderDealsResponse(BaseModel):
    """Response for order deals query."""
    success: bool
    code: int
    data: List[OrderDeal]


class CancelOrderResult(BaseModel):
    """Result of canceling a single order."""
    orderId: int
    errorCode: int  # 0 means success, non-zero means failure
    errorMsg: str


class CancelOrderResponse(BaseModel):
    """Response for cancel order request."""
    success: bool
    code: int
    data: List[CancelOrderResult]


class CancelOrderByExternalIdRequest(BaseModel):
    """Request to cancel order by external ID."""
    symbol: str
    externalOid: str


class CancelOrderByExternalIdData(BaseModel):
    """Data in cancel by external ID response."""
    symbol: str
    externalOid: str


class CancelOrderByExternalIdResponse(BaseModel):
    """Response for cancel order by external ID."""
    success: bool
    code: int
    data: Optional[CancelOrderByExternalIdData] = None


class CancelAllOrdersRequest(BaseModel):
    """Request to cancel all orders."""
    symbol: Optional[str] = None  # optional: cancel specific symbol orders


class CancelAllOrdersResponse(BaseModel):
    """Response for cancel all orders."""
    success: bool
    code: int
    data: Optional[dict] = None


class SubmitOrderRequest(BaseModel):
    """Request to submit an order."""
    symbol: str  # the name of the contract (mandatory)
    price: float  # price (mandatory)
    vol: float  # volume (mandatory)
    leverage: Optional[int] = None  # leverage, necessary on Isolated Margin
    side: Literal[1, 2, 3, 4]  # order direction: 1=open long, 2=close short, 3=open short, 4=close long
    type: Literal[1, 2, 3, 4, 5, 6]  # order type: 1=limit, 2=Post Only, 3=IOC, 4=FOK, 5=market, 6=convert
    openType: Literal[1, 2]  # open type: 1=isolated, 2=cross (mandatory)
    positionId: Optional[int] = None  # position ID, recommended when closing
    externalOid: Optional[str] = None  # external order ID
    stopLossPrice: Optional[float] = None  # stop-loss price
    takeProfitPrice: Optional[float] = None  # take-profit price
    positionMode: Optional[Literal[1, 2]] = None  # position mode: 1=hedge, 2=one-way
    reduceOnly: Optional[bool] = None  # for one-way positions only


class SubmitOrderResponse(BaseModel):
    """Response for submit order request."""
    success: bool
    code: int
    message: Optional[str] = None
    data: Optional[int] = None  # Order ID is returned directly as a number


class GetOrderData(BaseModel):
    """Detailed order information."""
    orderId: str
    symbol: str
    positionId: int
    price: float
    vol: float
    leverage: int
    side: int  # 1 open long, 2 close short, 3 open short, 4 close long
    category: int  # 1 limit order, 2 system take-over delegate, 3 close delegate, 4 ADL reduction
    orderType: int  # 1:limit, 2:Post Only, 3:IOC, 4:FOK, 5:market, 6:convert
    dealAvgPrice: float
    dealVol: float
    orderMargin: float
    takerFee: float
    makerFee: float
    profit: float
    feeCurrency: str
    openType: int  # 1 isolated, 2 cross
    state: int  # 1 uninformed, 2 uncompleted, 3 completed, 4 cancelled, 5 invalid
    externalOid: str
    errorCode: int
    usedMargin: float
    createTime: int
    updateTime: int


class GetOrderResponse(BaseModel):
    """Response for get order request."""
    success: bool
    code: int
    data: GetOrderData