# MEXC Futures Python SDK

A Python SDK for MEXC Futures trading with REST API support.

⚠️ **DISCLAIMER**: This SDK uses browser session tokens and reverse-engineered endpoints. MEXC does not officially support futures trading through API. Use at your own risk.

## Features

- ✅ **REST API** - Complete trading functionality
- ✅ **Async/Await** - Full asynchronous support with httpx
- ✅ **Type Safety** - Pydantic models for all API responses
- ✅ **Error Handling** - Comprehensive error management
- ✅ **Synchronous Support** - Optional sync wrapper for simple use cases

## Installation

```bash
# Install from PyPI (when published)
pip install mexc-futures-python

# Or install from source
git clone https://github.com/oboshto/mexc-futures-python.git
cd mexc-futures-python
pip install -e .
```

## Dependencies

- `httpx>=0.24.0` - Modern async HTTP client
- `pydantic>=2.0.0` - Data validation and serialization
- `typing-extensions>=4.0.0` - Type hints support

## Quick Start

### Async Usage (Recommended)

```python
import asyncio
from mexc_futures import MexcFuturesClient

async def main():
    client = MexcFuturesClient({
        "auth_token": "WEB_YOUR_TOKEN_HERE",  # Get from browser Developer Tools
        "log_level": "INFO"
    })
    
    try:
        # Get ticker data
        ticker = await client.get_ticker("BTC_USDT")
        print(f"BTC Price: ${ticker.data.lastPrice}")
        
        # Place a market order
        order = await client.submit_order({
            "symbol": "BTC_USDT",
            "price": 50000,
            "vol": 0.001,
            "side": 1,  # 1=open long, 3=open short
            "type": 5,  # 5=market order
            "openType": 1,  # 1=isolated margin
            "leverage": 10,
        })
        print(f"Order ID: {order.data}")
        
    finally:
        await client.close()

# Run the async function
asyncio.run(main())
```

### Synchronous Usage

```python
from mexc_futures import MexcFuturesClientSync

client = MexcFuturesClientSync({
    "auth_token": "WEB_YOUR_TOKEN_HERE",
    "log_level": "INFO"
})

try:
    # Get ticker data
    ticker = client.get_ticker("BTC_USDT")
    print(f"BTC Price: ${ticker.data.lastPrice}")
    
    # Get account balance
    balance = client.get_account_asset("USDT")
    print(f"USDT Balance: {balance.data.availableBalance}")
    
finally:
    client.close()
```

### Configuration Options

```python
from mexc_futures import MexcFuturesClient, MexcFuturesClientConfig

config = MexcFuturesClientConfig(
    auth_token="WEB_YOUR_TOKEN_HERE",
    base_url="https://futures.mexc.com/api/v1",  # Optional: custom base URL
    timeout=30,  # Optional: request timeout in seconds
    user_agent="Custom User Agent",  # Optional: custom user agent
    custom_headers={"Custom-Header": "value"},  # Optional: additional headers
    log_level="DEBUG"  # Optional: SILENT, ERROR, WARN, INFO, DEBUG
)

client = MexcFuturesClient(config)
```

## Authentication

### Browser Session Token

1. Login to MEXC futures in your browser
2. Open Developer Tools (F12) → Network tab  
3. Make any request to futures.mexc.com
4. Find the `authorization` header (starts with "WEB...")
5. Copy the token value

## API Methods

### Order Management

```python
# Submit order
order = await client.submit_order({
    "symbol": "BTC_USDT",
    "price": 50000,
    "vol": 0.001,
    "side": 1,  # 1=open long, 2=close short, 3=open short, 4=close long
    "type": 5,  # 1=limit, 2=Post Only, 3=IOC, 4=FOK, 5=market, 6=convert
    "openType": 1,  # 1=isolated margin, 2=cross margin
    "leverage": 10
})

# Cancel orders
await client.cancel_order([12345, 67890])  # List of order IDs

# Cancel all orders
await client.cancel_all_orders({"symbol": "BTC_USDT"})  # Optional symbol filter

# Get order history
history = await client.get_order_history({
    "category": 1,
    "page_num": 1,
    "page_size": 20,
    "states": 3,  # Order state filter
    "symbol": "BTC_USDT"
})

# Get specific order
order_info = await client.get_order(12345)
```

### Account Information

