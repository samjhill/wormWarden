import os
import requests
from typing import Optional, Dict, Any

from dotenv import load_dotenv

load_dotenv()

# Try to import the new auth system
try:
    from .auth import EVEAuth, PathfinderAuth
    AUTH_AVAILABLE = True
except ImportError:
    AUTH_AVAILABLE = False

# Legacy headers for backward compatibility
LEGACY_HEADERS = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-US,en;q=0.9",
    "Cookie": (
        "cookie=1; "
        f"pathfinder_session={os.getenv('PF_SESSION', '')}; "
        f"char_756f808ea2cc0b9e3480676514e66368={os.getenv('PF_CHAR_COOKIE', '')}"
    ),
    "pf-character": os.getenv("PF_CHARACTER", ""),
    "User-Agent": "Mozilla/5.0",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://path.shadowflight.org/map"
}

class PathfinderClient:
    """Enhanced Pathfinder client with automatic authentication"""
    
    def __init__(self):
        self.session = requests.Session()
        self.eve_auth = None
        self.pf_auth = None
        self.pathfinder_url = os.getenv("PATHFINDER_URL", "https://path.shadowflight.org")
        
        # Initialize authentication if available
        if AUTH_AVAILABLE:
            try:
                self.eve_auth = EVEAuth()
                self.pf_auth = PathfinderAuth(self.eve_auth)
            except Exception as e:
                print(f"⚠️ Could not initialize EVE auth: {e}")
        
        # Set up headers
        self._setup_headers()
    
    def _setup_headers(self):
        """Set up headers for requests"""
        # Check if manual session cookies are available
        pf_session = os.getenv('PF_SESSION')
        pf_char_cookie = os.getenv('PF_CHAR_COOKIE')
        
        if pf_session and pf_char_cookie:
            # Use manual session cookies (most reliable)
            self.session.headers.update(LEGACY_HEADERS)
            print("✅ Using manual session cookies")
            return
        
        # Try EVE SSO authentication (experimental)
        if self.pf_auth and self.pf_auth.authenticate_with_pathfinder():
            self.session.headers.update(self.pf_auth.get_session_headers())
            print("⚠️ Using EVE SSO authentication (experimental)")
        else:
            # No authentication available
            self.session.headers.update(LEGACY_HEADERS)
            print("❌ No authentication available")
            print("💡 Please set up manual session cookies in your .env file:")
            print("   PF_SESSION=your_session_cookie")
            print("   PF_CHAR_COOKIE=your_char_cookie")
            print("   PF_CHARACTER=your_character_id")
    
    def _ensure_authenticated(self) -> bool:
        """Ensure we have valid authentication"""
        # Check if manual session cookies are set (most reliable)
        pf_session = os.getenv('PF_SESSION')
        pf_char_cookie = os.getenv('PF_CHAR_COOKIE')
        
        if pf_session and pf_char_cookie:
            return True
        
        # Check if EVE auth is available and valid (experimental)
        if self.eve_auth and self.eve_auth.is_authenticated():
            return True
        
        return False
    
    def get_map_data(self) -> Optional[Dict[str, Any]]:
        """Get map data from Pathfinder with automatic authentication"""
        if not self._ensure_authenticated():
            print("❌ No valid authentication found")
            print("Please run: python3 setup_auth.py")
            return None
        
        url = f"{self.pathfinder_url}/api/Map/updateData"
        headers = self.session.headers.copy()
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        data = "getUserData=1"
        
        try:
            r = self.session.post(url, headers=headers, data=data)
            r.raise_for_status()
            return r.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching map data: {e}")
            
            # If using EVE auth, try refreshing tokens
            if self.eve_auth and self.eve_auth.refresh_access_token():
                print("🔄 Refreshed tokens, retrying...")
                self._setup_headers()
                try:
                    r = self.session.post(url, headers=headers, data=data)
                    r.raise_for_status()
                    return r.json()
                except requests.exceptions.RequestException as e2:
                    print(f"❌ Retry failed: {e2}")
            
            # If we're using EVE auth and it's failing, suggest manual cookies
            if self.eve_auth and self.eve_auth.is_authenticated():
                print("💡 EVE authentication is working, but Pathfinder is rejecting the request.")
                print("💡 This might be because:")
                print("   - Pathfinder doesn't support EVE SSO authentication")
                print("   - You need to use manual session cookies instead")
                print("💡 To use manual cookies, add to your .env file:")
                print("   PF_SESSION=your_session_cookie")
                print("   PF_CHAR_COOKIE=your_char_cookie")
                print("   PF_CHARACTER=your_character_id")
            
            return None

def get_map_data():
    """Legacy function for backward compatibility"""
    client = PathfinderClient()
    return client.get_map_data()

def print_graph(graph, system_name_lookup):
    print("🌌 Pathfinder Wormhole Graph:")
    for system_id, neighbors in graph.items():
        name = system_name_lookup.get(system_id, str(system_id))
        neighbor_names = [f"{system_name_lookup.get(n, str(n))} (id: {n})" for n in neighbors]
        print(f"  {name} (id {system_id}) → {', '.join(neighbor_names)}")