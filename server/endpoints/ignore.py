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
import os
import yaml

""" Ignore word API end point for CLC"""


async def process(server: plugins.basetypes.Server, session: plugins.session.SessionObject, indata: dict) -> dict:
    if session and (session.credentials or server.config.debug.open_server):
        repo = indata.get("repo", '')
        assert ".." not in repo, "Invalid path specified"
        assert "~" not in repo, "Invalid path specified"
        path = indata.get("path")
        word = indata.get("word")
        line = indata.get("line")
        column = indata.get("column")
        oymlfile = os.path.join(server.config.dirs.scratch, repo, "_clc.yaml")
        ymlfile = os.path.join(server.config.dirs.scratch, repo, "_clc_ignores.yaml")
        if os.path.exists(oymlfile):
            try:
                yml = yaml.safe_load(open(ymlfile))
            except FileNotFoundError:
                yml = []
            yml.append({
                "path": path,
                "word": word,
                "line": line,
                "mark": column,
                "resolution": "ignore",
            })
            yaml.dump(yml, open(ymlfile, "w"))
            server.data.projects[repo].mtimes[ymlfile] = os.stat(ymlfile).st_mtime
            plugins.auditlog.log_entry(session, f"Changed ignore settings for {repo} ({ymlfile})")
            return {
                "okay": True,
                "message": "Ignore list updated",
            }
        else:
            return {
                "okay": False,
                "message": "No such project",
            }

    else:
        return {
            "okay": False,
            "message": "You need to be logged in to access this endpoint",
        }


def register(server: plugins.basetypes.Server):
    return plugins.basetypes.Endpoint(process)
