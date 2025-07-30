#!/usr/bin/env python3
"""
Setup script for EVE Online SSO authentication
This script helps you set up automatic authentication for the WormWarden bot.
"""

import os
import webbrowser
import http.server
import socketserver
import urllib.parse
from urllib.parse import urlparse, parse_qs
from helpers.auth import EVEAuth, PathfinderAuth
from dotenv import load_dotenv

load_dotenv()

class AuthCallbackHandler(http.server.BaseHTTPRequestHandler):
    """Simple HTTP server to handle EVE SSO callback"""
    
    def do_GET(self):
        """Handle the callback from EVE SSO"""
        parsed_url = urlparse(self.path)
        
        if parsed_url.path == '/callback':
            # Parse the authorization code from the URL
            query_params = parse_qs(parsed_url.query)
            auth_code = query_params.get('code', [None])[0]
            state = query_params.get('state', [None])[0]
            
            if auth_code:
                # Send success response
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                
                response_html = """
                <html>
                <head><title>Authentication Successful</title></head>
                <body>
                <h1>✅ Authentication Successful!</h1>
                <p>You can close this window and return to the terminal.</p>
                <script>setTimeout(function(){ window.close(); }, 3000);</script>
                </body>
                </html>
                """
                self.wfile.write(response_html.encode())
                
                # Store the auth code for processing
                self.server.auth_code = auth_code
                self.server.state = state
                
                # Stop the server after a short delay
                import threading
                def stop_server():
                    import time
                    time.sleep(1)
                    self.server.shutdown()
                
                threading.Thread(target=stop_server, daemon=True).start()
                
            else:
                # Send error response
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                
                response_html = """
                <html>
                <head><title>Authentication Failed</title></head>
                <body>
                <h1>❌ Authentication Failed</h1>
                <p>No authorization code received. Please try again.</p>
                </body>
                </html>
                """
                self.wfile.write(response_html.encode())
        else:
            # Send 404 for other paths
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        """Suppress logging for cleaner output"""
        pass

def check_env_vars():
    """Check if required environment variables are set"""
    required_vars = ['EVE_CLIENT_ID', 'EVE_CLIENT_SECRET']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease add these to your .env file:")
        print("EVE_CLIENT_ID=your_eve_client_id")
        print("EVE_CLIENT_SECRET=your_eve_client_secret")
        print("\nYou can get these from: https://developers.eveonline.com/")
        return False
    
    return True

def setup_eve_auth():
    """Set up EVE Online SSO authentication"""
    print("🚀 Setting up EVE Online SSO authentication...")
    
    # Check environment variables
    if not check_env_vars():
        return False
    
    # Initialize EVE auth
    eve_auth = EVEAuth()
    
    # Check if we already have valid tokens
    if eve_auth.is_authenticated():
        print("✅ Already authenticated with EVE Online!")
        char_info = eve_auth.get_character_info()
        if char_info:
            print(f"👤 Authenticated as: {char_info.get('name', 'Unknown')}")
        return True
    
    # Generate authorization URL
    auth_url = eve_auth.get_auth_url()
    print(f"\n🔗 Opening EVE SSO authorization page...")
    print(f"URL: {auth_url}")
    
    # Open browser
    try:
        webbrowser.open(auth_url)
    except Exception as e:
        print(f"⚠️ Could not open browser automatically: {e}")
        print("Please manually open the URL above in your browser.")
    
    # Start local server to handle callback
    print("\n🌐 Starting local server to handle authentication callback...")
    print("Waiting for you to complete authentication in your browser...")
    
    # Create a custom server class to store auth data
    class AuthServer(http.server.HTTPServer):
        def __init__(self, *args, **kwargs):
            self.auth_code = None
            self.state = None
            super().__init__(*args, **kwargs)
    
    # Start server with timeout
    with AuthServer(('localhost', 8080), AuthCallbackHandler) as httpd:
        print("⏰ Server will timeout in 5 minutes if no callback is received...")
        
        # Run server in a separate thread
        import threading
        import time
        
        server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        server_thread.start()
        
        # Wait for auth code or timeout
        start_time = time.time()
        timeout = 300  # 5 minutes
        
        while time.time() - start_time < timeout:
            if httpd.auth_code:
                break
            time.sleep(0.1)
        
        # Shutdown server
        httpd.shutdown()
        server_thread.join(timeout=2)
        
        # Check if we got the auth code
        if httpd.auth_code:
            print("✅ Received authorization code, exchanging for tokens...")
            
            if eve_auth.exchange_code_for_token(httpd.auth_code):
                print("✅ Successfully authenticated with EVE Online!")
                char_info = eve_auth.get_character_info()
                if char_info:
                    print(f"👤 Authenticated as: {char_info.get('name', 'Unknown')}")
                return True
            else:
                print("❌ Failed to exchange authorization code for tokens")
                return False
        else:
            print("❌ No authorization code received within timeout period")
            print("Please try again and complete the authentication quickly.")
            return False

def setup_pathfinder_auth():
    """Set up Pathfinder authentication"""
    print("\n🔧 Setting up Pathfinder authentication...")
    
    eve_auth = EVEAuth()
    if not eve_auth.is_authenticated():
        print("❌ EVE authentication required first")
        return False
    
    pf_auth = PathfinderAuth(eve_auth)
    if pf_auth.authenticate_with_pathfinder():
        print("✅ Pathfinder authentication setup complete!")
        return True
    else:
        print("❌ Pathfinder authentication failed")
        return False

def main():
    """Main setup function"""
    print("🔧 WormWarden Authentication Setup")
    print("=" * 40)
    
    # Step 1: EVE Online SSO
    if not setup_eve_auth():
        print("\n❌ EVE Online authentication failed. Please check your .env file and try again.")
        return False
    
    # Step 2: Pathfinder authentication
    if not setup_pathfinder_auth():
        print("\n⚠️ Pathfinder authentication failed, but EVE authentication is working.")
        print("The bot may still work with manual Pathfinder session cookies.")
    
    print("\n✅ Setup complete!")
    print("\nNext steps:")
    print("1. Update your .env file with any additional Pathfinder-specific settings")
    print("2. Run the bot with: python3 -m main")
    print("3. The bot will now automatically refresh tokens as needed")
    
    return True

if __name__ == "__main__":
    main() 