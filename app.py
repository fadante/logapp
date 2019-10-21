#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, request, jsonify
import requests
import json
import sys
import os


# Global parameters
bearer = "bot_access_token"
webex_api = "https://api.ciscospark.com/v1"
bot_email = "logapp@webex.bot"
bot_name = "Logapp "


def webex_headers():
    headers = {
                "Accept": "application/json",
                "Content-Type": "application/json; charset=utf-8",
                "Authorization": "Bearer " + bearer
              }
    return headers


def webex_get(url):
    request = requests.get(url, headers=webex_headers())
    request = request.json()
    return request


def webex_post(url, data):
    request = requests.post(url, json.dumps(data), headers=webex_headers())
    request = request.json()
    return request


def help_me():
    return "Enter `TrackingID` to get it.<br/>"


def trackingId():
    return "TrackingID: "


def handle_text(text):
    result = None
    if text.lower().startswith('help'):
        result = help_me()
    if text.lower().startswith('trackingid'):
        result = trackingId()
    if text.lower().startswith('logapphelp'):
        result = help_me()
    if text.lower().startswith('logapptrackingid'):
        result = trackingId()
    if result == None:
        result = "I didn't understand your request. Please type `help` to see what I can do"
    return result


app = Flask(__name__) #Flask constructor

@app.route('/', methods=['GET', 'POST'])
def webex_webhook():
    if request.method == 'POST':
        webhook = request.get_json(silent=True)

        senders_email = webhook['data']['personEmail']
        room_id = webhook['data']['roomId']

        if senders_email != bot_email:
            result = webex_get(
                webex_api + '/messages/{0}'.format(webhook['data']['id']))
            in_message = result.get('text', '')

            textTrackingId = request.headers
            postTrackingId = textTrackingId['TrackingID']

            try:
                in_message = in_message.replace(bot_name.split(" ")[0] + " ", "")
            except:
                in_message = in_message.replace(bot_name.lower() + " ", '')
            msg = handle_text(in_message)

            if msg != None:
                webex_post(webex_api + "/messages",
                                {"roomId": room_id, "markdown": msg})
                #Post the TrackingID to Webex Space
                if 'trackingid' in in_message.lower():
                    webex_post(webex_api + "/messages",
                                {"roomId": room_id, "markdown": postTrackingId})

        return "true"

    elif request.method == 'GET':
        message = "<center><img src=\"http://bit.ly/logapp-512x512\" alt=\"Spark Bot\" style=\"width:256; height:256;\"</center>" \
                  "<center><h2><b>Congratulations! Your <i style=\"color:#0000ff;\">%s</i> bot is up and running.</b></h2></center>" \
                  "<center><b><i>Please don't forget to create Webhooks to start receiving events from Cisco Webex Teams!</i></b></center>" %bot_name
        return message


if __name__ == '__main__':
    app.run("0.0.0.0", port=16180, debug=True)
