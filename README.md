# Async Billing System

This project is a debt processing system built with FastAPI, Celery, RabbitMQ, and Redis, designed to handle high-performance asynchronous tasks such as boleto generation and email notifications.

## Features

- **Upload CSV Files**: Upload a CSV file containing debt records for processing and uses Pandas for reading.
- **Asynchronous Task Processing**: Uses Celery to process tasks like boleto generation and email notifications.
- **Data Deduplication**: Ensures that debts are not processed more than once using Redis.
- **Task Monitoring**: Monitor task execution using Flower.
- **API Documentation**: Swagger-based documentation available for easy interaction with the API.
- **Pre-commit Linters**: Ensures code quality with tools like Black, isort, and Flake8 integrated into the pre-commit hooks.
- **Continuous Integration (CI)**: The repository is configured with CI to run linters, unit tests, and integration tests locally, ensuring only validated code can be pushed or merged into the main branch.

## Why Celery, RabbitMQ, and Redis?

- **Celery**: Manages asynchronous task execution efficiently, allowing the system to handle a large number of tasks without blocking the main application.
- **RabbitMQ**: Serves as the message broker, ensuring reliable communication between the FastAPI application and Celery workers.
- **Redis**: Used for task result backend and data deduplication, ensuring processed debts are tracked persistently.

## Getting Started

### Prerequisites

- Docker and Docker Compose installed on your system.

### Running the Application

1. Clone the repository:
   ```bash
   git clone https://github.com/xjpaulo/async-billing-system.git
   cd async-billing-system
   ```

2. Build and start the Docker containers:
   ```bash
   docker-compose up --build -d
   ```
   **Note:** You can set the concurrency level for the Celery app using the `CONCURRENCY` environment variable **before building the application**. For example: `export CONCURRENCY=4`. By default, the value is `CONCURRENCY=8`.  

   Alternatively, this variable can be set inside a `.env` file to be loaded automatically during runtime.

3. Access the application:
   - **API Base URL**: `http://localhost:8000`
   - **Swagger Documentation**: `http://localhost:8000/docs`
   - **ReDoc Documentation**: `http://localhost:8000/redoc`
   - **Flower Monitoring**: `http://localhost:5555`

### Monitoring Logs

To monitor the Celery worker logs:
```bash
docker-compose logs -f celery
```

To monitor the application logs:
```bash
docker-compose logs -f async_billing_app
```

### Using the API

#### Upload CSV File
To process a CSV file, use the following endpoint:
- **Endpoint**: `/upload_csv`
- **Method**: `POST`
- **Request**: Upload a CSV file with debt data.

Example using `curl`:
```bash
curl -X POST "http://localhost:8000/process-file" \
-H "accept: application/json" \
-H "Content-Type: multipart/form-data" \
-F "file=@path/to/your/file.csv"
```

#### Reset Progress
To reset the processing progress of a file, use the following endpoint:
- **Endpoint**: `/reset_progress`
- **Method**: `POST`
- **Request**: Provide the file name as a query parameter.

Example using `curl`:
```bash
curl -X POST "http://localhost:8000/reset_progress?file=your_file_name.csv" \
-H "accept: application/json"
```

Alternatively, use the Swagger UI at `http://localhost:8000/docs` to test the endpoint interactively.

### Pre-commit Hooks and Linters

This project uses pre-commit hooks to ensure code quality:
- **Black**: For code formatting.
- **isort**: For sorting imports.
- **Flake8**: For linting and identifying style issues.

To set up the pre-commit hooks, run:
```bash
pre-commit install
```

You can manually run the hooks using:
```bash
pre-commit run --all-files
```

## License

This project is licensed under the MIT License. See the LICENSE file for details.
