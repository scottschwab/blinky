import json
import logging

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

bucket = 'slackstatus'
status_object = 'latestupdate.json'
known_channels_object = "known_channels.json"

def create_response(status_code, content_type, message_string):
    out = dict()
    out['statusCode'] = status_code
    out['headers'] = { "Content-Type" : content_type }
    out['body'] = message_string
    return out

def handle_authorization(body_json, known_channels):
    """ used on verify the end points works, just returning a message that 
    contains the challenge value passed in """
    logger.info(body_json['challenge'])
    return create_response(200, 'application/json', 
        json.dumps({ "challenge" : body_json['challenge']  }))


def load_known_from_s3():
    logger.info("loading channels")
    s3 = boto3.resource('s3')
    kc = s3.Object(bucket, known_channels_object)
    k = kc.get()['Body'].read().decode('utf-8')
    return json.loads(k)


def write_msg_to_s3(message):
    """Write the message to a known s3 object"""
    logging.info("writing message [" + message + "]")
    s3 = boto3.resource('s3')
    o2 = s3.Object(bucket, status_object)
    v = o2.put(Body=message, ContentLength=len(message), ContentType="application/json")
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


def handle_message(body_json, known_channels):
    logger.info("handling a message")

    logger.info(body_json)
    if 'event' in body_json:
        message_json = body_json['event']
        event_time = body_json['event_time']
        channel_name = determine_channel_tag(message_json)
        if channel_name is not None and message_json[channel_name] in known_channels:
            logger.info(known_channels[message_json[channel_name]])
            message = build_msg_from_message_body(
                message_json, 
                known_channels[message_json[channel_name]]['name'],
                event_time)
            logger.info(message)
            status = write_msg_to_s3(message)
            return create_response(status, "text/plain", "ok")
        else:
            return create_response(501,'text/plain','channel not known')
    else:
        return create_response(501, 'text/plain', 'event not in body')



def handle_type_top_level(body_json, known_channels):
    logger.info("in handle_type_top_level")
    if body_json['type'] in eventHandler:
        action = eventHandler[body_json['type']]
        response = action(body_json, known_channels) 
        logger.info(response)
        return response    
    logger.info("nothing in handle_type_top_level")


eventHandler = dict()
eventHandler["url_verification"] = handle_authorization
eventHandler["event_callback"] = handle_message


def lambda_handler(event, context):
    """ main driver called from AWS """
    try:
        known_channels = load_known_from_s3()
        logger.info(known_channels)
    except:
        return create_response(500, 'text/plain', 
             "support s3 file not found, " + known_channels_object)

    logger.info('got event {}'.format(event))
    if event is None or 'body' not in event:
        logger.warn("no body in the request")
        return create_response(400, 'text/plain', "missing body in request")

    logger.info("setting event sent in to body")
    body_json = json.loads(event['body'])

    if 'type' in body_json:
        logger.info("handing a type in the body")
        return handle_type_top_level(body_json, known_channels)
    
    logger.info("nothing triggered so falling through")
    return create_response(501, 'text/plain', "event not handled")
          
