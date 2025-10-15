"""Account-related type definitions."""

from typing import Dict, Generic, List, Literal, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar('T')


class RiskLimit(BaseModel):
    """Risk limit information."""
    symbol: str
    level: int
    maxVol: float  # maximum volume
    mmr: float  # maintenance margin rate
    imr: float  # initial margin rate
    maxLeverage: int
    positionType: int  # 1 = long, 2 = short
    openType: int  # 1 = isolated, 2 = cross
    leverage: int
    limitBySys: bool
    currentMmr: Optional[float] = None  # current maintenance margin rate (optional)


class FeeRate(BaseModel):
    """Fee rate information."""
    symbol: str
    takerFeeRate: float
    makerFeeRate: float


class AccountResponse(BaseModel, Generic[T]):
    """Generic account response wrapper."""
    success: bool
    code: int
    data: T


class AccountAsset(BaseModel):
    """Account asset information."""
    currency: str
    positionMargin: float
    availableBalance: float
    cashBalance: float
    frozenBalance: float
    equity: float
    unrealized: float
    bonus: float


class AccountAssetResponse(BaseModel):
    """Response for account asset query."""
    success: bool
    code: int
    data: AccountAsset


class Position(BaseModel):
    """Position information."""
    positionId: int
    symbol: str
    positionType: Literal[1, 2]  # 1 = long, 2 = short
    openType: Literal[1, 2]  # 1 = isolated, 2 = cross
    state: Literal[1, 2, 3]  # 1 = holding, 2 = system auto-holding, 3 = closed
    holdVol: float  # holding volume
    frozenVol: float  # frozen volume
    closeVol: float  # close volume
    holdAvgPrice: float  # holdings average price
    openAvgPrice: float  # open average price
    closeAvgPrice: float  # close average price
    liquidatePrice: float  # liquidate price
    oim: float  # original initial margin
    adlLevel: Optional[int] = None  # ADL level 1-5, may be empty
    im: float  # initial margin
    holdFee: float  # holding fee (positive = received, negative = paid)
    realised: float  # realized profit and loss
    leverage: int  # leverage
    createTime: int  # create timestamp
    updateTime: int  # update timestamp
    autoAddIm: Optional[bool] = None  # auto add initial margin


class OpenPositionsResponse(BaseModel):
    """Response for open positions query."""
    success: bool
    code: int
    data: List[Position]


class PositionHistoryParams(BaseModel):
    """Parameters for position history query."""
    symbol: Optional[str] = None  # Optional: the name of the contract
    type: Optional[Literal[1, 2]] = None  # Optional: position type, 1=long, 2=short
    page_num: int  # Required: current page number, default is 1
    page_size: int  # Required: page size, default 20, maximum 100


class PositionHistoryResponse(BaseModel):
    """Response for position history query."""
    success: bool
    code: int
    message: str
    data: List[Position]