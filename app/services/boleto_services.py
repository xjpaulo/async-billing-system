from app.models import DebtRecord
from app.services.interfaces import IBoletoService
from app.utils.logger import logger


class BoletoService(IBoletoService):
    """
    Service class for handling boleto generation.

    Inherits from the IBoletoService interface and provides the implementation
    of the boleto generation process. This method simulates the generation
    of a boleto
    for a specific debt record.

    Methods:
        generate_boleto(debt: DebtRecord) -> None:
            Simulates the generation of a boleto for the provided debt record.
            Logs an informational message with the debt ID.
    """

    def generate_boleto(self, debt: DebtRecord) -> None:
        """
        Simulates the generation of a boleto for a given debt record.

        This method logs an informational message indicating that the boleto
        generation has been simulated for the specific debt identified by the
        provided debt ID.

        Args:
            debt (DebtRecord): The debt record containing information about
            the debt, including the debt ID.

        Returns:
            None
        """
        logger.info(f"Simulating boleto generation for Debt ID: {debt.debtId}")
