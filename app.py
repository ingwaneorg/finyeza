from flask import Flask, request, redirect, render_template, jsonify
from google.cloud import firestore
import os
import logging
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)

# Initialize Firestore client
db = firestore.Client(database='finyeza')

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def is_zip_file(url):
    """Check if URL points to a zip file"""
    return url.lower().endswith('.zip')

def get_client_ip():
    """Get client IP address, handling proxies"""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    return request.remote_addr

@app.route('/<shortcode>')
def redirect_url(shortcode):
    """Redirect to destination URL and track click"""
    # Normalize shortcode to lowercase for lookup
    shortcode = shortcode.lower()
    
    doc_ref = db.collection('urls').document(shortcode)
    doc = doc_ref.get()
    
    if not doc.exists:
        return render_template('404.html', shortcode=shortcode), 404
    
    data = doc.to_dict()
    
    # Check if link is enabled
    if not data.get('enabled', False):
        return render_template('disabled.html', shortcode=shortcode), 403
    
    destination = data['destination']
    
    # Track the click (simple increment)
    try:
        doc_ref.update({'clicks': firestore.Increment(1)})
        logger.info(f"Click tracked: {shortcode} -> {destination}")
    except Exception as e:
        logger.error(f"Error tracking click: {e}")
        # Continue with redirect even if tracking fails
    
    # Handle zip files with download page
    if is_zip_file(destination):
        return render_template('download.html', destination=destination, shortcode=shortcode)
    
    # Regular redirect
    return redirect(destination, code=302)

@app.route('/health')
def health_check():
    """Simple health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'finyeza-url-forwarder'})

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
