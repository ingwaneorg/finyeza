# Test Suite for Finyeza URL Forwarder

This directory contains comprehensive tests for the Finyeza URL shortener service.

## 🧪 Test Structure

```
tests/
├── conftest.py          # Pytest fixtures and configuration
├── test_api.py          # Core API endpoint tests
├── test_stats.py        # Statistics and analytics tests
├── test_integration.py  # End-to-end workflow tests
├── test_edge_cases.py   # Edge cases and error handling
├── test_performance.py  # Performance and load tests
├── test_security.py     # Security and input validation tests
└── README.md            # This file
```

## 🚀 Quick Start

### Prerequisites
- Google Cloud SDK installed with Firestore emulator
- Python dependencies installed

### Run All Tests
```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

### Using Make Commands
```bash
make test              # Run all tests
make test-coverage     # Run with coverage report
make test-watch        # Run tests on file changes
make test-single TEST=test_create_url_success  # Run specific test
```

## 📊 Test Categories

### **Unit Tests** (`test_api.py`, `test_stats.py`)
- Test individual API endpoints
- Input validation and error handling
- Authentication and authorization
- **Fast execution** - run these frequently during development

### **Integration Tests** (`test_integration.py`)
- Complete user workflows
- Multiple component interaction
- Data flow validation
- **Marked with** `@pytest.mark.integration`

### **Edge Case Tests** (`test_edge_cases.py`)
- Boundary conditions
- Malformed inputs
- Concurrent access scenarios
- URL format variations

### **Performance Tests** (`test_performance.py`)
- Bulk operations
- Response time validation
- Load simulation
- **Marked with** `@pytest.mark.slow`

### **Security Tests** (`test_security.py`)
- Input sanitization
- Timing attack resistance
- Authentication bypass attempts
- XSS and injection prevention

## 🔧 Pytest Features

### **Fixtures** (`conftest.py`)
- **`firestore_emulator`** - Manages Firestore emulator lifecycle
- **`db`** - Provides clean database per test
- **`client`** - Flask test client for HTTP requests
- **`api_headers`** - Authenticated request headers

### **Parametrized Tests**
```python
@pytest.mark.parametrize("shortcode,expected", [
    ("Simple", "simple"),
    ("UPPERCASE", "uppercase"),
    ("MiXeD-CaSe", "mixed-case"),
])
def test_shortcode_normalization(client, api_headers, shortcode, expected):
    # Test case normalization with multiple inputs
```

### **Test Markers**
```bash
pytest tests/ -m "not slow"      # Skip performance tests
pytest tests/ -m integration     # Run only integration tests
pytest tests/ -m "unit or edge"  # Run multiple marker types
```

### **Coverage Reporting**
- **HTML Report**: `htmlcov/index.html`
- **Terminal Output**: Shows missing lines
- **XML Export**: For CI/CD integration

## 🛠️ Test Environment

### **Firestore Emulator**
Tests use the Google Cloud Firestore emulator for:
- **Isolated testing** - No impact on production data
- **Repeatable tests** - Fresh database per test
- **Fast execution** - Local emulator vs cloud calls
- **Offline capability** - No internet required

### **Test Data Isolation**
- Each test gets a **clean database**
- **Automatic cleanup** after each test
- **No test interference** - tests can run in parallel
- **Predictable state** - no hidden dependencies

## 📋 Test Execution Examples

### **Development Workflow**
```bash
# Quick feedback during development
pytest tests/test_api.py::TestCreateURL::test_create_url_success -v

# Run all unit tests (fast)
pytest tests/ -m "not slow" 

# Full test suite before commit
pytest tests/ --cov=app --cov-report=term-missing
```

### **CI/CD Pipeline**
```bash
# Full test suite with reports
pytest tests/ \
    --cov=app \
    --cov-report=html \
    --cov-report=xml \
    --html=reports/test_report.html
```

### **Performance Analysis**
```bash
# Run only performance tests
pytest tests/ -m slow -v

# Run with timing information
pytest tests/ --durations=10
```

## 🔍 Debugging Tests

### **Verbose Output**
```bash
pytest tests/ -v -s  # Show print statements and detailed output
```

### **Specific Test Debugging**
```bash
pytest tests/test_api.py::TestCreateURL::test_create_url_success -v -s --pdb
```

### **Coverage Analysis**
```bash
# See which lines aren't covered
pytest tests/ --cov=app --cov-report=term-missing

# Generate HTML report for detailed analysis
pytest tests/ --cov=app --cov-report=html
open htmlcov/index.html
```
