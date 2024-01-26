class TimeEntry:
    id: int = None
    workspace_id: int = None
    description: str = None
    is_running: bool = None
    project_id: int = None

    def __init__(self, api_dto) -> None:
        self.id = api_dto["id"]
        self.workspace_id = api_dto["workspace_id"]
        self.description = api_dto["description"] or "<no description>"
        self.is_running = api_dto["stop"] == None
        self.project_id = api_dto["project_id"]