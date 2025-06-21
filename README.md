# finyeza - URL Forwarder

A simple, secure URL shortener designed for educational file distribution. Built with Flask and Google Cloud Firestore.

## Features
- 🔗 Custom short URLs with enable/disable functionality
- 📦 Download pages for zip files
- 📊 Basic click tracking
- 🚀 Zero-cost scaling with Google Cloud Run
- 💾 Firestore database for reliable storage
- 🔄 Separate dev/prod databases

## Use Case

Perfect for educators who need to:
- Share course files with short, memorable URLs
- Control access timing (enable on Sunday, disable on Friday)
- Avoid giving permanent access to cloud storage URLs
- Track basic usage statistics

## Quick Start

### Prerequisites
- Google Cloud project with Firestore enabled
- Service account with appropriate permissions
- Python 3.11+ with virtual environment

### Local Development
```bash
# Set up environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure for development
export FIRESTORE_DB="finyeza-dev"
export FLASK_DEBUG="true"
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account-key.json"

# Run locally
python app.py
```

### Deploy to Google Cloud Run
```bash
# Configure for production
export SECRET_KEY="your-flask-secret-key"

# Deploy
./deploy.sh
```

## Project Structure
```
finyeza/
├── app.py                # Main Flask application
├── shorturl.py           # Command line interface
├── requirements.txt      # Python dependencies  
├── Dockerfile            # Container configuration
├── deploy.sh             # Deployment script
├── static/
│   └── app.css           # CSS styles
└── templates/
    ├── base.html         # Base template
    ├── 404.html          # Not found page
    ├── disabled.html     # Link disabled page
    └── download.html     # Download starting page
```

## Usage

### Command Line Interface

```bash
# Create a short URL (disabled by default)
python shorturl.py create test https://www.example.com/test1

# Enable for current week
python shorturl.py enable test

# Check status
python shorturl.py list
python shorturl.py stats test

# Disable after teaching
python shorturl.py disable test

# Disable all active links (Friday cleanup)
python shorturl.py disable-all
```

### Weekly Workflow

**Start of term:**
```bash
# Create all module shortcuts once
python shorturl.py create test1 https://example.com/test1
python shorturl.py create test2 https://example.com/test2
python shorturl.py create test3 https://example.com/test3
```

**Each week:**
```bash
# Sunday night - enable current week
python shorturl.py enable test1

# Friday afternoon - disable current week
python shorturl.py disable test1
# Or disable everything: python shorturl.py disable-all
```

### Student Access
Students simply visit `https://your-domain.com/test1` and either:
- Get redirected to download page (for zip files)
- Get redirected directly (for other links)
- See "Link Not Available" message (if disabled)

## Environment Variables

### Development
- `FIRESTORE_DB` - Database name (default: `finyeza`, dev: `finyeza-dev`)
- `FLASK_DEBUG` - Enable debug mode (`true`/`false`)
- `GOOGLE_APPLICATION_CREDENTIALS` - Path to service account key

### Production
- `SECRET_KEY` - Flask secret key (for deployment)
- `PORT` - Server port (default: 8080)

## Database Structure

```
Firestore Collection: urls/
├── {shortcode}/
│   ├── destination: "https://..."
│   ├── enabled: boolean
│   ├── created: timestamp
│   ├── updated: timestamp
│   └── clicks: number
```

Simple and efficient - no complex subcollections or detailed tracking.

## Security Features

- No public management interface (CLI only)
- Input validation for shortcodes
- Enable/disable functionality for access control
- Separate dev/prod databases
- Service account authentication

## Cost Optimization

- Scales to zero when not in use (Cloud Run)
- Minimal Firestore operations (1-2 per click)
- Designed to stay within Google Cloud free tier
- Simple database structure for efficiency

## Commands Reference

| Command               | Description                    |
|-----------------------|--------------------------------|
| `create <code> <url>` | Create new shortcode (disabled)|
| `update <code> <url>` | Update shortcode distination   |
| `enable <code>`       | Enable shortcode               |
| `disable <code>`      | Disable shortcode              |
| `disable-all`         | Disable all enabled shortcodes |
| `list`                | Show all shortcodes with status|
| `stats <code>`        | Show statistics for shortcode  |
| `help`                | Show help message              |

## Development vs Production

**Development:**
```bash
export FIRESTORE_DB="finyeza-dev"
export FLASK_DEBUG="true"
python shorturl.py create test123 https://example.com/test.zip
```

**Production:**
```bash
# No env vars = production defaults
python shorturl.py create test https://example.com/test
```

---
