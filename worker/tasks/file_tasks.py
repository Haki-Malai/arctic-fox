from worker import celery
from api.app import db, aws_wrapper
from database.models import File
import logging

logging.basicConfig(level=logging.INFO)


@celery.task(name='worker.tasks.file_tasks.set_dominant_color', bind=True, max_retries=3)
def set_dominant_color(self, file_id: int) -> None:
    """Set the dominant color of a file.

    :param file_id: The ID of the file.
    """
    try:
        file = db.session.get(File, file_id)
        if not file:
            logging.error(f'File with ID {file_id} not found')
            self.retry(countdown=2)
            return

        dominant_color = aws_wrapper.generate_dominant_color(file.filename)
        if dominant_color:
            file.dominant_color = dominant_color
        else:
            file.error = 'Could not generate dominant color'
            logging.error(f'Error in generating dominant color for file ID {file_id}')
            self.retry(countdown=2)

        db.session.commit()
    except Exception as e:
        logging.error(f'An error occurred with file ID {file_id}: {str(e)}')
        db.session.rollback()


@celery.task(name='worker.tasks.file_tasks.delete_s3_file', bind=True, max_retries=3)
def delete_s3_file(self, filename: str) -> None:
    """Delete a file from S3.

    :param filename: The name of the file.
    """
    try:
        aws_wrapper.delete_file_from_s3(filename)
    except Exception as e:
        logging.error(f'An error occurred with file {filename}: {str(e)}')
        self.retry(countdown=2)
