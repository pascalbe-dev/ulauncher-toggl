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

    def __init__(self):
        super(TogglExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(PreferencesEvent, PreferencesEventListener())
        self.subscribe(PreferencesUpdateEvent,
                       PreferencesUpdateEventListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())

    def get_current_entry(self):
        response = self.make_api_get_request("time_entries/current")
        entry = response["data"]
        if not entry:
            return None

        self.enrich_current_duration(entry)
        return entry

    def get_previous_timers(self):
        response = self.make_api_get_request("time_entries")
        distinct_entries = []
        for entry in response:
            if not any(existing_entry["description"] == entry["description"] for existing_entry in distinct_entries):
                distinct_entries.append(entry)

        return distinct_entries

    def start_entry(self, entry):
        request_payload = {
            "time_entry": {
                "description": entry["description"],
                "pid": entry["pid"],
                "created_with": "ULauncher Toggl Extension"
            }
        }
        response = self.make_api_post_request(
            "time_entries/start", request_payload)
        return response

    def stop_entry(self, entry_id):
        response = self.make_api_put_request(f"time_entries/{entry_id}/stop")
        return response

    def make_api_get_request(self, sub_url):
        url = TogglExtension.base_url + sub_url
        headers = {"Content-Type": "application/json"}
        response = requests.get(url, headers=headers,
                                auth=(self.token, "api_token")).json()
        return response

    def make_api_put_request(self, sub_url):
        url = TogglExtension.base_url + sub_url
        headers = {"Content-Type": "application/json"}
        response = requests.get(url, headers=headers,
                                auth=(self.token, "api_token")).json()
        return response

    def make_api_post_request(self, sub_url, payload):
        url = TogglExtension.base_url + sub_url
        headers = {"Content-Type": "application/json"}
        logger.debug(payload)
        response = requests.post(url, json=payload, headers=headers,
                                 auth=(self.token, "api_token")).json()
        return response

    def enrich_current_duration(self, current_entry):
        duration_attribute = current_entry["duration"]

        if duration_attribute < 0:
            current_time = int(time.time())
            duration = current_time + duration_attribute
        else:
            duration = duration_attribute

        if duration < 60:
            current_entry["displayable_duration"] = f"{duration} seconds"
        else:
            duration_in_mins = round(duration / 60)
            duration_extra_seconds = duration % 60
            current_entry["displayable_duration"] = f"{duration_in_mins} minutes, {duration_extra_seconds} seconds"


class KeywordQueryEventListener(EventListener):
    def on_event(self, event, extension):
        query = event.get_argument() or ""

        results = []
        if query:
            results = self.gen_latest_timers_results(query, extension)
        else:
            results = self.gen_current_timer_results(extension)

        return RenderResultListAction(results)

    def gen_current_timer_results(self, extension):
        current_timer = extension.get_current_entry()
        if not current_timer:
            return [self.gen_result_item("No timer running", "Type to start timer.", None)]

        stop_action = ExtensionCustomAction(
            {"action": "stop", "entry_id": current_timer["id"]})
        duration = current_timer["displayable_duration"]
        description = current_timer["description"]
        return [self.gen_result_item(f"{description} | {duration}.", "Select to stop. Type to start another.", stop_action)]

    def gen_latest_timers_results(self, query, extension):
        previous_timers = extension.get_previous_timers()
        filtered_previous_timers = [
            timer for timer in previous_timers if query.lower() in timer["description"].lower()]

        if not filtered_previous_timers:
            return [self.gen_result_item("No result found", "Nothing to do here right now.", None)]

        return [self.gen_result_item(timer["description"], "Select to start.",
                                     ExtensionCustomAction({"action": "start", "entry": timer})) for timer in filtered_previous_timers]

    def gen_result_item(self, name, description, action):
        action = action or HideWindowAction()
        return ExtensionResultItem(icon="images/icon.png", name=name, description=description, on_enter=action)


class ItemEnterEventListener(EventListener):
    def on_event(self, event, extension):
        event_data = event.get_data()
        action = event_data["action"]

        if action == "stop":
            entry_id = event_data["entry_id"]
            extension.stop_entry(entry_id)
        elif action == "start":
            entry = event_data["entry"]
            extension.start_entry(entry)


class PreferencesEventListener(EventListener):
    def on_event(self, event, extension):
        extension.token = event.preferences["api_token"]


class PreferencesUpdateEventListener(EventListener):
    def on_event(self, event, extension):
        if event.id == "api_token":
            extension.token = event.new_value


if __name__ == "__main__":
    TogglExtension().run()
