from typing import Optional


class UlauncherOption:
    def __init__(self, title: str, description: Optional[str] = None, action: Optional[callable] = None) -> None:
        self.title = title
        self.description = description
        self.action = action