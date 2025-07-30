import os
import time
import json
import requests
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()

class EVEAuth:
    """Handles EVE Online SSO authentication and token management"""
    
    def __init__(self):
        self.client_id = os.getenv("EVE_CLIENT_ID")
        self.client_secret = os.getenv("EVE_CLIENT_SECRET")
        self.callback_url = os.getenv("EVE_CALLBACK_URL", "http://localhost:8080/callback")
        self.token_file = "eve_tokens.json"
        self.access_token = None
        self.refresh_token = None
        self.token_expires_at = None
        
        # Load existing tokens if available
        self._load_tokens()
    
    def _load_tokens(self):
        """Load tokens from file if they exist"""
        if os.path.exists(self.token_file):
            try:
                with open(self.token_file, 'r') as f:
                    data = json.load(f)
                    self.access_token = data.get('access_token')
                    self.refresh_token = data.get('refresh_token')
                    expires_at = data.get('expires_at')
                    if expires_at:
                        self.token_expires_at = datetime.fromisoformat(expires_at)
            except Exception as e:
                print(f"⚠️ Error loading tokens: {e}")
    
    def _save_tokens(self):
        """Save tokens to file"""
        data = {
            'access_token': self.access_token,
            'refresh_token': self.refresh_token,
            'expires_at': self.token_expires_at.isoformat() if self.token_expires_at else None
        }
        with open(self.token_file, 'w') as f:
            json.dump(data, f)
    
    def get_auth_url(self) -> str:
        """Generate EVE SSO authorization URL"""
        scopes = "publicData esi-universe.read_structures.v1"
        state = str(int(time.time()))
        
        params = {
            'response_type': 'code',
            'redirect_uri': self.callback_url,
            'client_id': self.client_id,
            'scope': scopes,
            'state': state
        }
        
        url = "https://login.eveonline.com/v2/oauth/authorize"
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{url}?{query_string}"
    
    def exchange_code_for_token(self, auth_code: str) -> bool:
        """Exchange authorization code for access token"""
        url = "https://login.eveonline.com/v2/oauth/token"
        
        data = {
            'grant_type': 'authorization_code',
            'code': auth_code,
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'WormWarden/1.0'
        }
        
        try:
            response = requests.post(url, data=data, headers=headers)
            response.raise_for_status()
            token_data = response.json()
            
            self.access_token = token_data['access_token']
            self.refresh_token = token_data['refresh_token']
            self.token_expires_at = datetime.now() + timedelta(seconds=token_data['expires_in'])
            
            self._save_tokens()
            print("✅ Successfully obtained EVE SSO tokens")
            return True
            
        except Exception as e:
            print(f"❌ Error exchanging code for token: {e}")
            return False
    
    def refresh_access_token(self) -> bool:
        """Refresh the access token using refresh token"""
        if not self.refresh_token:
            print("❌ No refresh token available")
            return False
        
        url = "https://login.eveonline.com/v2/oauth/token"
        
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token,
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'WormWarden/1.0'
        }
        
        try:
            response = requests.post(url, data=data, headers=headers)
            response.raise_for_status()
            token_data = response.json()
            
            self.access_token = token_data['access_token']
            self.refresh_token = token_data.get('refresh_token', self.refresh_token)
            self.token_expires_at = datetime.now() + timedelta(seconds=token_data['expires_in'])
            
            self._save_tokens()
            print("✅ Successfully refreshed EVE SSO tokens")
            return True
            
        except Exception as e:
            print(f"❌ Error refreshing token: {e}")
            return False
    
    def get_valid_token(self) -> Optional[str]:
        """Get a valid access token, refreshing if necessary"""
        if not self.access_token:
            print("❌ No access token available")
            return None
        
        # Check if token is expired or will expire soon (within 5 minutes)
        if self.token_expires_at and datetime.now() + timedelta(minutes=5) >= self.token_expires_at:
            print("🔄 Access token expired or expiring soon, refreshing...")
            if not self.refresh_access_token():
                return None
        
        # Debug: Check token format
        if self.access_token:
            print(f"🔍 Token available: {self.access_token[:20]}...")
        
        return self.access_token
    
    def get_character_info(self) -> Optional[Dict[str, Any]]:
        """Get character information from EVE SSO"""
        token = self.get_valid_token()
        if not token:
            return None
        
        try:
            import jwt
            # Decode the JWT token to get character info
            decoded = jwt.decode(token, options={"verify_signature": False})
            character_id = decoded.get('sub', '').split(':')[-1]
            character_name = decoded.get('name', 'Unknown')
            
            print(f"🔍 Token decoded - Character ID: {character_id}, Name: {character_name}")
            
            # Return basic character info from the token
            return {
                'character_id': character_id,
                'name': character_name,
                'corporation_id': decoded.get('corporation_id', ''),
                'alliance_id': decoded.get('alliance_id', '')
            }
            
        except jwt.InvalidTokenError:
            print("❌ Invalid JWT token format")
            return None
        except Exception as e:
            print(f"❌ Error getting character info: {e}")
            return None
    
    def is_authenticated(self) -> bool:
        """Check if we have valid authentication"""
        return self.get_valid_token() is not None


class PathfinderAuth:
    """Handles Pathfinder-specific authentication using EVE tokens"""
    
    def __init__(self, eve_auth: EVEAuth):
        self.eve_auth = eve_auth
        self.pathfinder_url = os.getenv("PATHFINDER_URL", "https://path.shadowflight.org")
        self.session = requests.Session()
    
    def authenticate_with_pathfinder(self) -> bool:
        """Authenticate with Pathfinder using EVE SSO tokens"""
        if not self.eve_auth.is_authenticated():
            print("❌ EVE authentication required first")
            return False
        
        # Get character info
        char_info = self.eve_auth.get_character_info()
        if not char_info:
            print("❌ Could not get character info")
            return False
        
        print(f"👤 Authenticating as: {char_info.get('name', 'Unknown')}")
        
        # Note: Most Pathfinder instances don't support EVE SSO authentication directly
        # They typically use session-based authentication with cookies
        # This is a placeholder for future Pathfinder SSO integration
        try:
            # Set up basic headers for Pathfinder
            self.session.headers.update({
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Accept-Language": "en-US,en;q=0.9",
                "User-Agent": "Mozilla/5.0",
                "X-Requested-With": "XMLHttpRequest",
                "Referer": f"{self.pathfinder_url}/map"
            })
            
            # For now, we'll just set up the headers but note that EVE SSO
            # authentication with Pathfinder is not widely supported
            print("⚠️ EVE SSO authentication with Pathfinder is experimental")
            print("💡 Most Pathfinder instances require manual session cookies")
            
            return True
            
        except Exception as e:
            print(f"❌ Error setting up Pathfinder authentication: {e}")
            return False
    
    def get_session_headers(self) -> Dict[str, str]:
        """Get headers for Pathfinder API requests"""
        return dict(self.session.headers) 