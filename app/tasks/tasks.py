from celery import shared_task

from app.celery import app
from app.config.settings import PROCESSED_DEBTS_KEY
from app.models import DebtRecord
from app.services.boleto_services import BoletoService
from app.services.email_services import EmailService
from app.utils.logger import logger
from app.utils.redis_client import redis_client


@shared_task(queue="debt_queue")
def process_debt_task(debt_data) -> str:
    """
    Processes a single debt by generating a boleto and
    sending an email notification.

    This function is executed as an asynchronous task and
    performs the following steps:
    1. Creates a `DebtRecord` from the provided debt data.
    2. Generates a boleto (payment slip) for the debt.
    3. Sends an email to the debtor with details about the boleto.

    If any error occurs during the process, it logs an error message.

    Args:
        debt_data (dict): A dictionary containing the debt
        details, such as the debt ID, amount, due date, and debtor's email.

    Returns:
        str: A message indicating whether the debt was
        successfully processed or if there was an error.
    """
    try:
        debt = DebtRecord(**debt_data)
        boleto_service = BoletoService()
        boleto_service.generate_boleto(debt)
        email_service = EmailService()
        email_service.send_email(
            debt.email,
            f"Your boleto with the debt uuid {debt.debtId} "
            f"and value {debt.debtAmount} is ready.",
        )
        result = f"Processed Debt ID: {debt.debtId}"
    except Exception as e:
        result = (
            f"Error processing Debt ID"
            f" {debt_data.get('debtId', 'Unknown')}: {e}"
        )
    logger.info(result)
    return result


@shared_task(queue="debt_queue")
def process_chunk_task(chunk_data) -> list:
    """
    Processes a chunk of debt data by filtering out already
    processed debts and handling new ones.

    This function performs the following steps:
    1. Retrieves the set of already processed debts from Redis.
    2. Filters the provided chunk of debt data to exclude debts that
    have already been processed.
    3. Processes the remaining debts by invoking the
    `process_debt_task` function.
    4. Adds the processed debts to the Redis set to prevent
    future processing.
    5. Returns a list of results indicating whether each debt was
    successfully processed.

    Args:
        chunk_data (list): A list of dictionaries, each containing debt
        details (e.g., debt ID, amount, etc.).

    Returns:
        list: A list of messages indicating success or failure
        for each debt in the chunk.
    """
    try:
        processed_debts = redis_client.smembers(PROCESSED_DEBTS_KEY)
        processed_debts = {id for id in processed_debts}

        debts_to_process = [
            debt
            for debt in chunk_data
            if str(debt["debtId"]) not in processed_debts
        ]

        logger.info(f"Processing {len(debts_to_process)} new debts")

        results = []
        for record in debts_to_process:
            result = process_debt_task(record)
            redis_client.sadd(PROCESSED_DEBTS_KEY, record["debtId"])
            results.append(result)

        logger.info(f"Finished processing chunk with {len(results)} results")
        return results
    except Exception as e:
        logger.error(f"Error processing chunk data: {e}")
        raise


@shared_task(queue="default")
def all_tasks_done_task(results) -> dict:
    """
    Callback task that is triggered after all chunk processing
    tasks are complete.

    This function processes the results from completed chunk tasks
    to generate a summary of the task execution. It calculates the number
    of completed tasks and the total number of processed debts.

    Args:
        results (list): A list of results from the completed chunk tasks.
        Each result is expected to contain a dictionary with information
        on the number of processed debts.

    Returns:
        dict: A dictionary containing the following keys:
              - "processed_count": The number of chunk tasks that have
              been completed.
              - "total_debts": The total number of debts processed across
              all chunk tasks.
              - "error" (optional): An error message, if any
              exception occurred during the task execution.
    """
    try:
        processed_count = len(results)

        total_processed_debts = sum(
            result.get("processed_debts", 0)
            for result in results
            if isinstance(result, dict)
        )

        logger.info(f"Tasks completed: {processed_count}")
        logger.info(f"Total debts processed: {total_processed_debts}")

        return {
            "processed_count": processed_count,
            "total_debts": total_processed_debts,
        }
    except Exception as e:
        logger.error(f"Error in all_tasks_done_task: {e}")
        return {"processed_count": 0, "total_debts": 0, "error": str(e)}


@app.task(queue="boleto_queue")
def generate_boleto(debt: dict) -> None:
    """
    Simulate the creation of a boleto for a given debt ID.

    This function logs the simulated generation of a boleto for a debt.
    It uses the provided debt data to simulate the boleto creation process.

    Args:
        debt (dict): A dictionary containing the debt data. Expected to
        include the debt ID and other relevant information
        for boleto generation.
    """
    logger.info(f"Generating boleto for Debt ID: {debt['debtId']}")


@app.task(queue="email_queue")
def send_email(email: str, message: str) -> None:
    """
    Simulate the process of sending an email.

    This function logs the simulated sending of an email with the provided
    message to the specified email address.

    Args:
        email (str): The email address to which the message will be sent.
        message (str): The message content, typically containing
        information like debt amount and debt ID for the boleto.
    """
    logger.info(f"Sending email to: {email} with message: {message}")
