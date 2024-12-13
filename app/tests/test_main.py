from io import BytesIO

import pytest
from fastapi.testclient import TestClient

from app.main import web_app


@pytest.fixture
def client():
    return TestClient(web_app)


@pytest.fixture
def mock_redis(mocker):
    return mocker.patch("app.main.redis_client")


@pytest.fixture
def mock_celery(mocker):
    return mocker.patch("app.main.chord")


def create_csv_file(content: str) -> BytesIO:
    file = BytesIO()
    file.write(content.encode())
    file.seek(0)
    return file


def test_upload_invalid_file_type(client, mock_redis, mock_celery):
    file = create_csv_file("Name,Age\nJohn,30\nDoe,25")
    response = client.post(
        "/upload_csv", files={"file": ("test.txt", file, "text/plain")}
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "File must be a CSV"}


def test_upload_empty_file(client, mock_redis, mock_celery):
    file = create_csv_file("")
    response = client.post(
        "/upload_csv", files={"file": ("empty.csv", file, "text/csv")}
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Uploaded file is empty"}


def test_upload_no_new_rows(client, mock_redis, mock_celery):
    file_content = "name,governmentId\nJohn,100\nDoe,200"
    file = create_csv_file(file_content)

    mock_redis.hget.return_value = "3"
    mock_redis.hset.return_value = None

    response = client.post(
        "/upload_csv", files={"file": ("test.csv", file, "text/csv")}
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "No new rows to process"}


def test_upload_csv_success(client, mock_redis, mock_celery):
    file_content = "name,governmentId\nJohn,100\nDoe,200"
    file = create_csv_file(file_content)

    mock_redis.hget.return_value = "0"
    mock_redis.hset.return_value = None

    mock_celery.return_value.id = "task_id"
    mock_celery.return_value.get.return_value = (
        "Processing completed successfully"
    )

    response = client.post(
        "/upload_csv", files={"file": ("test.csv", file, "text/csv")}
    )

    assert response.status_code == 200
    assert response.json() == {"message": "File processing started"}


def test_upload_csv_internal_error(client, mock_redis, mock_celery):
    file_content = "Name,Age\nJohn,30\nDoe,25"
    file = create_csv_file(file_content)

    mock_redis.hget.side_effect = Exception("Internal error")

    response = client.post(
        "/upload_csv", files={"file": ("test.csv", file, "text/csv")}
    )

    assert response.status_code == 500
    assert response.json() == {"detail": "Internal server error"}


def test_reset_progress_success(client, mock_redis):
    mock_redis.hdel.return_value = 1

    response = client.post("/reset_progress?file_name=test.csv")

    assert response.status_code == 200
    assert response.json() == {
        "message": "Progress for test.csv has been reset."
    }


def test_reset_progress_failure(client, mock_redis):
    mock_redis.hdel.side_effect = Exception("Redis error")

    response = client.post("/reset_progress?file_name=test.csv")

    assert response.status_code == 500
    assert response.json() == {"detail": "Failed to reset progress"}
