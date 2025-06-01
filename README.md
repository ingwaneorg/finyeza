# finyeza - URL Forwarder

A secure, API-only URL shortener service built with Flask and Google Cloud Firestore.

## Features
- 🔗 Custom short URLs with manual shortcode entry
- 📦 Automatic zip file detection and download pages
- 📊 Click tracking and analytics
- 🔐 API key authentication for management
- 🚀 Zero-cost scaling with Google Cloud Run
- 💾 Firestore database for reliable storage

## Quick Start

### Local Development
```bash
pip install -r requirements.txt
export API_KEY="test-key-123"
export LOCAL_DEV=1
python app.py
```
Visit http://localhost:8080/health to verify service is running

### Deploy to Google Cloud Run
```bash
# Deploy with your API key
export API_KEY="your-secure-api-key"
./deploy.sh
```

## Project Structure
```
finyeza/
├── app.py                 # Main Flask application
├── shorturl.py           # Command line interface
├── requirements.txt       # Python dependencies  
├── deploy.sh             # Deployment script (keep local)
├── static/
│   └── app.css           # CSS styles
└── templates/
    ├── base.html         # Base template
    ├── 404.html          # Not found page
    └── download.html     # Download starting page
```

## Usage

### Command Line Interface
```bash
# Set your API key
export API_KEY="your-api-key"

# Create a short URL
python shorturl.py create project-files https://example.com/files.zip

# View click statistics
python shorturl.py stats project-files

# List all URLs
python shorturl.py list
```

### API Endpoints

All management endpoints require `X-API-Key` header.

**Create Short URL:**
```bash
curl -X POST https://go.ingwane.com/api/create \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"shortcode": "meeting-notes", "destination": "https://example.com/file.pdf"}'
```

**Get Statistics:**
```bash
curl https://go.ingwane.com/api/stats/meeting-notes \
  -H "X-API-Key: your-api-key"
```

**List All URLs:**
```bash
curl https://go.ingwane.com/api/list \
  -H "X-API-Key: your-api-key"
```

### User Access
Users simply visit `https://go.ingwane.com/{shortcode}` and get redirected automatically.

## Environment Variables

- `API_KEY` - Required for all management operations
- `LOCAL_DEV=1` - Use localhost:8080 for CLI tool during development
- `PORT` - Server port (default: 8080)

## Security Features

- API key authentication with constant-time comparison
- Input validation (shortcodes: letters, numbers, hyphens only)
- No public management interface
- Secure click tracking without exposing user data
- HTTPS enforced in production

## Analytics

Each short URL tracks:
- Total click count
- Individual click timestamps
- Source IP addresses (for basic analytics)
- User agent strings
- Automatic zip file detection

## Cost Optimization

- Scales to zero when not in use
- Minimal Firestore operations (2-3 per click)
- Efficient subcollection structure for click tracking
- Designed to stay within Google Cloud free tier:
  - Cloud Run: 2M requests/month
  - Firestore: 50K reads, 20K writes per day
- No continuous polling or background processes

## Database Structure

```
Firestore Collection: urls/
├── {shortcode}/
│   ├── destination: "https://..."
│   ├── created: timestamp
│   ├── clicks: number
│   ├── is_zip: boolean
│   └── clicks/ (subcollection)
│       └── {click_id}/
│           ├── timestamp: datetime
│           ├── ip: string
│           └── user_agent: string
```

---

**Note:** Keep your `deploy.sh` script local and never commit API keys to version control.
