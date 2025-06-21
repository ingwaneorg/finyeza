"""
Command line tool for managing short URLs
Usage:
    python shorturl.py create <shortcode> <destination>
    python shorturl.py enable <shortcode>
    python shorturl.py disable <shortcode>
    python shorturl.py list
    python shorturl.py stats <shortcode>
"""

import sys
import os
from datetime import datetime, timezone
from google.cloud import firestore
from google.cloud.firestore_v1 import FieldFilter

# List of reserved words that can't be shortcodes
RESERVED_WORDS = ['version']

# Initialize Firestore client
db = firestore.Client(database='finyeza')

# Check if URL points to a zip file
def is_zip_file(url):
    return url.lower().endswith('.zip')

# Create a new short URL
def create_url(shortcode, destination):
    shortcode = shortcode.lower()
    
    # Validate shortcode format (letters, numbers, hyphens only)
    if not all(c.isalnum() or c == '-' for c in shortcode):
        print(f"ERROR: Shortcode can only contain letters, numbers, and hyphens")
        return
    
    # Don't allow reserved words
    if shortcode in RESERVED_WORDS:
        print(f"ERROR: Shortcode '{shortcode}' is a reserved word")
        return

    # Check if shortcode already exists
    doc_ref = db.collection('urls').document(shortcode)
    if doc_ref.get().exists:
        print(f"ERROR: Shortcode '{shortcode}' already exists")
        return

    # Destination must start with http or https
    if not destination.startswith(('http://', 'https://')):
        print(f"ERROR: Destination URL must start with http:// or https://")
        return

    # Create new URL record (disabled by default)
    url_data = {
        'destination': destination,
        'created': datetime.now(timezone.utc),
        'updated': datetime.now(timezone.utc),
        'enabled': False,
        'clicks': 0
    }
    
    try:
        doc_ref.set(url_data)
        print(f"OK Created shortcode '{shortcode}'")
        print(f"   Destination: {destination}")
        print(f"   Status: Disabled (use 'enable {shortcode}' to activate)")
        print(f"   URL: https://go.ingwane.com/{shortcode}")
        
    except Exception as e:
        print(f"ERROR creating shortcode: {e}")

# Enable a short URL
def enable_url(shortcode):
    shortcode = shortcode.lower()

    doc_ref = db.collection('urls').document(shortcode)
    doc = doc_ref.get()
    
    if not doc.exists:
        print(f"ERROR: Shortcode '{shortcode}' not found")
        return
    
    try:
        doc_ref.update({
            'enabled': True,
            'updated': datetime.now(timezone.utc),
        })
        print(f"OK Enabled shortcode '{shortcode}'")
        print(f"   URL: https://go.ingwane.com/{shortcode}")
    except Exception as e:
        print(f"ERROR enabling shortcode: {e}")

# Disable a short URL
def disable_url(shortcode):
    shortcode = shortcode.lower()
    doc_ref = db.collection('urls').document(shortcode)
    doc = doc_ref.get()
    
    if not doc.exists:
        print(f"ERROR: Shortcode '{shortcode}' not found")
        return
    
    try:
        doc_ref.update({
            'enabled': False,
            'updated': datetime.now(timezone.utc),
        })
        print(f"OK Disabled shortcode '{shortcode}'")
    except Exception as e:
        print(f"ERROR disabling shortcode: {e}")

# Get statistics for a short URL
def get_stats(shortcode):
    shortcode = shortcode.lower()
    doc_ref = db.collection('urls').document(shortcode)
    doc = doc_ref.get()
    
    if not doc.exists:
        print(f"ERROR: Shortcode '{shortcode}' not found")
        return
    
    data = doc.to_dict()
    status = "[ON]" if data.get('enabled', False) else "[OFF]"
    zip_indicator = "[ZIP]" if is_zip_file(data['destination']) else "[LINK]"
    
    print(f"STATS for '{shortcode}':")
    print(f"   Status: {status}")
    print(f"   Type: {zip_indicator}")
    print(f"   Destination: {data['destination']}")
    print(f"   Total clicks: {data.get('clicks', 0)}")
    print(f"   Created: {data['created'].strftime('%Y-%m-%d %H:%M')}")
    print(f"   Updated: {data['updated'].strftime('%Y-%m-%d %H:%M')}")
    print(f"   URL: https://go.ingwane.com/{shortcode}")

