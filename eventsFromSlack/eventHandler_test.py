import pytest
import json
import eventHandler
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def test_no_event():
    msg = eventHandler.lambda_handler(None,None)
    assert msg is not None
    assert msg['statusCode'],400
    logger.info(msg)


def test_no_body():
    x = dict()
    x['test'] = "foo"
    msg = eventHandler.lambda_handler(x,None)
    assert msg is not None
    assert msg['statusCode'] == 400


def test_body_validate():
    x = dict()
    body = dict()
    x["token"] = "Jhj5dZrVaK7ZwHHjRyZWjbDl"
    x["challenge"] = "3eZbrw1aBm2rZgRNFdxV2595E9CY3gmdALWMmHkvFXO7tYXAYM8P"
    x["type"] = "url_verification"
    body['body'] = json.dumps(x)
    msg = eventHandler.lambda_handler(body,None)
    assert msg is not None
    assert msg['statusCode'] == 200
    assert msg['body'] == '{ "challenge" : "{3eZbrw1aBm2rZgRNFdxV2595E9CY3gmdALWMmHkvFXO7tYXAYM8P}" }'


def test_determine_channel_tag():
    msg1 = dict()
    msg1['channel'] = 'foo'
    assert 'channel' == eventHandler.determine_channel_tag(msg1)
    msg2 = dict()
    msg2['group'] = 'bar'
    assert 'group' == eventHandler.determine_channel_tag(msg2)
    msg3 = dict()
    msg3['frog'] = 'bar'
    assert eventHandler.determine_channel_tag(msg3) is None


def test_build_msg_from_message_body():
    message_body = dict()
    message_body['text'] = 'hello world'
    back_str = eventHandler.build_msg_from_message_body(message_body, 'dog',1)
    back = json.loads(back_str)
    assert back['channel'] == 'dog'
    assert back['text'] == 'hello world'
    assert back['event_time'] == 1


def test_message():
    msg_in = dict()
    
    msg_in["body"] = """
    {
        "token": "XXYYZZ",
        "team_id": "TXXXXXXXX",
        "api_app_id": "AXXXXXXXXX",
        "event": {
            "type": "message",
            "channel": "D33EMSV3J",
            "user": "U2147483697",
            "text": "Hello world",
            "ts": "135551523.000005"
        },
        "type": "event_callback",
        "authed_users": [
                "UXXXXXXX1",
                "UXXXXXXX2"
        ],
        "event_id": "Ev08MFMKH6",
        "event_time": 1234567890
    }"""

    
    msg = eventHandler.lambda_handler(msg_in,None)
    logger.info(msg)
