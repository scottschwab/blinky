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



def lambda_handler(event, context):
    """ main driver called from AWS """

    eventHandler = dict()
    eventHandler["url_verification"] = handleAuthorization

    logger.warn('got event {}'.format(event))
    event_in = event
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
