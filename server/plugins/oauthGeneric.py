# Generic OAuth plugin for services such as Apache OAuth
import re
import requests
import aiohttp

asf_oauth_url = "https://oauth.apache.org/token"
oauth_domain = "apache.org"


async def process(formdata, session, server):
    js = None
    url = asf_oauth_url
    headers = {"User-Agent": "ASF Boxer OAuth Agent/0.1"}
    # This is a synchronous process, so we offload it to an async runner in order to let the main loop continue.
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=formdata) as rv:
            js = await rv.json()
            assert rv.status == 200, f"Unexpected return code for GET on {url}: {rv.status}"
            js["oauth_domain"] = oauth_domain
            js["authoritative"] = True
            return js
