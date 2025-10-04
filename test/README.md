# Stock Market Analyzer - Testing Framework

This document describes the comprehensive testing framework for the Stock Market Analyzer project.

## Test Structure

The test suite is organized into multiple categories:

- `test_models.py`: Unit tests for data models (Stock, Transaction, PortfolioItem, etc.)
- `test_dse_api.py`: Tests for DSE API service and data fetching
- `test_data_manager.py`: Tests for data persistence and management
- `test_config.py`: Tests for configuration management
- `test_ui_components.py`: Tests for UI components (Dashboard, StockSelector, etc.)
- `test_auth_service.py`: Tests for authentication service
- `test_session_manager.py`: Tests for session management
- `test_app.py`: Tests for the main application
- `test_integration.py`: Integration tests and edge cases

## Running Tests

### Prerequisites
Make sure all dependencies are installed:
```bash
pip install -r requirements.txt
pip install pytest pytest-cov
```

### Running All Tests
```bash
python run_tests.py
# or
python -m pytest test/ -v
```

### Running Specific Test Suites
```bash
# Run unit tests only
python run_tests.py unit

# Run integration tests
python run_tests.py integration

# Run model-specific tests
python run_tests.py models

# Run API service tests
python run_tests.py api

# Run UI component tests
python run_tests.py ui

# Check coverage
python run_tests.py coverage
```

### Using Pytest Directly
```bash
# Run all tests with verbose output
pytest test/ -v

# Run tests with coverage
pytest test/ --cov=src --cov-report=html

# Run specific test file
pytest test/test_models.py

# Run tests with specific marker
pytest -m unit
pytest -m integration
pytest -m api

# Run tests in parallel (install pytest-xdist first)
pytest -n auto test/
```

## Test Categories

### Unit Tests
Located in individual test files, these test individual components in isolation using mocks.

### Integration Tests
Located in `test_integration.py`, these test how multiple components work together.

### API Tests
Test the DSE API service and its ability to fetch and parse data from the DSE website.

### Model Tests
Test data models to ensure proper serialization, deserialization, and calculations.

### UI Tests
Test the initialization and basic functionality of UI components.

## Test Coverage

The test suite aims for at least 50% coverage of the source code. Coverage reports are generated automatically when running tests.

## Writing Tests

When adding new functionality, please follow these guidelines:

1. Add unit tests for new models in `test_models.py`
2. Add service tests in the appropriate service test file
3. Add integration tests in `test_integration.py`
4. Use pytest fixtures where appropriate
5. Follow the existing test patterns
6. Ensure tests are isolated and don't depend on external services when possible

## Continuous Integration

The test suite is designed to run in a CI environment. All tests should pass before merging changes.

## Troubleshooting

If tests fail due to missing dependencies:
```bash
pip install pytest pytest-cov python-dotenv
```

If Redis is not available during tests, some functionality may be skipped. The tests handle this gracefully.

For detailed information about a failing test:
```bash
pytest test/test_file.py::TestClass::test_method -v -s
```