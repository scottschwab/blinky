import json
import logging

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

known_channels = dict()
known_channels['G02NE4N0M'] = "object_storage"
known_channels['D33EMSV3J'] = "bradley schwab"

bucket = 'slackstatus'
obj = 'latestupdate'


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


def write_msg_to_s3(message):
    """Write the message to a known s3 object"""
    logging.info("writing message [" + message + "]")
    s3 = boto3.resource('s3')
    o2 = s3.Object(bucket, obj)
    v = o2.put(Body=message, ContentLength=len(message), ContentType="text/plain")
    logger.info(v)
    return v['ResponseMetadata']['HTTPStatusCode']


def determine_channel_tag(message_json):
    if 'channel' in message_json:
        channel_name = 'channel'
    elif 'group' in message_json:
        channel_name = 'group'
    else:
        channel_name = None
    return channel_name


def build_msg_from_message_body(message_json, channel, event_time):
    msg = dict()
    msg['channel'] = channel
    msg['text'] = message_json['text']
    msg['event_time'] = event_time
    return json.dumps(msg)


def handle_message(body_json):
    logger.info("handling a message")
    status = 501

    logger.info(body_json)
    if 'event' in body_json:
        message_json = body_json['event']
        event_time = body_json['event_time']
        channel_name = determine_channel_tag(message_json)
        if channel_name is not None and message_json[channel_name] in known_channels:
            status = write_msg_to_s3(build_msg_from_message_body(
                message_json, 
                known_channels[message_json[channel_name]],
                event_time))
    return { "statusCode":status  }


eventHandler = dict()
eventHandler["url_verification"] = handle_authorization
eventHandler["event_callback"] = handle_message

def handle_type_top_level(body_json):
    logger.info("in handle_type_top_level")
    if body_json['type'] in eventHandler:
        action = eventHandler[body_json['type']]
        response = action(body_json) 
        logger.info(response)
        return response    
    logger.info("nothing in handle_type_top_level")

    

def lambda_handler(event, context):
    """ main driver called from AWS """

    logger.info('got event {}'.format(event))
    if event is None or 'body' not in event:
        logger.warn("no body in the request")
        return {
            "headers" : { "Context-type" : "text/plain" },
            "statusCode": 400,
            "body" : "missing body in request"
        }

    logger.info("setting event sent in to body")
    body_json = json.loads(event['body'])

    if 'type' in body_json:
        logger.info("handing a type in the body")
        return handle_type_top_level(body_json)
    
    logger.info("nothing triggered so falling through")
    return { 
        "headers" : { "Context-type" : "text/plain" },
        "statusCode" : 501,
        "body" : "event not handled"
    }      
