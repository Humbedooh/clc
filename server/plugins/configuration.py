from __future__ import annotations
import os
import typing

import yaml


class ServerConfig:
    def __init__(self, subyaml: dict, ver: tuple):
        self.ip: str = subyaml.get("bind", "0.0.0.0")
        self.port: int = int(subyaml.get("port", 8080))
        self.traceback: bool = bool(subyaml.get("traceback", False))
        self.version = ver


class TaskConfig:
    def __init__(self, subyaml: dict):
        self.refresh_rate: int = int(subyaml.get("refresh_rate", 150))
        assert self.refresh_rate >= 10, "Refresh rate must be at least 10 seconds!"


class OAuthConfig:
    def __init__(self, subyaml: dict):
        self.github_key: str = subyaml.get("github_api_key", "")
        self.authoritative_domains: typing.List[str] = subyaml.get("authoritative_domains", [])
        self.admins: typing.List[str] = subyaml.get("admins", "").split(" ")


class DirectoryConfig:
    def __init__(self, subyaml: dict):
        self.scratch = subyaml.get("scratch", "scratch")
        self.remove_bare = subyaml.get("remove_bare", True)
        assert os.path.isdir(self.scratch), f"Scratch dir {self.scratch} could not be found, please create it or change clc.yaml!"

class DebugConfig:
    def __init__(self, subyaml: dict):
        self.print_issues = subyaml.get('print_issues', True)
        self.open_server = subyaml.get('open_server', False)

class Project:
    def __init__(self, path):
        self.repo = path.split("/")[-1]
        self.mtimes = {}
        self.settings = {}
        self.history = []
        self.issues = []
        self.issues_per_file = {}
        self.deleted = False  # Is set to true when scheduled to removal by background services
        self.warning = ""  # Set when a scan fails for whatever reason


class LogicConfig:
    def __init__(self, subyaml: dict):
        self.short_word_limit = int(subyaml.get('short_word_limit', 5))
        self.short_word_regex = subyaml.get('short_words', r"(?:\b|_)+({word})(?:ed|ing|s)?(?:\b|\W|_)+")
        self.long_word_regex = subyaml.get('long_words', r"({word})")


class AccountConfig:
    def __init__(self, subyaml: dict):
        subyaml = subyaml or {}
        self.accounts_file = subyaml.get('accounts_file')
        self.accounts = {}
        self.audit_log = subyaml.get('auditlog', 'auditlog.txt')
        if self.accounts_file and os.path.exists(self.accounts_file):
            self.accounts = yaml.safe_load(open(self.accounts_file))
            self.accounts_file_stat = os.stat(self.accounts_file)
        else:
            self.accounts_file_stat = None


class Configuration:
    def __init__(self, clcversion: tuple, yml: dict, dyml: dict):
        self.server: ServerConfig = ServerConfig(yml.get("server", {}), clcversion)
        self.tasks: TaskConfig = TaskConfig(yml.get("tasks", {}))
        self.oauth: OAuthConfig = OAuthConfig(yml.get("oauth", {}))
        self.dirs: DirectoryConfig = DirectoryConfig(yml.get("directories", {}))
        self.debug: DebugConfig = DebugConfig(yml.get("debug", {}))
        self.accounts: AccountConfig = AccountConfig(yml.get('acl', {}))
        self.logic: LogicConfig = LogicConfig(dyml.get('match_logic', {}))
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

