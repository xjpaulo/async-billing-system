from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr


class DebtRecord(BaseModel):
    """
    Represents a debt record containing information about a debt.

    This class is used to model a debt, including the debtor's details,
    the amount of the debt, the due date, and a unique identifier.

    Attributes:
        name (str): The name of the debtor.
        governmentId (int): The government ID of the debtor.
        email (EmailStr): The email address of the debtor.
        debtAmount (int): The amount of the debt.
        debtDueDate (datetime): The due date for the debt.
        debtId (UUID): A unique identifier for the debt.
    """

    name: str
    governmentId: int
    email: EmailStr
    debtAmount: int
    debtDueDate: datetime
    debtId: UUID
