class TimeEntry:
    def __init__(self, api_dto) -> None:
        self.id = api_dto["id"]
        self.workspace_id = api_dto["workspace_id"]
        self.description = api_dto["description"] or "<no description>"
        self.is_running = api_dto["stop"] == None
