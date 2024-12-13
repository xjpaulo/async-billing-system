import pytest

from app.tasks.tasks import (
    all_tasks_done_task,
    generate_boleto,
    process_chunk_task,
    process_debt_task,
    send_email,
)


@pytest.fixture
def debt_data():
    return {
        "name": "Test user",
        "governmentId": 12345678900,
        "email": "test@example.com",
        "debtAmount": 1000,
        "debtDueDate": "2024-07-12",
        "debtId": "76403498-cffe-4c06-895e-f60ba27443b3",
    }


@pytest.fixture
def mock_services(mocker):
    mock_boleto_service = mocker.patch("app.tasks.tasks.BoletoService")
    mock_email_service = mocker.patch("app.tasks.tasks.EmailService")
    mock_logger = mocker.patch("app.tasks.tasks.logger")

    return mock_boleto_service, mock_email_service, mock_logger


def test_process_debt_task_success(mocker, debt_data, mock_services):
    mock_boleto_service, mock_email_service, mock_logger = mock_services

    result = process_debt_task(debt_data)
    assert result == "Processed Debt ID: 76403498-cffe-4c06-895e-f60ba27443b3"
    mock_boleto_service.return_value.generate_boleto.assert_called_once()
    mock_email_service.return_value.send_email.assert_called_once()
    mock_logger.info.assert_called_with(
        "Processed Debt ID: 76403498-cffe-4c06-895e-f60ba27443b3"
    )


def test_process_debt_task_failure(mocker, mock_services):
    mock_boleto_service, mock_email_service, mock_logger = mock_services

    invalid_data = {"email": "invalid_email"}
    result = process_debt_task(invalid_data)
    assert result.startswith("Error processing Debt ID")
    mock_logger.info.assert_called()


def test_process_chunk_task_success(mocker, mock_services):
    mock_boleto_service, mock_email_service, mock_logger = mock_services
    mock_redis_client = mocker.patch("app.tasks.tasks.redis_client")
    mock_process_debt_task = mocker.patch("app.tasks.tasks.process_debt_task")

    mock_redis_client.smembers.return_value = {"111"}
    mock_process_debt_task.return_value = (
        "Processed Debt ID: 76403498-cffe-4c06-895e-f60ba27443b3"
    )

    chunk_data = [
        {"debtId": "123", "email": "test@example.com", "debtAmount": 50.0},
        {
            "debtId": "111",
            "email": "already_processed@example.com",
            "debtAmount": 100.0,
        },
    ]

    result = process_chunk_task(chunk_data)
    assert len(result) == 1
    mock_logger.info.assert_called_with(
        "Finished processing chunk with 1 results"
    )


def test_process_chunk_task_failure(mocker, mock_services):
    mock_boleto_service, mock_email_service, mock_logger = mock_services
    mock_redis_client = mocker.patch("app.tasks.tasks.redis_client")

    mock_redis_client.smembers.side_effect = Exception("Redis error")
    chunk_data = [
        {"debtId": "123", "email": "test@example.com", "debtAmount": 50.0}
    ]
    with pytest.raises(Exception):
        process_chunk_task(chunk_data)
    mock_logger.error.assert_called()


def test_all_tasks_done_task_success(mocker, mock_services):
    mock_boleto_service, mock_email_service, mock_logger = mock_services

    results = [{"processed_debts": 2}, {"processed_debts": 3}]
    result = all_tasks_done_task(results)
    assert result["processed_count"] == 2
    assert result["total_debts"] == 5
    mock_logger.info.assert_any_call("Tasks completed: 2")
    mock_logger.info.assert_any_call("Total debts processed: 5")


def test_all_tasks_done_task_failure(mocker, mock_services):
    mock_boleto_service, mock_email_service, mock_logger = mock_services

    results = None
    result = all_tasks_done_task(results)
    assert result["processed_count"] == 0
    assert "error" in result
    mock_logger.error.assert_called()


def test_generate_boleto(mocker, mock_services):
    mock_boleto_service, mock_email_service, mock_logger = mock_services

    debt = {"debtId": "123"}
    generate_boleto(debt)
    mock_logger.info.assert_called_with("Generating boleto for Debt ID: 123")


def test_send_email(mocker, mock_services):
    mock_boleto_service, mock_email_service, mock_logger = mock_services

    send_email("test@example.com", "Test message")
    mock_logger.info.assert_called_with(
        "Sending email to: test@example.com with message: Test message"
    )
