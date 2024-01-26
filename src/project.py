class Project:
    id: int = None
    name: str = None
    is_active: bool = None

    def __init__(self, api_dto) -> None:
        self.id = api_dto["id"]
        self.name = api_dto["name"]
        self.is_active = api_dto["active"] == True
