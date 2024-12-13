from abc import ABC, abstractmethod

from pydantic import EmailStr

from app.models import DebtRecord


class IBoletoService(ABC):
    """
    Abstract base class for the BoletoService.

    Defines the interface for a service responsible for
    generating boletos (payment slips)
    based on debt records. Implementing classes must provide
    the logic for boleto generation.

    Methods:
        generate_boleto(debt: DebtRecord):
            Generates a boleto for the given debt record.
    """

    @abstractmethod
    def generate_boleto(self, debt: DebtRecord):
        """
        Generates a boleto for the given debt record.

        Args:
            debt (DebtRecord): The debt record containing information
            such as debt amount, debtor details, and due date.

        Raises:
            NotImplementedError: If this method is not implemented
            in a subclass.
        """
        pass


class IEmailService(ABC):
    """
    Abstract base class for the EmailService.

    Defines the interface for a service responsible for sending emails.
    Implementing classes must provide the logic for email sending.

    Methods:
        send_email(email: EmailStr, message: str):
            Sends an email with the specified message to the provided
            email address.
    """

    @abstractmethod
    def send_email(self, email: EmailStr, message: str):
        """
        Sends an email with the specified message to the provided
        email address.

        Args:
            email (EmailStr): The email address to which the message
            will be sent.
            message (str): The content of the email message.

        Raises:
            NotImplementedError: If this method is not implemented in
            a subclass.
        """
        pass
