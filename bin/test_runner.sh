#!/bin/bash
# test_runner.sh - Script to run tests with emulator
echo "Setting up test environment..."

# Check if firestore emulator is available
if ! command -v gcloud &> /dev/null; then
    echo "Error: gcloud CLI not found. Please install Google Cloud SDK."
    exit 1
fi

# Install test dependencies
echo "Installing test dependencies..."
pip install -r requirements-test.txt

# Run tests
echo "Running tests with Firestore emulator..."
pytest tests/ \
    --cov=app \
    --cov-report=html \
    --cov-report=term-missing \
    --html=reports/test_report.html \
    --self-contained-html \
    -v

echo "Test results:"
echo "- Coverage report: htmlcov/index.html"
echo "- Test report: reports/test_report.html"

# Makefile - Common development tasks
.PHONY: test test-watch install-deps clean lint format

# Install all dependencies
install-deps:
	pip install -r requirements.txt
	pip install -r requirements-test.txt

# Run all tests
test:
	pytest tests/ -v

# Run tests with coverage
test-coverage:
	pytest tests/ --cov=app --cov-report=html --cov-report=term-missing

# Run tests and watch for changes
test-watch:
	pytest tests/ --cov=app -f

# Run specific test file
test-file:
	pytest tests/$(FILE) -v

# Run specific test
test-single:
	pytest tests/ -k "$(TEST)" -v

# Lint code
lint:
	flake8 app.py tests/
	pylint app.py

# Format code
format:
	black app.py tests/
	isort app.py tests/

# Clean up generated files
clean:
	rm -rf htmlcov/
	rm -rf reports/
	rm -rf .pytest_cache/
	rm -rf __pycache__/
	find . -name "*.pyc" -delete

# Start local development server
dev:
	export API_KEY=test-api-key-123 && \
	export LOCAL_DEV=1 && \
	python app.py

# Start with emulator
dev-emulator:
	export FIRESTORE_EMULATOR_HOST=localhost:8081 && \
	export API_KEY=test-api-key-123 && \
	export LOCAL_DEV=1 && \
	python app.py
