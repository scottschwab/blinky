import json
import logging

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

bucket = 'slackstatus'
obj = 'latestupdate'

def write_msg_to_s3(message):
    logging.info("writing message [" + message + "]")
    s3 = boto3.resource('s3')
    o2 = s3.Object(bucket, obj)
    v = o2.put(Body=message, ContentLength=len(message), ContentType="text/plain")
    logger.info(v)
    return v['ResponseMetadata']['HTTPStatusCode']

def handle_authorization(body_json):
    """ used on verify the end points works, just returning a message that contains the 
    challenge value passed in """
    logger.info(body_json['challenge'])
    msg = '{ "challenge" : "{' + body_json['challenge'] + '}" }'
    return {
        "statusCode":200,
        "headers" : { "Content-Type":"application/json" },
        "body" : msg
    }


def handle_message(body_json):
    known_channels = dict()
    known_channels['G024BE91L'] = "fire_engine"

    pattern = "off"
    if body_json['channel'] in known_channels:
        pattern = known_channels[body_json['channel']]

    msg = '{ "pattern" : "' + pattern + '" }'
    status = write_msg_to_s3(msg)
    return {
        "statusCode":status
    }

def lambda_handler(event, context):
    """ main driver called from AWS """

    eventHandler = dict()
    eventHandler["url_verification"] = handle_authorization
    eventHandler["message"] = handle_message

    logger.warn('got event {}'.format(event))
    if event is None or 'body' not in event:
        logger.warn("no body in the request")
        return {
            "headers" : { "Context-type" : "text/plain" },
            "statusCode": 400,
            "body" : "missing body in request"
        }

    logger.info("setting event to body")
    body_json = json.loads(event['body'])


    if body_json['type'] in eventHandler:
        action = eventHandler[body_json['type']]
        response = action(body_json)
        return response

    return { 
        "headers" : { "Context-type" : "text/plain" },
        "statusCode" : 501,
        "body" : "event not handled"
    }      
