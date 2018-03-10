import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handleAuthorization(body_json):
    """ used on verify the end points works, just returning a message that contains the 
    challenge value passed in """
    logger.info(body_json['challenge'])
    msg = '{ "challenge" : "{' + body_json['challenge'] + '}" }'
    return {
        "statusCode":200,
        "headers" : { "Content-Type":"application/json" },
        "body" : msg
    }

def handleAuthorization(body_json):
    """ used on verify the end points works, just returning a message that contains the 
    challenge value passed in """
    logger.info(body_json['challenge'])
    msg = '{ "challenge" : "{' + body_json['challenge'] + '}" }'
    return {
        "statusCode":200,
        "headers" : { "Content-Type":"application/json" },
        "body" : msg
    }    



def lambda_handler(event, context):
    """ main driver called from AWS """
    logger.info('got event {}'.format(event))
    event_in = event
    if 'body' not in event:
        return {
            logger.warn("no body in the request")
            "headers" : { "Context-type" : "text/plain" },
            "statusCode": 400.
            "body" : "missing body in request"
        }

    logger.info("setting event to body")
    body_json = json.loads(event['body'])

    eventHandler = dict()
    eventHandler["url_verification"] = handleAuthorization

    if body_json in eventHandler.keys():
        action = eventHandler(body_json)
        return logger.info(body_json)

    return { 
        "headers" : { "Context-type" : "text/plain" },
        "statusCode" : 501,
        "body" : "event not handled"
    }      
