# Belvo Challenge - Invoice Anomaly Detection

A Streamlit application for detecting anomalies in invoice data using AI-powered analysis. The application extracts invoice data, identifies anomalies using OpenAI's GPT models, and provides detailed financial analysis.

## 🚀 Features

- **Invoice Data Extraction**: Extract and filter invoice data by date range and type
- **Anomaly Detection**: AI-powered detection of unusual patterns in invoice amounts
- **Financial Analysis**: Detailed analysis of detected anomalies with insights and recommendations
- **Interactive Dashboard**: Streamlit-based web interface with visualizations
- **Docker Support**: Containerized deployment ready for cloud platforms
- **CI/CD Pipeline**: Automated testing and deployment with GitHub Actions

## 📋 Prerequisites

- Python 3.12+
- Poetry (for dependency management)
- Docker (optional, for containerized deployment)
- OpenAI API key
- LangSmith API key (optional, for tracing)

## 🛠️ Setup

### 1. Environment Setup

We recommend using Conda or Pyenv for Python version management:

```bash
# Using Conda
conda create --name belvo-env python=3.12
conda activate belvo-env

# Using Pyenv
pyenv install 3.12.11
pyenv virtualenv 3.12.11 belvo-env
pyenv activate belvo-env
```

### 2. Install Poetry

```bash
pip install poetry
```

### 3. Install Dependencies

```bash
poetry install
```

### 4. Environment Variables

Copy the example environment file and configure your API keys:

```bash
cp .env.example .env
```

Edit `.env` with your actual values:

```bash
# Belvo Configuration
CLIENT_ID=
CLIENT_SECRET=
BASE_URL=

# OpenAI Configuration
OPENAI_API_KEY=

# LangSmith Configuration (Optional)
LANGSMITH_TRACING=
LANGSMITH_ENDPOINT=
LANGSMITH_API_KEY=
LANGSMITH_PROJECT=
```

### 5. Pre-commit Hooks (Recommended)

Set up pre-commit hooks for code quality:

```bash
make pre-commit-install
```

## 🏃‍♂️ Running the Application

### Local Development

```bash
# Run the Streamlit app
streamlit run app/streamlit_app.py

# Or using Poetry
poetry run streamlit run app/streamlit_app.py
```

The application will be available at `http://localhost:8501`

### Using Docker

**Important**: Make sure you have your OpenAI API key configured in your `.env` file before running with Docker.

```bash
# Build the Docker image
make build

# Run the container (recommended - uses .env file)
make run-env

# Alternative: Run with manual environment variables
make run
```

**Manual Docker commands** (if you prefer not to use make):

```bash
# Build the Docker image
docker build -t belvo-challenge .

# Run the container with .env file
docker run -p 8501:8501 --env-file .env belvo-challenge

# Run with specific OpenAI API key
docker run -p 8501:8501 -e OPENAI_API_KEY="your_api_key_here" belvo-challenge
```

## 🧪 Testing

### Run All Tests

```bash
make test
```

### Run Tests with Coverage

```bash
pytest tests/ --cov=app --cov-report=html
```

### Run Specific Test Files

```bash
pytest tests/test_invoices_extractor.py -v
```

## 🔧 Development Tools

The project includes several Makefile commands for development:

### Code Quality

```bash
# Run all quality checks (format, lint, tests)
make quality-check

# Format code with black and isort
make format

# Check code formatting
make format-check

# Run linting with flake8
make lint

# Run pre-commit hooks
make pre-commit-run
```

### Available Make Commands

- `make test` - Run all tests
- `make format` - Format code with black and isort
- `make format-check` - Check if code is properly formatted
- `make lint` - Run flake8 linting
- `make quality-check` - Run all quality checks
- `make pre-commit-install` - Install pre-commit hooks
- `make pre-commit-run` - Run pre-commit hooks on all files

### Docker Commands

- `make build` - Build Docker image
- `make run` - Run container with OpenAI API key
- `make run-env` - Run container with .env file
- `make run-bg` - Run container in background
- `make stop` - Stop running container
- `make logs` - View container logs
- `make clean` - Remove container

## 🏗️ Project Structure

```
belvo/
├── app/
│   ├── agents/
│   │   ├── models/
│   │   │   ├── detection_output.py
│   │   │   ├── invoice_type.py
│   │   │   ├── invoice_type_input.py
│   │   │   └── invoice_type_output.py
│   │   ├── anomaly_detector.py
│   │   └── financial_analysis_agent.py
│   ├── extractors/
│   │   └── invoices_extractor.py
│   └── streamlit_app.py
├── scripts/
│   ├── etl_invoices.py
│   └── etl_transactions.py
├── services/
│   ├── belvo_service.py
│   ├── fiscal_mx_service.py
│   ├── ofda_service.py
│   └── employment_records_mx_service.py
├── notebooks/
│   └── (EDA and analysis notebooks)
├── tests/
│   └── test_invoices_extractor.py
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── deploy-heroku.yml
├── Dockerfile
├── heroku.yml
├── pyproject.toml
├── Makefile
├── .env.example
├── .flake8
├── .pre-commit-config.yaml
└── README.md
```

## 📊 Data Analysis Infrastructure

The project includes specialized folders for data extraction and analysis that support the EDA (Exploratory Data Analysis) workflows:

