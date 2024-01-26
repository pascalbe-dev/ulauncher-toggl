class TimeEntry:
    description = None

    def __init__(self, description) -> None:
        self.description = description or "<no description>"
