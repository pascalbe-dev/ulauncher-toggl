from src.ulauncher_option import UlauncherOption
from typing import List

from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction

class UlauncherApi:
    def output_options(self, options: List[UlauncherOption]) -> None:
        return RenderResultListAction([
            ExtensionResultItem(icon='images/icon.png',
                                name=option.title,
                                description=option.description,
                                on_enter=option.action or None)
            for option in options
        ])