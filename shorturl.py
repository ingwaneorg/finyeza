
"""
Command line tool for managing short URLs
Usage:
    python shorturl.py create <shortcode> <destination>
    python shorturl.py stats <shortcode>
    python shorturl.py list
"""

import requests
import sys
import os
import json
from datetime import datetime

# Configuration
API_BASE_URL = "https://go.ingwane.com/api"  # Update when deployed
LOCAL_URL = "http://localhost:8080/api"      # For local testing
API_KEY = os.environ.get('API_KEY')

def get_api_url():
    """Get API URL based on environment"""
    if os.environ.get('LOCAL_DEV'):
        return LOCAL_URL
    return API_BASE_URL

def make_request(method, endpoint, data=None):
    """Make API request with authentication"""
    if not API_KEY:
        print("Error: API_KEY environment variable not set")
        sys.exit(1)
    
    url = f"{get_api_url()}{endpoint}"
    headers = {
        'X-API-Key': API_KEY,
        'Content-Type': 'application/json'
    }
    
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=data)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        return response
    except requests.exceptions.ConnectionError:
        print(f"Error: Could not connect to {url}")
        print("Make sure the service is running and accessible")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
        sys.exit(1)

def create_url(shortcode, destination):
    """Create a new short URL"""
    data = {
        'shortcode': shortcode,
        'destination': destination
    }
    
    response = make_request('POST', '/create', data)
    
    if response.status_code == 201:
        result = response.json()
        print(f"✅ Created successfully!")
        print(f"Short URL: {result['short_url']}")
        print(f"Destination: {result['destination']}")
        print(f"Created: {result['created']}")
    elif response.status_code == 409:
        print(f"❌ Error: Shortcode '{shortcode}' already exists")
    elif response.status_code == 401:
        print("❌ Error: Invalid API key")
    else:
        try:
            error = response.json().get('error', 'Unknown error')
            print(f"❌ Error: {error}")
        except:
            print(f"❌ Error: HTTP {response.status_code}")

def get_stats(shortcode):
    """Get statistics for a short URL"""
    response = make_request('GET', f'/stats/{shortcode}')
    
    if response.status_code == 200:
        data = response.json()
        print(f"📊 Stats for '{shortcode}':")
        print(f"Destination: {data['destination']}")
        print(f"Total clicks: {data['total_clicks']}")
        print(f"Created: {data['created']}")
        print(f"Is zip file: {'Yes' if data['is_zip'] else 'No'}")
        
        if data['recent_clicks']:
            print(f"\n🕒 Recent clicks ({len(data['recent_clicks'])}):")
            for click in data['recent_clicks'][:10]:  # Show last 10
                timestamp = datetime.fromisoformat(click['timestamp'].replace('Z', '+00:00'))
                print(f"  {timestamp.strftime('%Y-%m-%d %H:%M:%S')} - {click['ip']}")
        else:
            print("\n🕒 No clicks yet")
            
    elif response.status_code == 404:
        print(f"❌ Error: Shortcode '{shortcode}' not found")
    elif response.status_code == 401:
        print("❌ Error: Invalid API key")
    else:
        try:
            error = response.json().get('error', 'Unknown error')
            print(f"❌ Error: {error}")
        except:
            print(f"❌ Error: HTTP {response.status_code}")

def list_urls():
    """List all short URLs"""
    response = make_request('GET', '/list')
    
    if response.status_code == 200:
        data = response.json()
        urls = data['urls']
        
        if not urls:
            print("📝 No URLs found")
            return
        
        print(f"📝 Found {len(urls)} URL(s):")
        print()
        
        for url in urls:
            created = datetime.fromisoformat(url['created']).strftime('%Y-%m-%d')
            zip_indicator = "📦" if url['is_zip'] else "🔗"
            print(f"{zip_indicator} {url['shortcode']} -> {url['destination']}")
            print(f"   Created: {created} | Clicks: {url['clicks']}")
            print()
            
    elif response.status_code == 401:
        print("❌ Error: Invalid API key")
    else:
        try:
            error = response.json().get('error', 'Unknown error')
            print(f"❌ Error: {error}")
        except:
            print(f"❌ Error: HTTP {response.status_code}")

def show_help():
    """Show help message"""
    print("URL Forwarder CLI Tool")
    print()
    print("Usage:")
    print("  python shorturl.py create <shortcode> <destination>")
    print("  python shorturl.py stats <shortcode>")
    print("  python shorturl.py list")
    print("  python shorturl.py help")
    print()
    print("Examples:")
    print("  python shorturl.py create project-files https://example.com/files.zip")
    print("  python shorturl.py stats project-files")
    print("  python shorturl.py list")
    print()
    print("Environment variables:")
    print("  API_KEY      - Your API key (required)")
    print("  LOCAL_DEV    - Set to use localhost:8080 for testing")

def main():
    """Main CLI entry point"""
    if len(sys.argv) < 2:
        show_help()
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == 'create':
        if len(sys.argv) != 4:
            print("Usage: python shorturl.py create <shortcode> <destination>")
            sys.exit(1)
        create_url(sys.argv[2], sys.argv[3])
        
    elif command == 'stats':
        if len(sys.argv) != 3:
            print("Usage: python shorturl.py stats <shortcode>")
            sys.exit(1)
        get_stats(sys.argv[2])
        
    elif command == 'list':
        list_urls()
        
    elif command == 'help':
        show_help()
        
    else:
        print(f"Unknown command: {command}")
        show_help()
        sys.exit(1)

if __name__ == '__main__':
    main()
