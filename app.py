from datetime import datetime
import random
import shutil
from flask import Flask, jsonify, request, make_response, send_file
from mockupforge import mockup
import json
import urllib.request
import os

from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)


def generate_request_id() -> str:
    """
    Generate a unique ID for request based on server time and a random salt.

    Returns:
        str: unique ID
    """

    return hex(hash(datetime.now().timestamp() + random.randint(0, 1000000)))[2:]


def get_available_mockups() -> dict[str, dict[str, str | list[int]]]:
    with open("mockups.json", "r") as f:
        return json.load(f)


@app.get("/")
def ping():
    return make_response(
        jsonify({"status": "ok", "message": "hello", "data": None}), 200
    )


@app.post("/v1/<api_key>/mockup")
def mockup_post(api_key: str):
    req_id: str = generate_request_id()
    os.mkdir(f"temp/{req_id}")

    mockups: dict[str, dict[str, str | list[int]]] = get_available_mockups()

    try:
        req = request.get_json()

        if api_key != os.environ["API_KEY"]:
            return make_response(
                jsonify({"status": "error", "message": "Unauthorized.", "data": None}),
                401,
            )

        if not "type" in req:
            return make_response(
                jsonify(
                    {
                        "status": "error",
                        "message": "Expected `type` in request body.",
                        "data": None,
                    }
                ),
                400,
            )
        if not req["type"] in mockups.keys():
            return make_response(
                jsonify(
                    {
                        "status": "error",
                        "message": f"`type` must be one of `{'`, `'.join(mockups.keys())}`",
                        "data": None,
                    }
                ),
                400,
            )
        if not "image" in req:
            return make_response(
                jsonify(
                    {
                        "status": "error",
                        "message": "Expected `image` in request body.",
                        "data": None,
                    }
                ),
                400,
            )
        if not "color" in req:
            return make_response(
                jsonify(
                    {
                        "status": "error",
                        "message": "Expected `color` in request body.",
                        "data": None,
                    }
                ),
                400,
            )
        if not isinstance(req["color"], list):
            return make_response(
                jsonify(
                    {
                        "status": "error",
                        "message": "Expected `color` to be a list.",
                        "data": None,
                    }
                ),
                400,
            )
        if not all(
            (isinstance(v, float) or isinstance(v, int)) and v >= 0 and v <= 255
            for v in req["color"]
        ):
            return make_response(
                jsonify(
                    {
                        "status": "error",
                        "message": "Expected contents of `color` to be numeric values between 0 and 255 (inclusive).",
                        "data": None,
                    }
                ),
                400,
            )
        if len(req["color"]) != 3:
            return make_response(
                jsonify(
                    {
                        "status": "error",
                        "message": "Expected `color` to have three values.",
                        "data": None,
                    }
                ),
                400,
            )

        try:
            urllib.request.urlretrieve(
                req["image"], f"temp/{req_id}/source_image_{req_id}"
            )
        except Exception as e:
            print(e)

            return make_response(
                jsonify(
                    {
                        "status": "error",
                        "message": "failed to retrieve image",
                        "data": None,
                    }
                ),
                500,
            )

        output_path = f"temp/{req_id}/output_image_{req_id}.png"
        mockup(
            output_path,
            f"mockups/{req['type']}.xcf",
            f"temp/{req_id}/source_image_{req_id}",
            req["color"],
        )

        return send_file(output_path, mimetype="image/png")
    except Exception as e:
        print(e)

        return make_response(
            jsonify(
                {"status": "error", "message": "unknow server error", "data": None}
            ),
            500,
        )
    finally:
        shutil.rmtree(f"temp/{req_id}")


@app.get("/v1/<api_key>/mockup")
def mockup_get(api_key: str):
    mockups: dict[str, dict[str, str | list[int]]] = get_available_mockups()

    if api_key != os.environ["API_KEY"]:
        return make_response(
            jsonify({"status": "error", "message": "Unauthorized.", "data": None}), 401
        )

    return make_response(
        jsonify({"status": "ok", "message": "success", "data": {"mockups": mockups}}),
        200,
    )