```python
# Get account asset
asset = await client.get_account_asset("USDT")
print(f"Available: {asset.data.availableBalance}")
print(f"Total Equity: {asset.data.equity}")

# Get open positions
positions = await client.get_open_positions()
for position in positions.data:
    side = "LONG" if position.positionType == 1 else "SHORT"
    print(f"{position.symbol} {side}: {position.holdVol}")

# Get risk limits
risk_limits = await client.get_risk_limit()

# Get fee rates
fee_rates = await client.get_fee_rate()
```

### Market Data

```python
# Get ticker
ticker = await client.get_ticker("BTC_USDT")
print(f"Price: ${ticker.data.lastPrice}")
print(f"24h Volume: {ticker.data.volume24}")

# Get contract details
contract = await client.get_contract_detail("BTC_USDT")
print(f"Max Leverage: {contract.data.maxLeverage}x")

# Get order book
depth = await client.get_contract_depth("BTC_USDT", limit=10)
print(f"Best Bid: ${depth.bids[0].price}")
print(f"Best Ask: ${depth.asks[0].price}")
```

## Order Parameters

### Mandatory Parameters

- **symbol**: Contract name (e.g., "BTC_USDT")
- **price**: Order price (required for ALL order types, including market)
- **vol**: Order volume
- **side**: Order direction
  - `1` = Open long position
  - `2` = Close short position  
  - `3` = Open short position
  - `4` = Close long position
- **type**: Order type
  - `1` = Limit order
  - `2` = Post Only Maker
  - `3` = IOC (Immediate or Cancel)
  - `4` = FOK (Fill or Kill)
  - `5` = Market order
  - `6` = Convert market price
- **openType**: Margin type
  - `1` = Isolated margin
  - `2` = Cross margin

### Optional Parameters

- **leverage**: Required for isolated margin (openType: 1)
- **positionId**: Recommended when closing a position
- **externalOid**: External order ID for tracking
- **stopLossPrice**: Stop-loss price
- **takeProfitPrice**: Take-profit price
- **positionMode**: Position mode (1=hedge, 2=one-way)
- **reduceOnly**: For one-way positions only (boolean)

## Error Handling

The SDK provides comprehensive error handling with user-friendly messages:

```python
from mexc_futures.utils.errors import (
    MexcAuthenticationError,
    MexcApiError,
    MexcNetworkError,
    MexcRateLimitError,
    MexcValidationError
)

try:
    ticker = await client.get_ticker("BTC_USDT")
except MexcAuthenticationError as e:
    print("❌ Authentication failed. Please update your WEB token.")
except MexcRateLimitError as e:
    print(f"❌ Rate limit exceeded. Retry after {e.retry_after} seconds.")
except MexcNetworkError as e:
    print("❌ Network error. Check your internet connection.")
except MexcApiError as e:
    print(f"❌ API error ({e.status_code}): {e}")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
```

## Examples

See the `examples/` directory for complete working examples:

- `basic_example.py` - Basic API usage and market data
- More examples coming soon...

```bash
# Run the basic example
python examples/basic_example.py
```

## Development

```bash
# Clone repository
git clone https://github.com/oboshto/mexc-futures-python.git
cd mexc-futures-python

# Install in development mode
pip install -e .

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black mexc_futures/
isort mexc_futures/

# Type checking
mypy mexc_futures/
```

## Logging

The SDK supports configurable logging levels:

```python
client = MexcFuturesClient({
    "auth_token": "WEB_YOUR_TOKEN",
    "log_level": "DEBUG"  # SILENT, ERROR, WARN, INFO, DEBUG
})
```

- `ERROR`: Only error messages
- `INFO`: User-friendly informational messages  
- `DEBUG`: Detailed debugging information

## Comparison with TypeScript Version

This Python SDK provides feature parity with the original TypeScript version:

| Feature | TypeScript | Python |
|---------|------------|--------|
| REST API | ✅ | ✅ |
| WebSocket | ✅ | 🚧 Coming soon |
| Type Safety | ✅ | ✅ (Pydantic) |
| Async/Await | ✅ | ✅ |
| Error Handling | ✅ | ✅ |
| Authentication | ✅ | ✅ |

## Roadmap

- [ ] WebSocket client implementation
- [ ] More comprehensive examples
- [ ] Integration tests
- [ ] Performance optimizations
- [ ] Documentation improvements

## Support

This is an unofficial SDK. Use at your own risk. For issues and feature requests, please open a GitHub issue.

## License

MIT License - see LICENSE file for details.

## Disclaimer

This SDK is not affiliated with MEXC. It uses reverse-engineered browser endpoints and may break if MEXC changes their API. Always test with small amounts first.