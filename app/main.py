from pathlib import Path

import pandas as pd
import uvicorn
from celery import chord
from celery.exceptions import TimeoutError
from fastapi import BackgroundTasks, FastAPI, HTTPException, UploadFile

from app.config.settings import CHUNK_SIZE, FILE_PROGRESS_KEY
from app.tasks.tasks import all_tasks_done_task, process_chunk_task
from app.utils.logger import logger
from app.utils.redis_client import redis_client

web_app = FastAPI()


def validate_csv_file(file: UploadFile) -> Path:
    """
    Validate and save the uploaded CSV file.

    This function checks if the uploaded file is a valid CSV
    and saves it to a temporary location.
    If the file is invalid or empty, an HTTPException is raised.

    :param file: The uploaded file object to be validated and saved.
    :return: Path to the saved temporary file.
    :raises HTTPException: If the file is not a valid CSV or is empty.
    """
    if file.content_type != "text/csv":
        raise HTTPException(status_code=400, detail="File must be a CSV")

    temp_file = Path("temp_file.csv")
    with open(temp_file, "wb") as buffer:
        buffer.write(file.file.read())

    if temp_file.stat().st_size == 0:
        temp_file.unlink()
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    return temp_file


@web_app.post("/upload_csv")
async def upload_csv(
    file: UploadFile, background_tasks: BackgroundTasks
) -> dict:
    """
    Upload and process a CSV file in chunks.

    This endpoint allows the user to upload a CSV file. The file is validated,
    and its contents are processed in chunks. Each chunk is handled
    by a background task, and progress is tracked using Redis. Once all
    chunks are processed, a final task is triggered to summarize the results.

    :param file: The uploaded CSV file to be processed.
    :param background_tasks: FastAPI background task manager to handle
    asynchronous tasks.
    :return: A message indicating that the file processing has started.
    :raises HTTPException: If there is an error in file validation
    or processing.
    """
    try:
        temp_file = validate_csv_file(file)

        last_processed_line = (
            redis_client.hget(FILE_PROGRESS_KEY, file.filename) or 0
        )
        total_lines = sum(1 for _ in open(temp_file))

        if int(last_processed_line) >= total_lines:
            raise HTTPException(
                status_code=400, detail="No new rows to process"
            )

        subtasks = []
        for i, chunk in enumerate(
            pd.read_csv(
                temp_file,
                chunksize=CHUNK_SIZE,
                skiprows=int(last_processed_line),
            )
        ):
            chunk_data = chunk.to_dict(orient="records")
            subtasks.append(process_chunk_task.s(chunk_data))

            redis_client.hset(
                FILE_PROGRESS_KEY,
                file.filename,
                int(last_processed_line) + (i + 1) * CHUNK_SIZE,
            )

        def trigger_chord():
            try:
                result = chord(subtasks)(all_tasks_done_task.s())
                logger.info(f"Process result ID: {result.id}")
                try:
                    final_result = result.get(timeout=60)
                    logger.info(
                        f"Process completed successfully.: {final_result}"
                    )
                except TimeoutError:
                    logger.warning("Process timed out after 60 seconds.")
                    partial_results = result.collect()
                    processed_count = len(partial_results)
                    logger.info(f"Partial tasks completed: {processed_count}")
                    result.revoke(terminate=True)
                    raise TimeoutError(
                        "Processing exceeded the time limit of 60 seconds."
                    )
            except Exception as e:
                logger.error(f"Process failed with error: {e}")

        background_tasks.add_task(trigger_chord)

        return {"message": "File processing started"}
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@web_app.post("/reset_progress")
async def reset_progress(file_name: str) -> dict:
    """
    Reset the processing progress of a file.

    This endpoint allows the user to reset the progress of a specific file
    that is being processed. The progress is tracked using Redis, and calling
    this function removes the associated progress data.

    :param file_name: The name of the file for which the progress should
    be reset.
    :return: A message indicating the progress has been successfully reset.
    :raises HTTPException: If an error occurs while resetting the progress.
    """
    try:
        redis_client.hdel(FILE_PROGRESS_KEY, file_name)
        return {"message": f"Progress for {file_name} has been reset."}
    except Exception as e:
        logger.error(f"Error resetting progress for {file_name}: {e}")
        raise HTTPException(status_code=500, detail="Failed to reset progress")


if __name__ == "__main__":
    uvicorn.run(web_app, host="0.0.0.0", port=8000)
