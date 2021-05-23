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

"""Parent OAuth endpoint for CLC"""

import plugins.basetypes
import plugins.session
import plugins.oauthGeneric
import typing
import aiohttp.web


async def process(
    server: plugins.basetypes.Server, session: plugins.session.SessionObject, indata: dict,
) -> typing.Union[dict, aiohttp.web.Response]:

    state = indata.get("state")
    code = indata.get("code")

    rv: typing.Optional[dict] = None
    oatype = None
    # Generic OAuth handler, only one we support for now. Works with ASF OAuth.
    if state and code:
        rv = await plugins.oauthGeneric.process(indata, session, server)
        oatype = "apache"

    if rv and oatype == "apache":
        cookie = await plugins.session.set_session(
            server, uid=rv["uid"], name=rv["fullname"], email=rv["email"]
        )
        return aiohttp.web.Response(
            headers={"set-cookie": cookie, "content-type": "application/json"}, status=200, text='{"okay": true}',
        )

    # Plain text login
    usr = indata.get('username')
    pwd = indata.get('password')
    if usr and pwd:
        if usr in server.config.accounts.accounts:
            account = server.config.accounts.accounts[usr]
            xpwd = None
            # So far, just plain text support
            if 'password_plain' in account:
                xpwd = account['password_plain']
            if xpwd and pwd == xpwd:  # Correct credentials!
                cookie = await plugins.session.set_session(
                    server, uid=usr, name=account.get('name', usr), email=account.get('email', usr)
                )
                return aiohttp.web.Response(
                    headers={"set-cookie": cookie, "content-type": "application/json"}, status=200, text='{"okay": true}',
                )
        return {"okay": False, "message": "Invalid credentials supplied."}
    return {"okay": False, "message": "Could not process OAuth login!"}


def register(server: plugins.basetypes.Server):
    return plugins.basetypes.Endpoint(process)