# List all short URLs
def list_urls():
    try:
        docs = db.collection('urls').stream()  # no need to sort as this is done below

        urls = []
        for doc in docs:
            data = doc.to_dict()
            urls.append({
                'shortcode': doc.id,
                'destination': data['destination'],
                'enabled': data.get('enabled', False),
                'clicks': data.get('clicks', 0),
                'created': data['created'],
                'updated': data['updated'],
            })
        
        if not urls:
            print("FOUND No URLs found")
            return
        
        # First: sort by updated date (newest first)
        urls.sort(key=lambda x: x['updated'], reverse=True)
        # Second: sort by enabled status (enabled first) - stable sort preserves the time ordering within groups
        urls.sort(key=lambda x: not x['enabled'])
        print(urls)

        print(f"FOUND {len(urls)} shortcode(s):")
        print()
        
        for url in urls:
            status = "[ON] " if url['enabled'] else "[OFF]"
            zip_indicator = "[ZIP]" if is_zip_file(url['destination']) else "[LINK]"
            updated = url['updated'].strftime('%Y-%m-%d %H:%M')
            
            print(f"{status}{zip_indicator} {url['shortcode']}")
            print(f"   {url['destination']}")
            print(f"   Updated: {updated} | Clicks: {url['clicks']}")
            print()
            
    except Exception as e:
        print(f"ERROR listing URLs: {e}")

# Disable all currently enabled URLs
def disable_all():
    try:
        docs = db.collection('urls').where(filter=FieldFilter('enabled', '==', True)).stream()

        disabled_count = 0
        for doc in docs:
            doc.reference.update({
                'enabled': False,
                'updated': datetime.now(timezone.utc),
            })
            disabled_count += 1
            print(f"OK Disabled {doc.id}")
        
        if disabled_count == 0:
            print("FOUND No enabled URLs found")
        else:
            print(f"OK Disabled {disabled_count} shortcode(s)")
            
    except Exception as e:
        print(f"ERROR disabling URLs: {e}")

# Show help message
def show_help():
    print("Finyeza URL Forwarder CLI Tool")
    print()
    print("Usage:")
    print("  python shorturl.py create <shortcode> <destination>")
    print("  python shorturl.py enable <shortcode>")
    print("  python shorturl.py disable <shortcode>")
    print("  python shorturl.py disable-all")
    print("  python shorturl.py stats <shortcode>")
    print("  python shorturl.py list")
    print("  python shorturl.py help")
    print()
    print("Examples:")
    print("  python shorturl.py create de5m2 https://storage.googleapis.com/.../module2.zip")
    print("  python shorturl.py enable de5m2")
    print("  python shorturl.py disable de5m2")
    print("  python shorturl.py stats de5m2")
    print()
    print("Weekly workflow:")
    print("  Sunday:  python shorturl.py enable de5m2")
    print("  Friday:  python shorturl.py disable de5m2")

# Main CLI entry point
def main():
    if len(sys.argv) < 2:
        show_help()
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == 'create':
        if len(sys.argv) != 4:
            print("Usage: python shorturl.py create <shortcode> <destination>")
            sys.exit(1)
        create_url(sys.argv[2], sys.argv[3])
        
    elif command == 'enable':
        if len(sys.argv) != 3:
            print("Usage: python shorturl.py enable <shortcode>")
            sys.exit(1)
        enable_url(sys.argv[2])
        
    elif command == 'disable':
        if len(sys.argv) != 3:
            print("Usage: python shorturl.py disable <shortcode>")
            sys.exit(1)
        disable_url(sys.argv[2])
        
    elif command == 'disable-all':
        disable_all()
        
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