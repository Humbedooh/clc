from __future__ import annotations
import os
import typing


class ServerConfig:
    def __init__(self, subyaml: dict):
        self.ip: str = subyaml.get("bind", "0.0.0.0")
        self.port: int = int(subyaml.get("port", 8080))
        self.traceback: bool = bool(subyaml.get("traceback", False))


class TaskConfig:
    def __init__(self, subyaml: dict):
        self.refresh_rate: int = int(subyaml.get("refresh_rate", 150))
        assert self.refresh_rate >= 10, "Refresh rate must be at least 10 seconds!"


class OAuthConfig:
    def __init__(self, subyaml: dict):
        self.authoritative_domains: typing.List[str] = subyaml.get("authoritative_domains", [])
        self.admins: typing.List[str] = subyaml.get("admins", "").split(" ")


class DirectoryConfig:
    def __init__(self, subyaml: dict):
        self.scratch = subyaml.get("scratch", "scratch")
        assert os.path.isdir(self.scratch), f"Scratch dir {self.scratch} could not be found, please create it or change clc.yaml!"


class Configuration:
    def __init__(self, yml: dict):
        self.server: ServerConfig = ServerConfig(yml.get("server", {}))
        self.tasks: TaskConfig = TaskConfig(yml.get("tasks", {}))
        self.oauth: OAuthConfig = OAuthConfig(yml.get("oauth", {}))
        self.dirs: DirectoryConfig = DirectoryConfig(yml.get("directories", {}))
        self.words = yml.get("words", [])
        self.excludes = yml.get("excludes", [])


class InterData:
    """
        A mix of various global variables used throughout processes
    """

    def __init__(self):
        self.repositories: list = []
        self.sessions: dict = {}
        self.people: list = []
        self.projects: dict = {}
        self.project_queue: list = []
        self.activity: str = "Idling..."
