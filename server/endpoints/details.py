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
import aiofiles
import typing
try:
    loader = typing.Union[yaml.Loader, yaml.CLoader]  # mypy fixups
    dumper = typing.Union[yaml.Dumper, yaml.CDumper]  # mypy fixups
    from yaml import CLoader as loader, CDumper as dumper
    print("Using fast C++ YAML parser..!")
except:
    from yaml import Loader as loader, Dumper as dumper

""" Quick Details API end point for CLC"""


async def process(server: plugins.basetypes.Server, session: plugins.session.SessionObject, indata: dict) -> dict:
    out = {}
    project = indata.get("project", "foo")
    path = os.path.join(server.config.dirs.scratch, project)
    limit = int(indata.get("limit", 1000))
    if os.path.isdir(path):
        assert ".." not in path, "Invalid path specified"
        assert "~" not in path, "Invalid path specified"
        hymlfile = os.path.join(path, "_clc_history.yaml")
        ymlfile = os.path.join(path, "_clc.yaml")
        if os.path.exists(hymlfile):
            hyml = yaml.safe_load(open(hymlfile))
            yml = yaml.safe_load(open(ymlfile))
            issues = ["Issues discovered"]
            processed = ["Files processed"]
            duration: typing.List[typing.Union[str, int]] = ["Scan duration"]
            x = ["x"]
            for scan in hyml[-50:]:
                issues.append(scan["issues"])
                processed.append(scan["files_processed"])
                duration.append(int(scan["duration"]))
                x.append(scan["epoch"])
            yml["bad_words"] = yml.get("bad_words", server.config.words)
            yml["excludes"] = yml.get("excludes", server.config.excludes)
            out["details"] = yml
            out["repo"] = project
            out["reasons"] = server.config.contexts
            out["chart"] = [x, processed, issues, duration]
            out["breakdown"] = yml['status'].get('words_stacked')
        ymlfile = os.path.join(path, "_clc_issues.yaml")
        issues_stacked = {}
        if os.path.exists(ymlfile):
            ymldata = ""
            entries = 0
            if limit < 2500:  # Slow async load if few lines requested
                async with aiofiles.open(ymlfile) as f:
                    async for line in f:
                        if line.startswith("- "):
                            entries += 1
                            if entries > limit:
                                break
                        ymldata += line
            else:  # If more requested, load everything at once
                ymldata = open(ymlfile).read()
            yml = yaml.load(ymldata, Loader=loader)
            yml = yml[:limit]
            for issue in yml:
                issue["path"] = issue["path"].replace(path, "", 1)
                if not out["breakdown"]:
                    if issue["word"] not in issues_stacked:
                        issues_stacked[issue["word"]] = 1
                    else:
                        issues_stacked[issue["word"]] += 1
            out["issues"] = yml
            if not out["breakdown"]:
                out["breakdown"] = [(x, y) for x, y in issues_stacked.items()]
            else:
                out["breakdown"] = [(x, y) for x, y in out['breakdown'].items() if y]
    return out


def register(server: plugins.basetypes.Server):
    return plugins.basetypes.Endpoint(process)
