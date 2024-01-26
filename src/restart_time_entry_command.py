from src.time_entry import TimeEntry

class RestartTimeEntryCommand:
    def __init__(self, time_entry: TimeEntry):
        self.time_entry = time_entry