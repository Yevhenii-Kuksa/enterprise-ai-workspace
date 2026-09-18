from typing import Any


class SharePointApiGateway:
    def __init__(
        self,
        *,
        client: Any,
        drive_id: str,
    ) -> None:
        self.client = client
        self.drive_id = drive_id

    def list_items(
        self,
        *,
        page_size: int,
    ) -> list[dict[str, Any]]:
        response = self.client.get(
            
                f"/drives/{self.drive_id}/root/children"
                f"?$top={page_size}"
            
        )

        items = response.get(
            "value",
            [],
        )

        return [
            dict(item)
            for item in items
        ]