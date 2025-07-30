#!/usr/bin/env python3
"""
Helper script to guide users on getting Pathfinder session cookies
"""

import webbrowser
import time

def main():
    print("🍪 Pathfinder Session Cookie Helper")
    print("=" * 40)
    print()
    print("Since Pathfinder doesn't support EVE SSO authentication directly,")
    print("you'll need to get your session cookies manually.")
    print()
    print("Here's how to get your session cookies:")
    print()
    print("1. 🔗 Open Pathfinder in your browser")
    print("2. 🔐 Log in to Pathfinder")
    print("3. 🍪 Open browser developer tools (F12)")
    print("4. 📋 Go to Application/Storage tab")
    print("5. 🔍 Look for cookies under the Pathfinder domain")
    print("6. 📝 Copy these cookie values:")
    print()
    print("   - pathfinder_session")
    print("   - char_756f808ea2cc0b9e3480676514e66368")
    print("   - pf-character (character ID)")
    print()
    print("7. 📄 Add them to your .env file:")
    print()
    print("   PF_SESSION=your_pathfinder_session_value")
    print("   PF_CHAR_COOKIE=your_char_cookie_value")
    print("   PF_CHARACTER=your_character_id")
    print()
    
    # Ask if user wants to open Pathfinder
    response = input("Would you like to open Pathfinder now? (y/n): ")
    if response.lower() in ['y', 'yes']:
        pathfinder_url = input("Enter your Pathfinder URL (or press Enter for default): ").strip()
        if not pathfinder_url:
            pathfinder_url = "https://path.shadowflight.org"
        
        print(f"🔗 Opening {pathfinder_url}...")
        webbrowser.open(pathfinder_url)
        
        print()
        print("📋 After logging in, follow these steps:")
        print("1. Press F12 to open developer tools")
        print("2. Go to Application tab (Chrome) or Storage tab (Firefox)")
        print("3. Click on Cookies in the left sidebar")
        print("4. Click on your Pathfinder domain")
        print("5. Look for the cookie names mentioned above")
        print("6. Copy their values to your .env file")
        print()
        print("💡 Tip: The cookies will expire, so you may need to refresh them periodically")
    
    print()
    print("✅ Once you've added the cookies to your .env file, run:")
    print("   python3 -m main")
    print()
    print("🎯 The bot will automatically use manual session cookies when available.")

if __name__ == "__main__":
    main() 