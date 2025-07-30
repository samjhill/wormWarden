#!/usr/bin/env python3
"""
Test script for WormWarden authentication
"""

import os
from dotenv import load_dotenv
from helpers.pathfinder import PathfinderClient
from helpers.auth import EVEAuth

load_dotenv()

def test_eve_auth():
    """Test EVE Online authentication"""
    print("🧪 Testing EVE Online authentication...")
    
    try:
        eve_auth = EVEAuth()
        
        if eve_auth.is_authenticated():
            print("✅ EVE authentication is working!")
            char_info = eve_auth.get_character_info()
            if char_info:
                print(f"👤 Authenticated as: {char_info.get('name', 'Unknown')}")
            return True
        else:
            print("❌ EVE authentication failed")
            print("Please run: python3 setup_auth.py")
            return False
            
    except Exception as e:
        print(f"❌ Error testing EVE auth: {e}")
        return False

def test_pathfinder_auth():
    """Test Pathfinder authentication"""
    print("\n🧪 Testing Pathfinder authentication...")
    
    try:
        client = PathfinderClient()
        data = client.get_map_data()
        
        if data:
            print("✅ Pathfinder authentication is working!")
            print(f"📊 Retrieved map data with {len(data.get('mapData', []))} maps")
            return True
        else:
            print("❌ Pathfinder authentication failed")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Pathfinder auth: {e}")
        return False

def main():
    """Run all tests"""
    print("🔧 WormWarden Authentication Test")
    print("=" * 40)
    
    eve_ok = test_eve_auth()
    pf_ok = test_pathfinder_auth()
    
    print("\n" + "=" * 40)
    if eve_ok and pf_ok:
        print("✅ All tests passed! Your authentication is working correctly.")
    elif eve_ok:
        print("⚠️ EVE authentication works, but Pathfinder authentication failed.")
        print("This might be due to Pathfinder-specific configuration issues.")
    else:
        print("❌ Authentication tests failed.")
        print("Please run: python3 setup_auth.py")

if __name__ == "__main__":
    main() 