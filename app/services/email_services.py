from pydantic import EmailStr

from app.services.interfaces import IEmailService
from app.utils.logger import logger


class EmailService(IEmailService):
    """
    Service class for handling email sending.

    Inherits from the IEmailService interface and provides the implementation
    for sending emails. This method simulates the process of sending an
    email to a specified recipient with a given message.

    Methods:
        send_email(email: EmailStr, message: str) -> None:
            Simulates the sending of an email to the provided email address
            with the specified message.
    """

    def send_email(self, email: EmailStr, message: str) -> None:
        """
        Simulates sending an email to the given email address with
        the specified message.

        This method logs an informational message indicating that an
        email has been sent to the provided email address with
        the given message.

        Args:
            email (EmailStr): The recipient's email address.
            message (str): The message to be sent in the email.

        Returns:
            None
        """
        logger.info(
            f"Simulating email sent to: {email} with message: {message}"
        )
