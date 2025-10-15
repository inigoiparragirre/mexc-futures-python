"""Basic example demonstrating MEXC Futures Python SDK usage."""

import sys
import os
import asyncio
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from mexc_futures import MexcFuturesClient


async def main():
    """Main async function."""
    # Get token from environment variable
    auth_token = os.getenv('WEB_TOKEN')
    
    if not auth_token:
        print("❌ Error: WEB_TOKEN not found in environment variables.")
        print("💡 Please set WEB_TOKEN in your .env file or environment.")
        return
    
    client = MexcFuturesClient({
        "auth_token": auth_token,
        "timeout": 15,  # Optional: request timeout in seconds
        "log_level": "INFO",  # Optional: logging level
    })

    try:
        # Test connection
        print("🔌 Testing connection...")
        is_connected = await client.test_connection()
        print(f"Connection: {'✅ SUCCESS' if is_connected else '❌ FAILED'}")

        if not is_connected:
            print("❌ Connection failed. Check your WEB token.")
            return

        # Get market data
        print("\n📈 Fetching market data...")

        symbols = ["BTC_USDT", "CAKE_USDT"]
        for symbol in symbols:
            try:
                print(f"\n🔍 {symbol}:")
                ticker = await client.get_ticker(symbol)

                print(f"  💰 Price: ${ticker.data.lastPrice}")
                print(f"  📈 24h Change: {(ticker.data.riseFallRate * 100):.2f}%")
                print(f"  📊 24h Volume: {ticker.data.volume24:,.0f}")
                print(f"  🏦 Open Interest: {ticker.data.holdVol:,.0f}")
                print(f"  💸 Funding Rate: {ticker.data.fundingRate}")
            except Exception as error:
                print(f"  ❌ Failed to fetch {symbol}: {error}")

        # Get contract details
        print("\n📋 Fetching contract details...")
        try:
            btc_contract = await client.get_contract_detail("BTC_USDT")
            if btc_contract.data:
                # Handle both single object and array responses
                contract = (
                    btc_contract.data[0] 
                    if isinstance(btc_contract.data, list) 
                    else btc_contract.data
                )

                print("✅ BTC_USDT Contract:")
                print(f"   Max Leverage: {contract.maxLeverage}x")
                print(f"   Contract Size: {contract.contractSize}")
                print(f"   Taker Fee: {(contract.takerFeeRate * 100):.4f}%")
                print(f"   Maker Fee: {(contract.makerFeeRate * 100):.4f}%")
                print(f"   Min Volume: {contract.minVol}")
                print(f"   Max Volume: {contract.maxVol:,.0f}")
        except Exception as error:
            print(f"❌ Contract details failed: {error}")

        # Get order book depth
        print("\n📊 Fetching order book depth...")
        try:
            depth = await client.get_contract_depth("BTC_USDT", limit=5)

            # Handle different response formats
            asks = depth.asks or (depth.data.asks if depth.data else [])
            bids = depth.bids or (depth.data.bids if depth.data else [])

            if asks and bids:
                print("✅ BTC_USDT Order Book:")
                print(f"   Best Ask: ${asks[0].price} ({asks[0].volume} contracts)")
                print(f"   Best Bid: ${bids[0].price} ({bids[0].volume} contracts)")
                print(f"   Spread: ${(asks[0].price - bids[0].price):.2f}")
                print(f"   Depth: {len(asks)} asks, {len(bids)} bids")
        except Exception as error:
            print(f"❌ Order book depth failed: {error}")

        # Get account information (requires valid auth)
        print("\n🛡️ Fetching account info...")

        try:
            risk_limits = await client.get_risk_limit()
            print(f"✅ Risk limits: {len(risk_limits.data or [])} contracts")
        except Exception as error:
            print(f"❌ Risk limits failed: {error}")

        try:
            fee_rates = await client.get_fee_rate()
            print(f"✅ Fee rates: {len(fee_rates.data or [])} contracts")
        except Exception as error:
            print(f"❌ Fee rates failed: {error}")

        try:
            usdt_asset = await client.get_account_asset("USDT")
            print(f"✅ USDT balance: {usdt_asset.data.availableBalance or 0} USDT")
            print(f"   Total equity: {usdt_asset.data.equity or 0} USDT")
        except Exception as error:
            print(f"❌ Account asset failed: {error}")

        try:
            positions = await client.get_open_positions()
            print(f"✅ Open positions: {len(positions.data or [])}")

            if positions.data:
                for position in positions.data[:3]:  # Show first 3 positions
                    side = "LONG" if position.positionType == 1 else "SHORT"
                    pnl = f"+{position.realised}" if position.realised >= 0 else str(position.realised)
                    print(f"   {position.symbol} {side}: {position.holdVol} @ ${position.holdAvgPrice} (PnL: {pnl})")
        except Exception as error:
            print(f"❌ Open positions failed: {error}")

        # Get order history
        print("\n📋 Fetching order history...")
        try:
            order_history = await client.get_order_history({
                "category": 1,
                "page_num": 1,
                "page_size": 5,
                "states": 3,
                "symbol": "CAKE_USDT",
            })
            orders_count = len(order_history.data.orders) if order_history.data else 0
            print(f"✅ Order history: {orders_count} orders")
        except Exception as error:
            print(f"❌ Order history failed: {error}")

        # Get order deals
        print("\n💼 Fetching order deals...")
        try:
            order_deals = await client.get_order_deals({
                "symbol": "CAKE_USDT",
                "page_num": 1,
                "page_size": 5,
            })
            print(f"✅ Order deals: {len(order_deals.data or [])} transactions")
        except Exception as error:
            print(f"❌ Order deals failed: {error}")

        # Example order submission (COMMENTED OUT FOR SAFETY)
        print("\n🚀 Order submission examples (commented out for safety):")
        print("Uncomment the code below to test real order submission")
        print("⚠️  WARNING: This will create real orders on the exchange!\n")

        """
        # Example 1: Market order (instant execution)
        print("🎯 Market Order Example:")
        ticker = await client.get_ticker("CAKE_USDT")
        current_price = ticker.data.lastPrice
        
        market_order = await client.submit_order({
            "symbol": "CAKE_USDT",
            "price": current_price,  # price is mandatory even for market orders
            "vol": 5,  # volume in tokens
            "side": 1,  # 1 = open long
            "type": 5,  # 5 = market order (instant execution)
            "openType": 1,  # 1 = isolated margin
            "leverage": 10,  # required for isolated margin
        })
        print("Market order result:", market_order)

        # Example 2: IOC order (recommended for fast execution)
        ask = ticker.data.ask1
        ioc_price = ask * 1.005  # +0.5% from ask

        print("⚡ IOC Order Example:")
        ioc_order = await client.submit_order({
            "symbol": "CAKE_USDT",
            "price": ioc_price,
            "vol": 5,
            "side": 1,  # 1 = open long
            "type": 3,  # 3 = IOC (Immediate or Cancel)
            "openType": 1,  # 1 = isolated margin
            "leverage": 10,
        })
        print("IOC order result:", ioc_order)

        # Example 3: Limit order with Stop Loss and Take Profit
        print("📈 Limit Order with SL/TP Example:")
        limit_order = await client.submit_order({
            "symbol": "CAKE_USDT",
            "price": current_price * 0.98,  # limit price 2% below current
            "vol": 5,
            "side": 1,  # 1 = open long
            "type": 1,  # 1 = limit order
            "openType": 1,  # 1 = isolated margin
            "leverage": 10,
            "stopLossPrice": current_price * 0.95,  # stop loss 5% below current
            "takeProfitPrice": current_price * 1.1,  # take profit 10% above current
            "externalOid": "my-limit-order-123",  # external order ID
        })
        print("Limit order result:", limit_order)

        # Example 4: Cancel orders
        if market_order.success and market_order.data:
            print("🗑️ Canceling test order...")
            cancel_result = await client.cancel_order([market_order.data])
            print("Cancel result:", cancel_result)
        """

        print("\n✅ Example completed successfully!")
        print("\n💡 Order Parameters Guide:")
        print("📋 Mandatory Parameters:")
        print("   symbol: Contract name (e.g., 'BTC_USDT')")
        print("   price: Order price (mandatory for ALL order types, including market)")
        print("   vol: Order volume")
        print("   side: 1=open long, 2=close short, 3=open short, 4=close long")
        print("   type: 1=limit, 2=Post Only, 3=IOC, 4=FOK, 5=market, 6=convert")
        print("   openType: 1=isolated margin, 2=cross margin")
        print("\n🔧 Optional Parameters:")
        print("   leverage: Required for isolated margin (openType: 1)")
        print("   positionId: Recommended when closing a position")
        print("   externalOid: External order ID for tracking")
        print("   stopLossPrice: Stop-loss price (number)")
        print("   takeProfitPrice: Take-profit price (number)")
        print("   positionMode: 1=hedge, 2=one-way")
        print("   reduceOnly: For one-way positions only (boolean)")

    except Exception as error:
        print(f"❌ Error: {error}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Always close the client
        await client.close()


# Synchronous example
def main_sync():
    """Synchronous version using MexcFuturesClientSync."""
    from mexc_futures import MexcFuturesClientSync
    
    # Get token from environment variable
    auth_token = os.getenv('WEB_TOKEN')
    
    if not auth_token:
        print("❌ Error: WEB_TOKEN not found in environment variables.")
        return
    
    client = MexcFuturesClientSync({
        "auth_token": auth_token,
        "log_level": "INFO",
    })
    
    try:
        # Test connection
        print("🔌 Testing connection...")
        is_connected = client.test_connection()
        print(f"Connection: {'✅ SUCCESS' if is_connected else '❌ FAILED'}")
        
        if is_connected:
            # Get ticker
            ticker = client.get_ticker("BTC_USDT")
            print(f"💰 BTC Price: ${ticker.data.lastPrice}")
    
    except Exception as error:
        print(f"❌ Error: {error}")
    
    finally:
        client.close()


if __name__ == "__main__":
    print("🚀 MEXC Futures Python SDK - Basic Example")
    print("=" * 50)
    
    # Run async version
    asyncio.run(main())
    
    # Uncomment to test synchronous version
    # print("\n" + "=" * 50)
    # print("🔄 Testing synchronous version...")
    # main_sync()