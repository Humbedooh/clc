#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import plugins.basetypes
import plugins.session
import plugins.auditlog
import typing
import aiohttp
import re

""" New Organization API end point for CLC"""

GRAPHQL_URL = "https://api.github.com/graphql"


async def github_repos(server: plugins.basetypes.Server, login: str) -> typing.List[str]:
    """Loads all GitHub repositories in an organization or userspace using GraphQL"""
    query = """
        {
            organization(login: "%s") {
                repositories(first: 100, after:%s) {
                    pageInfo {
                        hasNextPage
                        endCursor
                    }
                    edges {
                        node {
                            name
                            databaseId
                        }
                    }
                }
            }
        }
        """
    repos = []
    api_headers = {"Authorization": "token %s" % server.config.oauth.github_key}
    async with aiohttp.ClientSession(headers=api_headers) as session:
        next_page = True
        after = "null"
        while next_page:
            async with session.post(
                    GRAPHQL_URL, json={"query": query % (login, after)}
            ) as rv:
                js = await rv.json()
                for edge in js["data"]["organization"]["repositories"]["edges"]:
                    repo = edge['node']['name']
                    repos.append(repo)
                next_page = js["data"]["organization"]["repositories"]["pageInfo"][
                    "hasNextPage"
                ]
                after = (
                        '"%s"'
                        % js["data"]["organization"]["repositories"]["pageInfo"]["endCursor"]
                )
    return repos


async def process(server: plugins.basetypes.Server, session: plugins.session.SessionObject, indata: dict) -> dict:
    if session and (session.credentials or server.config.debug.open_server):
        provider = indata.get("provider")
        orgid = indata.get("id")
        words = indata.get("words", server.config.words)
        excludes = indata.get("excludes", server.config.excludes)
        excludes_context = indata.get("excludes_context", [])
        branch = indata.get("branch")
        repos = []
        if orgid and provider == "github":
            repos = await github_repos(server, orgid)
        if repos:
            known = 0
            new = 0
            for repo in repos:
                repo_url = f"https://github.com/{orgid}/{repo}.git"
                in_db = any([project.settings["source"] == repo_url for project in server.data.projects.values()])
                if repo_url and not in_db and not any(project["url"] == repo_url for project in server.data.project_queue):
                    new += 1
                    server.data.project_queue.append(
                        {
                            "url": repo_url,
                            "branch": branch,
                            "excludes": [e for e in excludes if e],
                            "words": words,
                            "excludes_context": [e for e in excludes_context if e],
                        }
                    )
                else:
                    known += 1
                    plugins.auditlog.log_entry(session, f"Added {repo_url} to list of projects")
            return {"okay": True, "message": f"{new} repositories added to scan queue, {known} already in the system."}
        else:
            return {"okay": False, "message": "No repositories could be found."}
    else:
        return {
            "okay": False,
            "message": "You need to be logged in to access this endpoint",
        }


def register(server: plugins.basetypes.Server):
    return plugins.basetypes.Endpoint(process)
