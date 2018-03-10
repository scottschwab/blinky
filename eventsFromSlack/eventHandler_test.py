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



