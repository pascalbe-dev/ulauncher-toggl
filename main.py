import logging

from src.toggl_api import TogglApi
from src.time_entry import TimeEntry
from src.ulauncher_api import UlauncherApi
from src.ulauncher_option import UlauncherOption

from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.client.Extension import Extension
from ulauncher.api.shared.event import (ItemEnterEvent, KeywordQueryEvent,
                                        PreferencesEvent,
                                        PreferencesUpdateEvent)

from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction

logger = logging.getLogger(__name__)

class TogglExtension(Extension):
    toggl_api = TogglApi()
    ulauncher_api = UlauncherApi()

    def __init__(self):
        super(TogglExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(PreferencesEvent, PreferencesEventListener())
        self.subscribe(PreferencesUpdateEvent,PreferencesUpdateEventListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())

class KeywordQueryEventListener(EventListener):
    def on_event(self, event, extension: TogglExtension):
        try:
            if not extension.toggl_api.has_token_set():
                return extension.ulauncher_api.output_options([
                    UlauncherOption(
                        title='No Toggl API token set',
                        description='Please set the Toggl API token in the Ulauncher preferences.',
                    )
                ])

            if event.get_argument() is not None:
                new_time_entry_description = event.get_argument()
                return extension.ulauncher_api.output_options([
                    UlauncherOption(
                        title='Start time entry "%s"' % new_time_entry_description,
                        description='Hit enter to start this time entry.',
                        action=ExtensionCustomAction(new_time_entry_description, keep_app_open=True)
                    )
                ])

            current_time_entry = extension.toggl_api.get_current_time_entry()

            if current_time_entry is None:
                return extension.ulauncher_api.output_options([
                    UlauncherOption(
                        title='No current time entry',
                        description='Start writing to start a new time entry.',
                    )
                ])
            return extension.ulauncher_api.output_options([
                UlauncherOption(
                    title='Current "%s"' % str(current_time_entry),
                    description='Click this item to stop the current time entry or start writing to start another one.',
                    action=ExtensionCustomAction(current_time_entry, keep_app_open=True)
                )
            ])
        except Exception as e:
            logger.error(e)
            return extension.ulauncher_api.output_options([
                UlauncherOption(
                    title='Error in handling the keyword query',
                    description=str(e),
                )
            ])

class ItemEnterEventListener(EventListener):
    def on_event(self, event, extension: TogglExtension):
        try:
            if isinstance(event.get_data(), TimeEntry):
                time_entry = event.get_data()
                extension.toggl_api.stop_time_entry(time_entry)

                return extension.ulauncher_api.output_options([
                    UlauncherOption(
                        title='Stopped "%s"' % str(time_entry),
                        description='Press enter to dismiss or start writing to start a new time entry.',
                        action=HideWindowAction()
                    )
                ])
            if isinstance(event.get_data(), str):
                new_time_entry_description = event.get_data()
                extension.toggl_api.start_time_entry(new_time_entry_description)

                return extension.ulauncher_api.output_options([
                    UlauncherOption(
                        title='Started time entry "%s"' % new_time_entry_description,
                        description='Press enter to dismiss',
                        action=HideWindowAction()
                    )
                ])
        except Exception as e:
            logger.error(e)
            return extension.ulauncher_api.output_options([
                UlauncherOption(
                    title='Error in handling the item enter event',
                    description=str(e),
                )
            ])

class PreferencesEventListener(EventListener):
    def on_event(self, event, extension):
        extension.keyword = event.preferences["keyword"]
        extension.toggl_api.set_token(event.preferences["api_token"])

class PreferencesUpdateEventListener(EventListener):
    def on_event(self, event, extension):
        if event.id == "api_token":
            extension.toggl_api.set_token(event.new_value)

if __name__ == "__main__":
    TogglExtension().run()
