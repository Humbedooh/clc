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

""" Settings API end point for CLC"""


async def process(server: plugins.basetypes.Server, session: plugins.session.SessionObject, indata: dict) -> dict:
    if session and (session.credentials or True):
        repo = indata.get("repo")
        assert ".." not in repo, "Invalid path specified"
        assert "~" not in repo, "Invalid path specified"
        excludes = indata.get("excludes")
        bad_words = indata.get("words")
        excludes_context = indata.get("excludes_context", [])
        ymlfile = os.path.join(server.config.dirs.scratch, repo, "_clc.yaml")
        if os.path.exists(ymlfile):
            yml = yaml.safe_load(open(ymlfile))
            if not isinstance(bad_words, dict):
                return {
                    "okay": False,
                    "message": "Word list must be dictionary, word: context",
                }
            if not isinstance(excludes, list):
                return {
                    "okay": False,
                    "message": "Excludes list must by an array of exclude globs",
                }
            if not isinstance(excludes_context, list):
                return {
                    "okay": False,
                    "message": "Excludes context list must by an array of exclude regexes",
                }
            yml["bad_words"] = bad_words
            yml["excludes"] = excludes
            yml["excludes_context"] = excludes_context
            yaml.dump(yml, open(ymlfile, "w"))
            return {
                "okay": True,
                "message": "Settings saved. Please wait for next scan for it to apply.",
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
