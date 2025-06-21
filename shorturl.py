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
from datetime import datetime
from google.cloud import firestore

# Initialize Firestore client
db = firestore.Client(database='finyeza')

def is_zip_file(url):
    """Check if URL points to a zip file"""
    return url.lower().endswith('.zip')

def create_url(shortcode, destination):
    """Create a new short URL"""
    shortcode = shortcode.lower()
    
    # Validate shortcode format (letters, numbers, hyphens only)
    if not all(c.isalnum() or c == '-' for c in shortcode):
        print("❌ Error: Shortcode can only contain letters, numbers, and hyphens")
        return
    
    # Check if shortcode already exists
    doc_ref = db.collection('urls').document(shortcode)
    if doc_ref.get().exists:
        print(f"❌ Error: Shortcode '{shortcode}' already exists")
        return
    
    # Create new URL record (disabled by default)
    url_data = {
        'destination': destination,
        'created': datetime.utcnow(),
        'enabled': False,
        'clicks': 0
    }
    
    try:
        doc_ref.set(url_data)
        print(f"✅ Created shortcode '{shortcode}'")
        print(f"   Destination: {destination}")
        print(f"   Status: Disabled (use 'enable {shortcode}' to activate)")
        print(f"   URL: https://go.ingwane.com/{shortcode}")
        
    except Exception as e:
        print(f"❌ Error creating shortcode: {e}")

def enable_url(shortcode):
    """Enable a short URL"""
    shortcode = shortcode.lower()
    doc_ref = db.collection('urls').document(shortcode)
    doc = doc_ref.get()
    
    if not doc.exists:
        print(f"❌ Error: Shortcode '{shortcode}' not found")
        return
    
    try:
        doc_ref.update({'enabled': True})
        print(f"✅ Enabled shortcode '{shortcode}'")
        print(f"   URL: https://go.ingwane.com/{shortcode}")
    except Exception as e:
        print(f"❌ Error enabling shortcode: {e}")

def disable_url(shortcode):
    """Disable a short URL"""
    shortcode = shortcode.lower()
    doc_ref = db.collection('urls').document(shortcode)
    doc = doc_ref.get()
    
    if not doc.exists:
        print(f"❌ Error: Shortcode '{shortcode}' not found")
        return
    
    try:
        doc_ref.update({'enabled': False})
        print(f"✅ Disabled shortcode '{shortcode}'")
    except Exception as e:
        print(f"❌ Error disabling shortcode: {e}")

def get_stats(shortcode):
    """Get statistics for a short URL"""
    shortcode = shortcode.lower()
    doc_ref = db.collection('urls').document(shortcode)
    doc = doc_ref.get()
    
    if not doc.exists:
        print(f"❌ Error: Shortcode '{shortcode}' not found")
        return
    
    data = doc.to_dict()
    status = "🟢 Enabled" if data.get('enabled', False) else "🔴 Disabled"
    zip_indicator = "📦 Zip file" if is_zip_file(data['destination']) else "🔗 Link"
    
    print(f"📊 Stats for '{shortcode}':")
    print(f"   Status: {status}")
    print(f"   Type: {zip_indicator}")
    print(f"   Destination: {data['destination']}")
    print(f"   Total clicks: {data.get('clicks', 0)}")
    print(f"   Created: {data['created'].strftime('%Y-%m-%d %H:%M')}")
    print(f"   URL: https://go.ingwane.com/{shortcode}")

def list_urls():
    """List all short URLs"""
    try:
        docs = db.collection('urls').order_by('created', direction=firestore.Query.DESCENDING).stream()
        
        urls = []
        for doc in docs:
            data = doc.to_dict()
            urls.append({
                'shortcode': doc.id,
                'destination': data['destination'],
                'enabled': data.get('enabled', False),
                'clicks': data.get('clicks', 0),
                'created': data['created']
            })
        
        if not urls:
            print("📝 No URLs found")
            return
        
        print(f"📝 Found {len(urls)} shortcode(s):")
        print()
        
        for url in urls:
            status = "🟢" if url['enabled'] else "🔴"
            zip_indicator = "📦" if is_zip_file(url['destination']) else "🔗"
            created = url['created'].strftime('%Y-%m-%d')
            
            print(f"{status} {zip_indicator} {url['shortcode']}")
            print(f"   {url['destination']}")
            print(f"   Created: {created} | Clicks: {url['clicks']}")
            print()
            
    except Exception as e:
        print(f"❌ Error listing URLs: {e}")

def disable_all():
    """Disable all currently enabled URLs"""
    try:
        docs = db.collection('urls').where('enabled', '==', True).stream()
        
        disabled_count = 0
        for doc in docs:
            doc.reference.update({'enabled': False})
            disabled_count += 1
            print(f"✅ Disabled {doc.id}")
        
        if disabled_count == 0:
            print("📝 No enabled URLs found")
        else:
            print(f"✅ Disabled {disabled_count} shortcode(s)")
            
    except Exception as e:
        print(f"❌ Error disabling URLs: {e}")

def show_help():
    """Show help message"""
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
