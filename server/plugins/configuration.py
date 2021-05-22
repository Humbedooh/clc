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

class DebugConfig:
    def __init__(self, subyaml: dict):
        self.print_issues = subyaml.get('print_issues', True)


class Project:
    def __init__(self, path):
        self.repo = path.split("/")[-1]
        self.mtimes = {}
        self.settings = {}
        self.history = []
        self.issues = []
        self.issues_per_file = {}


class Configuration:
    def __init__(self, yml: dict, dyml: dict):
        self.server: ServerConfig = ServerConfig(yml.get("server", {}))
        self.tasks: TaskConfig = TaskConfig(yml.get("tasks", {}))
        self.oauth: OAuthConfig = OAuthConfig(yml.get("oauth", {}))
        self.dirs: DirectoryConfig = DirectoryConfig(yml.get("directories", {}))
        self.debug: DebugConfig = DebugConfig(yml.get("debug", {}))
        self.words = dyml.get("words", [])
        self.excludes = dyml.get("excludes", [])
        self.excludes_context = dyml.get("excludes_context", [])
        self.contexts = dyml.get("contexts", [])
        self.executables = yml.get("executables", {})
        assert "git" in self.executables and os.path.exists(self.executables["git"]), \
            "This service requires the git executable installed. If it is already installed, " \
            "please let me know where to find it in clc.yaml"


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

