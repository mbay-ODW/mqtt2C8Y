import sys
import logging
from os import path
from os import remove
import requests
import API.authentication as auth
import API.identity
import time
import threading
import utils
import streamingAnalytics.listener



logger = logging.getLogger('deviceAgent')
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger.info('Logger for deviceAgent was initialised')

def start():
    auth.get().internalID = API.identity.getInternalID(utils.settings.basics()['deviceID'])
    logger.info('Finishing start sequency')

def listener():
    logger.info('Starting listener')
    threadMQTTListener = threading.Thread(
        target=streamingAnalytics.listener.start, daemon=True)
    threadMQTTListener.start()
    return threadMQTTListener

if __name__== "__main__":
    try:
        start()
        statusListener = listener()
        while True:
            time.sleep(1)
            print("Heartbeat")
            if statusListener.is_alive() is False:
                logger.error('Listener on Measurements not alive, restarting')
                time.sleep(5)
                statusListerner = listener()
    except KeyboardInterrupt:
        sys.exit(1)
    except Exception as e:
        logger.error('The following error occured: ' + str(e))
        raise
