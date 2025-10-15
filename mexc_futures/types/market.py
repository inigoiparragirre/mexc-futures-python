"""Market data type definitions."""

from typing import List, Optional, Union

from pydantic import BaseModel, field_validator, model_validator


class RiseFallRates(BaseModel):
    """Rise/fall rate information."""
    zone: str
    r: float  # current rate
    v: float  # current value
    r7: float  # 7 days rate
    r30: Optional[float] = None  # 30 days rate
    r90: Optional[float] = None  # 90 days rate
    r180: Optional[float] = None  # 180 days rate
    r365: Optional[float] = None  # 365 days rate


class TickerData(BaseModel):
    """Ticker data information."""
    contractId: int
    symbol: str
    lastPrice: float
    bid1: float
    ask1: float
    volume24: float  # 24h volume
    amount24: float  # 24h amount
    holdVol: float  # open interest
    lower24Price: float  # 24h low
    high24Price: float  # 24h high
    riseFallRate: float  # price change rate
    riseFallValue: float  # price change value
    indexPrice: float
    fairPrice: float
    fundingRate: float
    maxBidPrice: float
    minAskPrice: float
    timestamp: int
    riseFallRates: RiseFallRates
    riseFallRatesOfTimezone: List[float]


class TickerResponse(BaseModel):
    """Response for ticker query."""
    success: bool
    code: int
    data: TickerData


class ContractDetail(BaseModel):
    """Contract detail information."""
    symbol: str
    displayName: str
    displayNameEn: str
    positionOpenType: int  # 1: isolated, 2: cross, 3: both
    baseCoin: str
    quoteCoin: str
    settleCoin: str
    contractSize: float
    minLeverage: int
    maxLeverage: int
    priceScale: int
    volScale: int
    amountScale: int
    priceUnit: float
    volUnit: float
    minVol: float
    maxVol: float
    bidLimitPriceRate: float
    askLimitPriceRate: float
    takerFeeRate: float
    makerFeeRate: float
    maintenanceMarginRate: float
    initialMarginRate: float
    riskBaseVol: float
    riskIncrVol: float
    riskIncrMmr: float
    riskIncrImr: float
    riskLevelLimit: int
    priceCoefficientVariation: float
    indexOrigin: List[str]
    state: int  # 0: enabled, 1: delivery, 2: completed, 3: offline, 4: pause
    isNew: bool
    isHot: bool
    isHidden: bool
    conceptPlate: List[str]
    riskLimitType: str  # "BY_VOLUME" or "BY_VALUE"
    maxNumOrders: List[int]
    marketOrderMaxLevel: int
    marketOrderPriceLimitRate1: float
    marketOrderPriceLimitRate2: float
    triggerProtect: float
    appraisal: float
    showAppraisalCountdown: int
    automaticDelivery: int
    apiAllowed: bool


class ContractDetailResponse(BaseModel):
    """Response for contract detail query."""
    success: bool
    code: int
    data: Union[ContractDetail, List[ContractDetail]]  # Can be single object or array


class DepthEntry(BaseModel):
    """Order book depth entry [price, volume, count?]."""
    price: float
    volume: float
    count: Optional[int] = None
    
    @classmethod
    def __get_validators__(cls):
        # For pydantic v1 compatibility
        yield cls.validate
    
    @classmethod
    def validate(cls, value):
        """Validate and convert array format to DepthEntry."""
        if isinstance(value, (list, tuple)) and len(value) >= 2:
            # Handle array format [price, volume, count?]
            return cls(
                price=float(value[0]),
                volume=float(value[1]),
                count=int(value[2]) if len(value) > 2 else None
            )
        elif isinstance(value, dict):
            return cls(**value)
        elif isinstance(value, cls):
            return value
        else:
            raise ValueError(f"Cannot convert {type(value)} to DepthEntry")


class ContractDepthData(BaseModel):
    """Contract depth data."""
    asks: List[DepthEntry]  # seller depth (ascending price)
    bids: List[DepthEntry]  # buyer depth (descending price)
    version: int  # version number
    timestamp: int  # system timestamp
    
    @field_validator('asks', 'bids', mode='before')
    @classmethod
    def validate_depth_entries(cls, v):
        """Convert array format to DepthEntry objects."""
        if isinstance(v, list):
            return [DepthEntry.validate(entry) for entry in v]
        return v


class ContractDepthResponse(BaseModel):
    """Response for contract depth query."""
    success: Optional[bool] = None  # Note: this endpoint may not return success/code fields
    code: Optional[int] = None
    data: Optional[ContractDepthData] = None
    asks: Optional[List[DepthEntry]] = None  # Direct response format
    bids: Optional[List[DepthEntry]] = None
    version: Optional[int] = None
    timestamp: Optional[int] = None
    
    @field_validator('asks', 'bids', mode='before')
    @classmethod
    def validate_depth_entries(cls, v):
        """Convert array format to DepthEntry objects."""
        if isinstance(v, list):
            return [DepthEntry.validate(entry) for entry in v]
        return v