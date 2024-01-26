from __future__ import annotations
from typing import List

from src.project import Project


class TimeEntry:
    id: int = None
    workspace_id: int = None
    description: str = None
    is_running: bool = None
    project_id: int = None
    project: Project = None

    def __init__(self, api_dto) -> None:
        self.id = api_dto["id"]
        self.workspace_id = api_dto["workspace_id"]
        self.description = api_dto["description"] or "<no description>"
        self.is_running = api_dto["stop"] == None
        self.project_id = api_dto["project_id"]

    def __repr__(self) -> str:
        prefix = "[" + self.project.name + "] " if self.project else ""
        return prefix + self.description

    def enrich_project(self, all_projects: List[Project]) -> TimeEntry:
        project = next((project for project in all_projects if project.id == self.project_id), None)
        self.project = project or None
        return self