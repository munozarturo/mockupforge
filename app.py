from datetime import datetime
import random
import shutil
from flask import Flask, jsonify, request, make_response
from mockupforge import mockup
import json
import urllib.request
import os
import boto3
import boto3.session
from botocore.exceptions import ClientError

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
    return make_response(jsonify({"status": "ok", "message": "hello", "data": None}), 200)

@app.post("/v1/<api_key>/mockup")
def mockup_post(api_key: str):
    req_id: str = generate_request_id()
    os.mkdir(f"temp/{req_id}")

    mockups: dict[str, dict[str, str | list[int]]] = get_available_mockups()

    try:
        req = request.get_json()

        if api_key != os.environ["API_KEY"]:
            return make_response(jsonify({"status": "error", "message": "Unauthorized.", "data": None}), 401)

        if not "type" in req:
            return make_response(jsonify({"status": "error", "message": "Expected `type` in request body.", "data": None}), 400)
        if not req["type"] in mockups.keys():
            return make_response(jsonify({"status": "error", "message": f"`type` must be one of `{'`, `'.join(mockups.keys())}`", "data": None}), 400)
        if not "image" in req:
            return make_response(jsonify({"status": "error", "message": "Expected `image` in request body.", "data": None}), 400)
        if not "color" in req:
            return make_response(jsonify({"status": "error", "message": "Expected `color` in request body.", "data": None}), 400)
        if not isinstance(req["color"], list):
            return make_response(jsonify({"status": "error", "message": "Expected `color` to be a list.", "data": None}), 400)
        if not all((isinstance(v, float) or isinstance(v, int)) and v >= 0 and v <= 255 for v in req["color"]):
            return make_response(jsonify({"status": "error", "message": "Expected contents of `color` to be numeric values between 0 and 255 (inclusive).", "data": None}), 400)
        if len(req["color"]) != 3:
            return make_response(jsonify({"status": "error", "message": "Expected `color` to have three values.", "data": None}), 400)

        try:
            urllib.request.urlretrieve(
                req["image"], f"temp/{req_id}/source_image_{req_id}"
            )
        except Exception as e:
            print(e)
            
            return make_response(jsonify({"status": "error", "message": "failed to retrieve image", "data": None}), 500)

        mockup(
            f"temp/{req_id}/output_image_{req_id}.png",
            f"mockups/{req["type"]}.xcf",
            f"temp/{req_id}/source_image_{req_id}", 
            req["color"]
        )

        s3 = boto3.client(
            "s3", 
            aws_access_key_id=os.environ["AWS_ACCESS_KEY"], 
            aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
        )
        
        s3.upload_file(f"temp/{req_id}/output_image_{req_id}.png", "mockupforge-mockups", f"{req_id}.png")

        return make_response(jsonify({"status": "ok", "message": "success", "data": {
            "mockup_id": req_id
        }}), 200)
    except Exception as e:
        print(e)

        return make_response(jsonify({"status": "error", "message": "unknow server error", "data": None}), 500)
    finally:
        shutil.rmtree(f"temp/{req_id}")


@app.get("/v1/<api_key>/mockup")
def mockup_get(api_key: str):
    mockups: dict[str, dict[str, str | list[int]]] = get_available_mockups()

    if api_key != os.environ["API_KEY"]:
        return make_response(jsonify({"status": "error", "message": "Unauthorized.", "data": None}), 401)

    return make_response(jsonify({"status": "ok", "message": "success", "data": {
            "mockups": mockups
        }}), 200)


@app.get("/v1/<api_key>/mockup/<mockup_id>")
def mockup_get_id(api_key: str, mockup_id: str):
    if api_key != os.environ["API_KEY"]:
        return make_response(jsonify({"status": "error", "message": "Unauthorized.", "data": None}), 401)

    s3 = boto3.client(
        "s3", 
        aws_access_key_id=os.environ["AWS_ACCESS_KEY"], 
        aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"]
    )

    try:
        s3.head_object(Bucket="mockupforge-mockups", Key=f"{mockup_id}.png")

        return make_response(jsonify({"status": "ok", "message": "success", "data": {
           "mockup": f"https://mockupforge-mockups.s3.us-east-2.amazonaws.com/{mockup_id}.png"
        }}), 200)
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            return make_response(jsonify({"status": "error", "message": "requested resource does not exist.", "data": None}), 200)
