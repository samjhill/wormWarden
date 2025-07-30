#!/usr/bin/env python3
"""
Debug script to examine EVE tokens
"""

import os
import json
from dotenv import load_dotenv

load_dotenv()

def debug_token():
    """Debug the stored EVE token"""
    token_file = "eve_tokens.json"
    
    if not os.path.exists(token_file):
        print("❌ No token file found")
        return
    
    try:
        with open(token_file, 'r') as f:
            data = json.load(f)
        
        print("📄 Token file contents:")
        print(f"Access token: {data.get('access_token', 'None')[:50]}...")
        print(f"Refresh token: {data.get('refresh_token', 'None')[:50]}...")
        print(f"Expires at: {data.get('expires_at', 'None')}")
        
        # Try to decode the JWT token
        if data.get('access_token'):
            try:
                import jwt
                decoded = jwt.decode(data['access_token'], options={"verify_signature": False})
                print("\n🔍 Decoded token:")
                print(f"Subject: {decoded.get('sub', 'None')}")
                print(f"Name: {decoded.get('name', 'None')}")
                print(f"Scopes: {decoded.get('scp', [])}")
                print(f"Expires: {decoded.get('exp', 'None')}")
                print(f"Issued at: {decoded.get('iat', 'None')}")
                
                # Extract character ID
                if decoded.get('sub'):
                    character_id = decoded['sub'].split(':')[-1]
                    print(f"Character ID: {character_id}")
                    
                    # Test ESI endpoint
                    import requests
                    url = f"https://esi.evetech.net/latest/characters/{character_id}/"
                    response = requests.get(url)
                    if response.status_code == 200:
                        char_data = response.json()
                        print(f"✅ ESI character data: {char_data.get('name', 'Unknown')}")
                    else:
                        print(f"❌ ESI request failed: {response.status_code}")
                
            except Exception as e:
                print(f"❌ Error decoding token: {e}")
        
    except Exception as e:
        print(f"❌ Error reading token file: {e}")

if __name__ == "__main__":
    debug_token() 