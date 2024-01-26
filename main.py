import logging
from src.toggl_api import TogglApi
from src.time_entry import TimeEntry

from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.client.Extension import Extension
from ulauncher.api.shared.action.ExtensionCustomAction import \
    ExtensionCustomAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
from ulauncher.api.shared.action.RenderResultListAction import \
    RenderResultListAction
from ulauncher.api.shared.action.SetUserQueryAction import SetUserQueryAction
from ulauncher.api.shared.event import (ItemEnterEvent, KeywordQueryEvent,
                                        PreferencesEvent,
                                        PreferencesUpdateEvent)
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem

logger = logging.getLogger(__name__)


class TogglExtension(Extension):
    toggl_api = TogglApi()

    def __init__(self):
        super(TogglExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(PreferencesEvent, PreferencesEventListener())
        self.subscribe(PreferencesUpdateEvent,
                       PreferencesUpdateEventListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())

class KeywordQueryEventListener(EventListener):
    def on_event(self, event, extension: TogglExtension):
        try:
            if not extension.toggl_api.has_token_set():
                return RenderResultListAction([
                    ExtensionResultItem(icon='images/icon.png',
                                        name='No Toggl API token set',
                                        description='Please set the Toggl API token in the Ulauncher preferences.'
                    )
                ])

            current_time_entry = extension.toggl_api.get_current_time_entry()

            if current_time_entry is None:
                return RenderResultListAction([
                    ExtensionResultItem(icon='images/icon.png',
                                        name='No current time entry',
                                        description='Click this item to start a new time entry.'
                    )
                ])

            return RenderResultListAction([
                ExtensionResultItem(icon='images/icon.png',
                                    name='Entry "%s" running' % current_time_entry.description,
                                    description='Click this item to stop the current time entry.',
                                    on_enter=ExtensionCustomAction(current_time_entry, keep_app_open=True))
            ])
        except Exception as e:
            logger.error(e)
            return RenderResultListAction([
                ExtensionResultItem(icon='images/icon.png',
                                    name='Error in handling the keyword query.',
                                    description=str(e))
            ])

class ItemEnterEventListener(EventListener):
    def on_event(self, event, extension: TogglExtension):
        try:
            if isinstance(event.get_data(), TimeEntry):
                time_entry = event.get_data()
                extension.toggl_api.stop_time_entry(time_entry)
                message = 'Stopped time entry "%s"' % time_entry.description
                return RenderResultListAction([
                    ExtensionResultItem(icon='images/icon.png',
                                        name=message,
                                        description='Press enter to dismiss',
                                        on_enter=HideWindowAction()
                )])
        except Exception as e:
            logger.error(e)
            return RenderResultListAction([
                ExtensionResultItem(icon='images/icon.png',
                                    name='Error in handling the action.',
                                    description=str(e))
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
