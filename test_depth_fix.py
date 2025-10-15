#!/usr/bin/env python3
"""Test script to verify the DepthEntry validation fix."""

import json
from mexc_futures.types.market import ContractDepthResponse, DepthEntry, ContractDepthData


def test_depth_entry_from_array():
    """Test DepthEntry creation from array format."""
    print("🧪 Testing DepthEntry validation...")
    
    # Test array format [price, volume, count]
    array_data = [113035.6, 79465, 1]
    
    try:
        entry = DepthEntry.validate(array_data)
        print(f"✅ Array validation success: price={entry.price}, volume={entry.volume}, count={entry.count}")
        
        assert entry.price == 113035.6
        assert entry.volume == 79465
        assert entry.count == 1
        print("✅ Array validation assertions passed")
        
    except Exception as e:
        print(f"❌ Array validation failed: {e}")
        return False
    
    # Test array format [price, volume] (without count)
    array_data_2 = [113035.7, 75669]
    
    try:
        entry2 = DepthEntry.validate(array_data_2)
        print(f"✅ Array validation (no count) success: price={entry2.price}, volume={entry2.volume}, count={entry2.count}")
        
        assert entry2.price == 113035.7
        assert entry2.volume == 75669
        assert entry2.count is None
        print("✅ Array validation (no count) assertions passed")
        
    except Exception as e:
        print(f"❌ Array validation (no count) failed: {e}")
        return False
    
    return True


def test_contract_depth_response():
    """Test ContractDepthResponse with array data format."""
    print("\n🧪 Testing ContractDepthResponse validation...")
    
    # Mock API response with array format (similar to what MEXC API returns)
    mock_response = {
        "success": True,
        "code": 0,
        "data": {
            "asks": [
                [113035.6, 79465, 1],
                [113035.7, 75669, 1], 
                [113035.8, 82341, 1]
            ],
            "bids": [
                [113035.5, 68432, 1],
                [113035.4, 71234, 1],
                [113035.3, 59876, 1]
            ],
            "version": 123456789,
            "timestamp": 1697356800000
        }
    }
    
    try:
        response = ContractDepthResponse(**mock_response)
        print("✅ ContractDepthResponse validation success")
        
        if response.data:
            print(f"   📊 Asks: {len(response.data.asks)} entries")
            print(f"   📊 Bids: {len(response.data.bids)} entries")
            
            # Check first ask
            first_ask = response.data.asks[0]
            print(f"   💰 Best Ask: ${first_ask.price} ({first_ask.volume} vol, {first_ask.count} orders)")
            
            # Check first bid
            first_bid = response.data.bids[0]
            print(f"   💰 Best Bid: ${first_bid.price} ({first_bid.volume} vol, {first_bid.count} orders)")
            
            assert first_ask.price == 113035.6
            assert first_ask.volume == 79465
            assert first_ask.count == 1
            
            assert first_bid.price == 113035.5
            assert first_bid.volume == 68432
            assert first_bid.count == 1
            
            print("✅ ContractDepthResponse assertions passed")
        
    except Exception as e:
        print(f"❌ ContractDepthResponse validation failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


def test_direct_response_format():
    """Test ContractDepthResponse with direct response format (no 'data' wrapper)."""
    print("\n🧪 Testing direct response format...")
    
    # Mock direct response format
    mock_direct_response = {
        "asks": [
            [113035.6, 79465, 1],
            [113035.7, 75669, 1]
        ],
        "bids": [
            [113035.5, 68432, 1],
            [113035.4, 71234, 1]
        ],
        "version": 123456789,
        "timestamp": 1697356800000
    }
    
    try:
        response = ContractDepthResponse(**mock_direct_response)
        print("✅ Direct response validation success")
        
        if response.asks and response.bids:
            print(f"   📊 Direct Asks: {len(response.asks)} entries")
            print(f"   📊 Direct Bids: {len(response.bids)} entries")
            
            # Check first ask
            first_ask = response.asks[0]
            print(f"   💰 Best Ask: ${first_ask.price} ({first_ask.volume} vol)")
            
            assert first_ask.price == 113035.6
            assert first_ask.volume == 79465
            
            print("✅ Direct response assertions passed")
        
    except Exception as e:
        print(f"❌ Direct response validation failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


def main():
    """Run all tests."""
    print("🚀 Testing DepthEntry validation fixes")
    print("=" * 50)
    
    tests = [
        test_depth_entry_from_array,
        test_contract_depth_response,
        test_direct_response_format
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()  # Add spacing between tests
    
    print("=" * 50)
    print(f"🎯 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("✅ All tests passed! The DepthEntry validation fix is working correctly.")
        return True
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)