### 📁 `scripts/` - Data Extraction Scripts

Contains ETL (Extract, Transform, Load) scripts that fetch data from Belvo APIs and prepare it for analysis:

- **`etl_invoices.py`**: Extracts invoice data from Fiscal MX API
  - Fetches paginated invoice data for specified link IDs
  - Processes and cleans invoice information
  - Exports data to CSV format for notebook analysis

- **`etl_transactions.py`**: Extracts transaction data from OFDA API
  - Retrieves bank transaction data with pagination
  - Handles data transformation and cleaning
  - Saves processed data for financial analysis

### 🔧 `services/` - API Service Layer

Provides a clean abstraction layer for interacting with Belvo APIs:

- **`belvo_service.py`**: Base service class with authentication
  - Handles Belvo API authentication and headers
  - Provides common functionality for all Belvo services

- **`fiscal_mx_service.py`**: Mexican fiscal data service
  - Specialized methods for invoice data retrieval
  - Handles Fiscal MX API endpoints and pagination

- **`ofda_service.py`**: Open Finance Data API service
  - Transaction data extraction from banking APIs
  - Manages OFDA-specific data formats and structures

- **`employment_records_mx_service.py`**: Employment records service
  - Extracts Mexican employment and payroll data
  - Supports employment history analysis

### 📓 `notebooks/` - Exploratory Data Analysis

The data extracted by the `scripts/` using the `services/` layer is consumed by Jupyter notebooks for:

- **Data exploration and visualization**
- **Statistical analysis and pattern detection**
- **Feature engineering for anomaly detection**
- **Model development and testing**
- **Business insights and reporting**

### 🔄 Data Flow

```
Belvo APIs → services/ → scripts/ → CSV files → notebooks/ → EDA & Analysis
```

This architecture separates concerns and allows for:
- **Reusable API clients** in the `services/` layer
- **Automated data extraction** via `scripts/`
- **Interactive analysis** in `notebooks/`
- **Production-ready anomaly detection** in the main `app/`

## 🚀 CI/CD Pipeline

The project includes automated CI/CD with GitHub Actions:

### Continuous Integration (`ci.yml`)

- **Triggers**: Push/PR to `develop` and `master` branches
- **Actions**:
  - Install dependencies with Poetry
  - Run code formatting checks (black, isort)
  - Run linting (flake8)
  - Execute all tests

### Deployment (`deploy-heroku.yml`)

- **Triggers**: Push to `master` branch (after CI passes)
- **Actions**:
  - Build Docker image
  - Deploy to Heroku using Docker + Heroku API
  - Automatic rollback on failure

### Required GitHub Secrets

For deployment to work, configure these secrets in your GitHub repository:

- `HEROKU_API_KEY`: Your Heroku API key
- `HEROKU_APP_NAME`: Your Heroku app name
- `HEROKU_EMAIL`: Your Heroku account email

## 🐳 Docker Deployment

### Local Docker Build

**Using Make commands (recommended)**:

```bash
# Build the image
make build

# Run with environment file
make run-env

# Run in background
make run-bg

# View logs
make logs

# Stop container
make stop
```

**Manual Docker commands**:

```bash
docker build -t belvo-challenge .
docker run -p 8501:8501 --env-file .env belvo-challenge
```

**Available Docker Make Commands**:

- `make build` - Build the Docker image
- `make run` - Run container with OpenAI API key from environment
- `make run-env` - Run container with full .env file
- `make run-bg` - Run container in background
- `make run-dev` - Run container with data volume mount for development
- `make stop` - Stop the running container
- `make logs` - View container logs
- `make shell` - Access container shell
- `make clean` - Remove container
- `make clean-all` - Remove container and image

### Heroku Deployment

The application is configured for Heroku deployment with:

- `heroku.yml`: Heroku build configuration
- `Dockerfile`: Multi-stage build for production
- Dynamic port configuration via `$PORT` environment variable

## 🔍 Usage

1. **Configure Date Range**: Select start and end dates for invoice analysis
2. **Choose Invoice Type**: Select INFLOW or OUTFLOW invoices
3. **Detect Anomalies**: Click "Detect Anomalies" to analyze the data
4. **View Results**: Review detected anomalies in the interactive chart
5. **Analyze Anomalies**: Select specific anomalies for detailed AI analysis

## 🛡️ Code Quality

The project enforces code quality through:

- **Black**: Code formatting (120 char line length)
- **isort**: Import sorting
- **flake8**: Linting and style checks
- **pre-commit**: Automated checks on commit
- **pytest**: Comprehensive test coverage

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Install pre-commit hooks: `make pre-commit-install`
4. Make your changes and ensure tests pass: `make quality-check`
5. Commit your changes: `git commit -m 'Add amazing feature'`
6. Push to the branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Troubleshooting

### Common Issues

1. **Poetry Installation Issues**:
   ```bash
   pip install --upgrade pip
   pip install poetry
   ```

2. **Environment Variable Issues**:
   - Ensure `.env` file exists and contains all required variables
   - Check that API keys are valid and have proper permissions

3. **Docker Issues**:
   - Ensure Docker is running
   - Check that port 8501 is not already in use

4. **Test Failures**:
   - Run `make quality-check` to identify issues
   - Ensure all dependencies are installed: `poetry install`

For additional help, please open an issue in the GitHub repository.
