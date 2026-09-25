from pathlib import Path

from fastapi import UploadFile

from app.repositories.task_attachment_repository import (
    TaskAttachmentRepository,
)


ATTACHMENT_FOLDER = Path(
    "data/attachments"
)


class TaskAttachmentService:

    def __init__(
        self,
        repository: TaskAttachmentRepository,
    ):
        self.repository = repository

        ATTACHMENT_FOLDER.mkdir(
            parents=True,
            exist_ok=True,
        )

    def save_attachment(
        self,
        task_id: int,
        file: UploadFile,
    ):

        original_filename = Path(
            file.filename
        ).name

        stored_filename = (
            f"t{task_id}_{original_filename}"
        )

        file_path = (
            ATTACHMENT_FOLDER
            / stored_filename
        )

        with open(
            file_path,
            "wb",
        ) as output_file:

            while chunk := file.file.read(
                1024 * 1024
            ):
                output_file.write(chunk)

        return self.repository.create(
            task_id=task_id,
            original_filename=original_filename,
            stored_filename=stored_filename,
        )

    def get_task_attachments(
        self,
        task_id: int,
    ):
        return self.repository.get_by_task_id(
            task_id
        )

    def get_attachment(
        self,
        attachment_id: int,
    ):
        return self.repository.get_by_id(
            attachment_id
        )