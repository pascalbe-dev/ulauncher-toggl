from typing import List
import requests
from datetime import datetime, timezone

from src.time_entry import TimeEntry
from src.project import Project

class TogglApi:
    token = None
    base_url = "https://api.track.toggl.com/api/v9/"

    workspace_id: int = None
    projects: List[Project] = []
    recent_time_entries: List[TimeEntry] = []

    def set_token(self, token):
        self.token = token
        self.get_and_store_user_details()

    def has_token_set(self):
        return self.token != None and len(self.token) > 31

    def get_and_store_user_details(self):
        response = requests.get(self.base_url + "me?with_related_data=true", auth=(self.token, "api_token"))
        if response.status_code != 200:
            raise Exception("Could not get data from Toggl: " + response.status_code)

        self.workspace_id = response.json()["default_workspace_id"]
        self.projects = [Project(project) for project in response.json()["projects"]]
        self.recent_time_entries = [TimeEntry(time_entry).enrich_project(self.projects) for time_entry in response.json()["time_entries"]]

    def get_workspace_id(self) -> int:
        return self.workspace_id

    def get_current_time_entry(self) -> TimeEntry:
        self.get_and_store_user_details()
        return next((time_entry for time_entry in self.recent_time_entries if time_entry.is_running), None)

    def stop_time_entry(self, time_entry: TimeEntry) -> None:
        response = requests.patch(self.base_url + "workspaces/" + str(time_entry.workspace_id) + "/time_entries/" + str(time_entry.id) + "/stop", auth=(self.token, "api_token"))
        if response.status_code != 200:
            raise Exception("Could not stop time entry: " + response.text)

    def start_time_entry(self, description: str, project_id: int = None) -> None:
        workspace_id = self.get_workspace_id()
        response = requests.post(self.base_url + "workspaces/" + str(workspace_id) + "/time_entries", auth=(self.token, "api_token"), json={
            "workspace_id": workspace_id,
            "project_id": project_id or None,
            "description": description,
            "created_with": "ulauncher-toggl",
            "start": datetime.now(timezone.utc).isoformat(),
            "duration": -1,
            "tags": ["by:ulauncher-toggl"]
        })
        if response.status_code != 200:
            raise Exception("Could not start time entry: " + response.text)

    def get_recent_time_entries(self, filter: str = "") -> List[TimeEntry]:
        return set([time_entry for time_entry in self.recent_time_entries if not time_entry.is_running and filter.lower() in time_entry.description.lower()])

    def restart_time_entry(self, time_entry: TimeEntry) -> None:
        self.start_time_entry(time_entry.description, time_entry.project_id)


