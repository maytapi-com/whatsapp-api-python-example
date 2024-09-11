from pickle import TRUE
from urllib import response
from flask import Flask, request, jsonify
from pyngrok import ngrok
import requests
import sys
import base64
import json

app = Flask(__name__)

# Replace the values here.
INSTANCE_URL = "https://api.maytapi.com/api"
PRODUCT_ID = ""
PHONE_ID = ""
API_TOKEN = ""


@app.route("/")
def hello():
    return app.send_static_file("index.html")


def getCatalog():
    url = INSTANCE_URL + "/" + PRODUCT_ID + "/" + PHONE_ID + "/catalog"
    payload = {}
    headers = {
        "Content-Type": "application/json",
        "x-maytapi-key": API_TOKEN,
    }
    r = requests.request('GET', url, headers=headers, data=payload)
    tjson = r.json()
    pData = tjson["data"]
    pSuccess = tjson["success"]
    if pSuccess == True and len(pData) > 0:
        pId = tjson["data"][0]["productId"]
        return pId
    else:
        return 0


def send_response(body):
    print("Request Body", body, file=sys.stdout, flush=True)
    url = INSTANCE_URL + "/" + PRODUCT_ID + "/" + PHONE_ID + "/sendMessage"
    headers = {
        "Content-Type": "application/json",
        "x-maytapi-key": API_TOKEN,
    }
    response = requests.post(url, json=body, headers=headers)
    print("Response", response.json(), file=sys.stdout, flush=True)
    return


@app.route("/webhook", methods=["POST"])
def webhook():
    json_data = request.get_json()

    wttype = json_data["type"]
    if wttype == "message":
        message = json_data["message"]
        conversation = json_data["conversation"]
        _type = message["type"]
        if message["fromMe"]:
            return
        if _type == "text":
            # Handle Messages
            text = message["text"]
            text = text.lower()
            if text == "media":
                body = {
                    "type": "media",
                    "text": "Image Response",
                    "message": "https://via.placeholder.com/140x100",
                }
            elif text == "media64":
                with open("maytapi.jpg", "rb") as img_file:
                    b64_string = base64.b64encode(img_file.read())
                firstStr = "data:image/jpeg;base64,"
                formatImg = b64_string.decode('utf-8')
                fullDataImg = firstStr+formatImg
                body = {
                    "type": "image",
                    "text": "image Response",
                    "message": fullDataImg
                }
            elif text == "location":
                body = {
                    "type": "location",
                    "text": "Location Response",
                    "latitude": "41.093292",
                    "longitude": "29.061737",
                }
            elif text == "link":
                body = {
                    "type": "link",
                    "message": "https://maytapi.com/",
                }
            elif text == "contact":
                body = {
                    "type": "contact",
                    "message": "905301234567@c.us",
                }
            elif text == "vcard":
                body = {
                    "type": "vcard",
                    "message": {
                        "displayName": "John Doe",
                        "vcard": "BEGIN:VCARD\nVERSION:3.0\nFN;CHARSET=UTF-8:John Doe\nN;CHARSET=UTF-8:;John;Doe;;\nTEL;TYPE=CELL:+9051234567\nREV:2020-01-23T11:09:14.782Z\nEND:VCARD",
                    },
                }
            elif text == "filedoc":
                body = {
                    "type": "media",
                    "message": "https://file-examples-com.github.io/uploads/2017/02/file-sample_100kB.doc",
                }
            elif text == "filepdf":
                body = {
                    "type": "media",
                    "message": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
                }
            elif text == "reply":
                rpyto = json_data["message"]["_serialized"]
                body = {
                    "type": "text",
                    "message": "This is reply text",
                    "reply_to": rpyto
                }
            elif text == "product":
                productIdTake = getCatalog()
                if productIdTake == 0:
                    body = {
                        "type": "text",
                        "message": "You don't have a any product"
                    }
                else:
                    body = {
                        "type": "product",
                        "productId": productIdTake
                    }
            elif text == "poll":
                body = {
                    "type": "poll",
                    "message": "Poll Message",
                    "options": ["1", "2", "3"],
                    "only_one": True  # Optional
                }
            elif text == "sticker":
                body = {
                    "type": "sticker",
                    "message": "https://cdnydm.com/wh/aERKsVRyYAO9enBQrRwjlA.webp?size=512x512",
                    "options": {
                        "width": 500,
                        "height": 500
                    }
                }
            else:
                body = {"type": "text", "message": "Echo - " + text}
            body.update({"to_number": conversation})
            send_response(body)
    elif wttype == "status":
        stype =  json_data["type"]
        spid =  json_data["pid"]
        sphoneid =  json_data["phone_id"]
        sStatus =  json_data["status"]
        print("Status of instance ", sphoneid, " changed to ", sStatus)
    elif wttype == "ack":
        ackType =  json_data["type"]
        ackProductId =  json_data["product_id"]
        ackData =  json_data["data"]
        acty = ackData[0]
        acmsgId = ackData[0]
        print("your message with id ",
              acmsgId["msgId"], " was ", acty["ackType"])
    else:
        print("Unknow Type:", wttype,  file=sys.stdout, flush=True)
    return jsonify({"success": True}), 200


def setup_webhook():
    if PRODUCT_ID == "" or PHONE_ID == "" or API_TOKEN == "":
        print(
            "You need to change PRODUCT_ID, PHONE_ID and API_TOKEN values in app.py file.", file=sys.stdout, flush=True
        )
        return
    public_url = ngrok.connect(9000)
    url = INSTANCE_URL + "/" + PRODUCT_ID + "/setWebhook"
    print("url", url, file=sys.stdout, flush=True)
    headers = {
        "Content-Type": "application/json",
        "x-maytapi-key": API_TOKEN,
    }
    body = {"webhook": public_url.public_url + "/webhook"}
    response = requests.post(url, json=body, headers=headers)
    print("webhook ", response.json())


# Do not use this method in your production environment
setup_webhook()
