class TimeEntry:
    def __init__(self, api_dto) -> None:
        self.description = api_dto["description"] or "<no description>"
        self.is_running = api_dto["stop"] == None
