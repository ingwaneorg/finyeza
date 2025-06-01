from flask import Flask, request, redirect, render_template, jsonify
from google.cloud import firestore
import os
import logging
from datetime import datetime
import hashlib
import hmac

# Initialize Flask app
app = Flask(__name__)

# Initialize Firestore client
db = firestore.Client()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get API key from environment variable
API_KEY = os.environ.get('API_KEY')
if not API_KEY:
    logger.warning("API_KEY environment variable not set")

def verify_api_key(provided_key):
    """Verify API key using constant-time comparison"""
    if not API_KEY or not provided_key:
        return False
    return hmac.compare_digest(API_KEY, provided_key)

def is_zip_file(url):
    """Check if URL points to a zip file"""
    return url.lower().endswith('.zip')

def get_client_ip():
    """Get client IP address, handling proxies"""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    return request.remote_addr

@app.route('/api/create', methods=['POST'])
def create_short_url():
    """Create a new short URL (API key required)"""
    # Check API key
    api_key = request.headers.get('X-API-Key')
    if not verify_api_key(api_key):
        return jsonify({'error': 'Invalid or missing API key'}), 401
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'JSON data required'}), 400
    
    shortcode = data.get('shortcode', '').strip()
    destination = data.get('destination', '').strip()
    
    if not shortcode or not destination:
        return jsonify({'error': 'Both shortcode and destination are required'}), 400
    
    # Validate shortcode format (letters, numbers, hyphens only)
    if not all(c.isalnum() or c == '-' for c in shortcode):
        return jsonify({'error': 'Shortcode can only contain letters, numbers, and hyphens'}), 400
    
    # Check if shortcode already exists
    doc_ref = db.collection('urls').document(shortcode)
    if doc_ref.get().exists:
        return jsonify({'error': 'Shortcode already exists'}), 409
    
    # Create new URL record
    url_data = {
        'destination': destination,
        'created': datetime.utcnow(),
        'clicks': 0,
        'is_zip': is_zip_file(destination)
    }
    
    try:
        doc_ref.set(url_data)
        logger.info(f"Created short URL: {shortcode} -> {destination}")
        
        return jsonify({
            'shortcode': shortcode,
            'destination': destination,
            'short_url': f"https://go.ingwane.com/{shortcode}",
            'created': url_data['created'].isoformat()
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating URL: {e}")
        return jsonify({'error': 'Failed to create short URL'}), 500

@app.route('/api/stats/<shortcode>')
def get_stats(shortcode):
    """Get click statistics for a short URL (API key required)"""
    # Check API key
    api_key = request.headers.get('X-API-Key')
    if not verify_api_key(api_key):
        return jsonify({'error': 'Invalid or missing API key'}), 401
    
    doc_ref = db.collection('urls').document(shortcode)
    doc = doc_ref.get()
    
    if not doc.exists:
        return jsonify({'error': 'Shortcode not found'}), 404
    
    data = doc.to_dict()
    
    # Get recent clicks from subcollection
    clicks_ref = doc_ref.collection('clicks').order_by('timestamp', direction=firestore.Query.DESCENDING).limit(100)
    recent_clicks = []
    
    for click in clicks_ref.stream():
        click_data = click.to_dict()
        recent_clicks.append({
            'timestamp': click_data['timestamp'].isoformat(),
            'ip': click_data.get('ip', 'unknown')
        })
    
    return jsonify({
        'shortcode': shortcode,
        'destination': data['destination'],
        'created': data['created'].isoformat(),
        'total_clicks': data['clicks'],
        'is_zip': data.get('is_zip', False),
        'recent_clicks': recent_clicks
    })

@app.route('/api/list')
def list_urls():
    """List all short URLs (API key required)"""
    # Check API key
    api_key = request.headers.get('X-API-Key')
    if not verify_api_key(api_key):
        return jsonify({'error': 'Invalid or missing API key'}), 401
    
    try:
        urls = []
        docs = db.collection('urls').order_by('created', direction=firestore.Query.DESCENDING).stream()
        
        for doc in docs:
            data = doc.to_dict()
            urls.append({
                'shortcode': doc.id,
                'destination': data['destination'],
                'created': data['created'].isoformat(),
                'clicks': data['clicks'],
                'is_zip': data.get('is_zip', False)
            })
        
        return jsonify({'urls': urls})
        
    except Exception as e:
        logger.error(f"Error listing URLs: {e}")
        return jsonify({'error': 'Failed to list URLs'}), 500

@app.route('/<shortcode>')
def redirect_url(shortcode):
    """Redirect to destination URL and track click"""
    doc_ref = db.collection('urls').document(shortcode)
    doc = doc_ref.get()
    
    if not doc.exists:
        return render_template('404.html', shortcode=shortcode), 404
    
    data = doc.to_dict()
    destination = data['destination']
    is_zip = data.get('is_zip', False)
    
    # Track the click
    try:
        # Increment click counter
        doc_ref.update({'clicks': firestore.Increment(1)})
        
        # Add click record to subcollection
        click_data = {
            'timestamp': datetime.utcnow(),
            'ip': get_client_ip(),
            'user_agent': request.headers.get('User-Agent', 'unknown')
        }
        doc_ref.collection('clicks').add(click_data)
        
        logger.info(f"Click tracked: {shortcode} -> {destination}")
        
    except Exception as e:
        logger.error(f"Error tracking click: {e}")
        # Continue with redirect even if tracking fails
    
    # Handle zip files with download page
    if is_zip:
        return render_template('download.html', destination=destination, shortcode=shortcode)
    
    # Regular redirect
    return redirect(destination, code=302)

@app.route('/health')
def health_check():
    """Simple health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'url-forwarder'})

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
