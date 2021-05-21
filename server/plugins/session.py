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

"""This is the user session handler for CLC"""

import http.cookies
import time
import typing
import uuid

import aiohttp.web

import plugins.basetypes
import copy
import typing

MAX_SESSION_AGE = 86400 * 7  # Max 1 week between visits before voiding a session
SAVE_SESSION_INTERVAL = 3600  # Update sessions on disk max once per hour


class SessionCredentials:
    def __init__(self, **kwargs):
        self.uid: str = kwargs.get("uid", "")
        self.name: str = kwargs.get("name", "")
        self.email: str = kwargs.get("email", "")
        self.admin: bool = kwargs.get("admin", False)
        self.github_login = kwargs.get("github_login", None)
        self.github_id = 0


class SessionObject:
    cid: typing.Optional[str]
    cookie: str
    created: int
    last_accessed: int
    credentials: typing.Optional[SessionCredentials]
    server: plugins.basetypes.Server

    def __init__(self, server: plugins.basetypes.Server, **kwargs):
        self.server = server
        if not kwargs:
            now = int(time.time())
            self.created = now
            self.last_accessed = now
            self.credentials = None
            self.cookie = str(uuid.uuid4())
            self.cid = None
        else:
            self.last_accessed = kwargs.get("last_accessed", 0)
            self.credentials = SessionCredentials(**kwargs)
            self.cookie = kwargs.get("cookie", "___")
            self.cid = kwargs.get("cid")


async def get_session(server: plugins.basetypes.Server, request: aiohttp.web.BaseRequest) -> SessionObject:
    session_id = None
    now = int(time.time())
    if request.headers.get("cookie"):
        for cookie_header in request.headers.getall("cookie"):
            cookies: http.cookies.SimpleCookie = http.cookies.SimpleCookie(cookie_header)
            if "clc" in cookies:
                session_id = cookies["clc"].value
                if not all(c in "abcdefg1234567890-" for c in session_id):
                    session_id = None
                break

    # Do we have the session in local memory?
    if session_id and session_id in server.data.sessions:
        x_session = server.data.sessions[session_id]
        if (now - x_session.last_accessed) > MAX_SESSION_AGE:
            del server.data.sessions[session_id]
        else:
            x_session.last_accessed = now
            session = copy.copy(x_session)
            return session
    # If not in local memory, start a new session object
    session = SessionObject(server)
    return session


async def set_session(server: plugins.basetypes.Server, **credentials):
    """Create a new user session in the database"""
    session_id = str(uuid.uuid4())
    cookie: http.cookies.SimpleCookie = http.cookies.SimpleCookie()
    cookie["clc"] = session_id
    session = SessionObject(server, last_accessed=time.time(), cookie=session_id)
    session.credentials = SessionCredentials(**credentials)
    server.data.sessions[session_id] = session

    return cookie["clc"].OutputString()
