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

""" New Project API end point for CLC"""


async def process(server: plugins.basetypes.Server, session: plugins.session.SessionObject, indata: dict) -> dict:
    if session and (session.credentials or server.config.debug.open_server):
        repo_url = indata.get("url")
        words = indata.get("words", server.config.words)
        excludes = indata.get("excludes", server.config.excludes)
        excludes_context = indata.get("excludes_context", [])
        branch = indata.get("branch")
        in_db = any([project.settings["source"] == repo_url for project in server.data.projects.values()])
        if repo_url and not in_db and not any(project["url"] == repo_url for project in server.data.project_queue):
            server.data.project_queue.append(
                {
                    "url": repo_url,
                    "branch": branch,
                    "excludes": [e for e in excludes if e],
                    "words": words,
                    "excludes_context": [e for e in excludes_context if e],
                }
            )
            plugins.auditlog.log_entry(session, f"Added {repo_url} to list of projects")
            return {"okay": True, "message": "Project URL added to scan queue. Please wait for the next scan to run."}
        else:
            return {"okay": False, "message": "Project URL is already on the scan list"}
    else:
        return {
            "okay": False,
            "message": "You need to be logged in to access this endpoint",
        }


def register(server: plugins.basetypes.Server):
    return plugins.basetypes.Endpoint(process)
