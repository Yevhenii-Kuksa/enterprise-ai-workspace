from typing import Any


class GoogleDriveApiGateway:
    def __init__(
        self,
        *,
        service: Any,
    ) -> None:
        self.service = service

    def list_files(
        self,
        *,
        page_size: int,
    ) -> list[dict[str, Any]]:
        response = (
            self.service.files()
            .list(
                pageSize=page_size,
                fields=(
                    "files("
                    "id,"
                    "name,"
                    "mimeType,"
                    "modifiedTime,"
                    "driveId,"
                    "webViewLink"
                    ")"
                ),
            )
            .execute()
        )

        files = response.get(
            "files",
            [],
        )

        return [
            dict(file_data)
            for file_data in files
        ]