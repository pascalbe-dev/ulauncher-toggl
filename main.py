import logging
import time

import requests
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.client.Extension import Extension
from ulauncher.api.shared.action.ExtensionCustomAction import \
    ExtensionCustomAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
from ulauncher.api.shared.action.RenderResultListAction import \
    RenderResultListAction
from ulauncher.api.shared.event import (ItemEnterEvent, KeywordQueryEvent,
                                        PreferencesEvent,
                                        PreferencesUpdateEvent)
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem

logger = logging.getLogger(__name__)


class TogglExtension(Extension):

    base_url = "https://api.track.toggl.com/api/v8/"
    project_map = {}
    existing_time_entries = []

    def __init__(self):
        super(TogglExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(PreferencesEvent, PreferencesEventListener())
        self.subscribe(PreferencesUpdateEvent,
                       PreferencesUpdateEventListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())

    def fill_cache(self):
        projects = self.get_projects()

        self.project_map = dict(
            (project["id"], project["name"]) for project in projects)

        self.existing_time_entries = self.get_existing_time_entries()

    def get_project_name(self, project_id):
        return self.project_map[project_id]

    def get_projects(self):
        workspaces = self.api_get_request("workspaces")
        selected_workspace = workspaces[0]
        selected_workspace_id = selected_workspace["id"]

        projects = self.api_get_request(
            f"workspaces/{selected_workspace_id}/projects")
        return projects

    def get_current_time_entry(self):
        current_time_entry = self.api_get_request("time_entries/current")
        time_entry = current_time_entry["data"]
        if not time_entry:
            return None

        self.enrich_with_current_duration(time_entry)
        self.enrich_with_project(time_entry)
        return time_entry

    def get_existing_time_entries(self):
        time_entries = self.api_get_request("time_entries")
        distinct_time_entries = []
        for entry in time_entries:
            if not any(existing_entry["description"] == entry["description"] for existing_entry in distinct_time_entries):
                self.enrich_with_project(entry)
                distinct_time_entries.append(entry)

        return distinct_time_entries

    def start_existing_time_entry(self, time_entry):
        request_payload = {
            "time_entry": {
                "description": time_entry["description"],
                "pid": time_entry["pid"],
                "created_with": "ULauncher Toggl Extension"
            }
        }
        self.api_post_request(
            "time_entries/start", request_payload)

    def stop_time_entry(self, time_entry_id):
        self.api_put_request(f"time_entries/{time_entry_id}/stop")

    def api_get_request(self, sub_url):
        url = TogglExtension.base_url + sub_url
        headers = {"Content-Type": "application/json"}
        response = requests.get(url, headers=headers,
                                auth=(self.token, "api_token")).json()
        return response

    def api_put_request(self, sub_url):
        url = TogglExtension.base_url + sub_url
        headers = {"Content-Type": "application/json"}
        response = requests.get(url, headers=headers,
                                auth=(self.token, "api_token")).json()
        return response

    def api_post_request(self, sub_url, payload):
        url = TogglExtension.base_url + sub_url
        headers = {"Content-Type": "application/json"}
        logger.debug(payload)
        response = requests.post(url, json=payload, headers=headers,
                                 auth=(self.token, "api_token")).json()
        return response

    def enrich_with_project(self, time_entry):
        time_entry.update(
            {"project": self.get_project_name(time_entry["pid"])})

    def enrich_with_current_duration(self, current_time_entry):
        duration_attribute = current_time_entry["duration"]

        if duration_attribute < 0:
            current_time = int(time.time())
            duration = current_time + duration_attribute
        else:
            duration = duration_attribute

        if duration < 60:
            current_time_entry["displayable_duration"] = f"{duration} seconds"
        else:
            duration_in_mins = round(duration / 60)
            duration_extra_seconds = duration % 60
            current_time_entry["displayable_duration"] = f"{duration_in_mins} minutes, {duration_extra_seconds} seconds"


class KeywordQueryEventListener(EventListener):
    def on_event(self, event, extension):
        query = event.get_argument() or ""

        results = []
        if query:
            results = self.gen_existing_time_entries_results(query, extension)
        else:
            results = self.gen_current_time_entry_results(extension)

        return RenderResultListAction(results)

    def gen_current_time_entry_results(self, extension):
        timer = extension.get_current_time_entry()
        if not timer:
            return [self.gen_result_item("No timer running", "Type to start timer.", None)]

        stop_action = ExtensionCustomAction(
            {"action": "stop", "entry_id": timer["id"]})
        duration = timer["displayable_duration"]
        description = timer["description"]
        project = timer["project"]
        return [self.gen_result_item(f"{description} | {duration}.",
                                     f"Project: {project}",
                                     stop_action)]

    def gen_existing_time_entries_results(self, query, extension):
        filtered_existing_time_entries = [
            time_entry for time_entry in extension.existing_time_entries
            if query.lower() in time_entry["description"].lower()]

        if not filtered_existing_time_entries:
            return [self.gen_result_item("No result found", "Nothing to do here right now.", None)]

        return [self.gen_result_item(time_entry["description"],
                                     "Project: " + time_entry["project"],
                                     ExtensionCustomAction({"action": "start", "entry": time_entry}))
                for time_entry in filtered_existing_time_entries]

    def gen_result_item(self, name, description, action):
        action = action or HideWindowAction()
        return ExtensionResultItem(icon="images/icon.png", name=name, description=description, on_enter=action)


class ItemEnterEventListener(EventListener):
    def on_event(self, event, extension):
        event_data = event.get_data()
        action = event_data["action"]

        if action == "stop":
            time_entry_id = event_data["entry_id"]
            extension.stop_time_entry(time_entry_id)
        elif action == "start":
            time_entry = event_data["entry"]
            extension.start_existing_time_entry(time_entry)


class PreferencesEventListener(EventListener):
    def on_event(self, event, extension):
        extension.token = event.preferences["api_token"]
        extension.fill_cache()


class PreferencesUpdateEventListener(EventListener):
    def on_event(self, event, extension):
        if event.id == "api_token":
            extension.token = event.new_value
            extension.fill_cache()


if __name__ == "__main__":
    TogglExtension().run()
