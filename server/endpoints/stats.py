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
import os
import yaml
import typing

""" Quick Stats API end point for CLC"""


async def process(server: plugins.basetypes.Server, session: plugins.session.SessionObject, indata: dict) -> dict:
    out = {}
    repos = []
    for repo in os.listdir(server.config.dirs.scratch):
        path = os.path.join(server.config.dirs.scratch, repo)
        ymlfile = os.path.join(path, "_clc.yaml")
        if os.path.exists(ymlfile):
            yml = yaml.safe_load(open(ymlfile))
            repos.append((repo, yml.get("lastrun", 0)))

    repos = [x[0] for x in sorted(repos, key=lambda x: x[1], reverse=True)]

    for repo in repos:
        path = os.path.join(server.config.dirs.scratch, repo)
        ymlfile = os.path.join(path, "_clc_history.yaml")
        if os.path.exists(ymlfile):
            yml = yaml.safe_load(open(ymlfile))
            yml = yml[-50:]
            issues = ["Issues discovered"]
            processed = ["Files processed"]
            duration: typing.List[typing.Union[str, int]] = ["Scan duration"]
            x = ["x"]
            for scan in yml:
                issues.append(scan["issues"])
                processed.append(scan["files_processed"])
                duration.append(int(scan["duration"]))
                x.append(scan["epoch"])
            out[repo] = [x, processed, issues, duration]
    return {
        "activity": server.data.activity,
        "stats": out,
    }


def register(server: plugins.basetypes.Server):
    return plugins.basetypes.Endpoint(process)
