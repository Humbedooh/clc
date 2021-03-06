import io
import json
import urllib.parse

import aiohttp.web
import multipart

BOXER_MAX_PAYLOAD = 256 * 1024


async def parse_formdata(body_type, request: aiohttp.web.BaseRequest) -> dict:
    indata = {}
    for key, val in urllib.parse.parse_qsl(request.query_string):
        indata[key] = val
    # PUT/POST form data?
    if request.method in ["PUT", "POST"]:
        if request.can_read_body:
            try:
                if request.content_length and request.content_length > BOXER_MAX_PAYLOAD:
                    raise ValueError("Form data payload too large, max 256kb allowed")
                body = await request.text()
                if body_type == "json":
                    try:
                        js = json.loads(body)
                        assert isinstance(js, dict)  # json data MUST be an dictionary object, {...}
                        indata.update(js)
                    except ValueError:
                        raise ValueError("Erroneous payload received")
                elif body_type == "form":
                    if request.headers.get("content-type", "").lower() == "application/x-www-form-urlencoded":
                        try:
                            for key, val in urllib.parse.parse_qsl(body):
                                indata[key] = val
                        except ValueError:
                            raise ValueError("Erroneous payload received")
                    # If multipart, turn our body into a BytesIO object and use multipart on it
                    elif "multipart/form-data" in request.headers.get("content-type", "").lower():
                        fh = request.headers.get("content-type")
                        fb = fh.find("boundary=")
                        if fb > 0:
                            boundary = fh[fb + 9 :]
                            if boundary:
                                try:
                                    for part in multipart.MultipartParser(
                                        io.BytesIO(body.encode("utf-8")), boundary, len(body),
                                    ):
                                        indata[part.name] = part.value
                                except ValueError:
                                    raise ValueError("Erroneous payload received")
            finally:
                pass
    return indata
