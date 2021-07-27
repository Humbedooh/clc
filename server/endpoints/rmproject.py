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
import shutil
import os

""" Remove Project API end point for CLC"""


async def process(server: plugins.basetypes.Server, session: plugins.session.SessionObject, indata: dict) -> dict:
    if session and (session.credentials or server.config.debug.open_server):
        project = indata.get("project")
        in_db = project in server.data.projects.keys()
        if project and in_db:
            plugins.auditlog.log_entry(session, f"Removed {project} from the list of projects")
            project_path = os.path.join(server.config.dirs.scratch, project)
            if os.path.exists(project_path):
                server.data.projects[project].deleted = True
            return {"okay": True, "message": "Project removed from scanner"}
        else:
            return {"okay": False, "message": "Project not found in scan list"}
    else:
        return {
            "okay": False,
            "message": "You need to be logged in to access this endpoint",
        }


def register(server: plugins.basetypes.Server):
    return plugins.basetypes.Endpoint(process)
