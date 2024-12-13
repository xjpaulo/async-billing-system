from datetime import datetime
from uuid import uuid4

import pytest

from app.models import DebtRecord
from app.services.boleto_services import BoletoService
from app.services.email_services import EmailService
from app.utils.logger import logger


@pytest.fixture
def mock_logger(mocker):
    mock_info = mocker.patch.object(logger, "info", autospec=True)
    yield mock_info


def test_generate_boleto(mock_logger):
    debt = DebtRecord(
        name="Test User",
        governmentId=12345678900,
        email="test@example.com",
        debtAmount=1000,
        debtDueDate=datetime(2023, 12, 31),
        debtId=uuid4(),
    )

    boleto_service = BoletoService()
    boleto_service.generate_boleto(debt)

    mock_logger.assert_called_once_with(
        f"Simulating boleto generation for Debt ID: {debt.debtId}"
    )


def test_send_email(mock_logger):
    email = "test@example.com"
    message = "This is a test email"

    email_service = EmailService()
    email_service.send_email(email, message)

    mock_logger.assert_called_once_with(
        f"Simulating email sent to: {email} with message: {message}"
    )
