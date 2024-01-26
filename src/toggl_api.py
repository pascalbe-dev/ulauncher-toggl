import requests
from datetime import datetime, timezone

from src.time_entry import TimeEntry

class TogglApi:
    token = None
    base_url = "https://api.track.toggl.com/api/v9/"

    def set_token(self, token):
        self.token = token

    def has_token_set(self):
        return self.token != None and len(self.token) > 31

    def get_current_time_entry(self) -> TimeEntry:
        response = requests.get(self.base_url + "me/time_entries", auth=(self.token, "api_token"))
        if response.status_code != 200:
            raise Exception("Could not get current time entry: " + response.text)

        time_entry_dtos = response.json()
        if len(time_entry_dtos) == 0:
            return None

        time_entries = [TimeEntry(time_entry) for time_entry in time_entry_dtos]
        return next((time_entry for time_entry in time_entries if time_entry.is_running), None)

    def stop_time_entry(self, time_entry: TimeEntry) -> None:
        response = requests.patch(self.base_url + "workspaces/" + str(time_entry.workspace_id) + "/time_entries/" + str(time_entry.id) + "/stop", auth=(self.token, "api_token"))
        if response.status_code != 200:
            raise Exception("Could not stop time entry: " + response.text)

    def start_time_entry(self, description: str) -> None:
        workspace_id = 2719602
        creator = "ulauncher-toggl"
        response = requests.post(self.base_url + "workspaces/" + str(workspace_id) + "/time_entries", auth=(self.token, "api_token"), json={
            "workspace_id": workspace_id,
            "description": description,
            "created_with": creator,
            "start": datetime.now(timezone.utc).isoformat(),
            "duration": -1,
            "tags": ["by:" + creator]
        })
        if response.status_code != 200:
            raise Exception("Could not start time entry: " + response.text)
