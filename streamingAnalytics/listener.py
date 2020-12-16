import paho.mqtt.client as mqtt
import sys
import os
import jsonify
import logging
import utils.settings
import time
import threading
import json
import API.measurement
import API.authentication as auth
import API.identity
import datetime

logger = logging.getLogger('Listener')
logging.basicConfig(level=logging.debug, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger.debug('Logger for MQTT listener was initialised')

def event(topic, payload):
    message = {}
    message['type'] = "c8y_PLC_Data"
    message['source'] = {"id": str(auth.get().internalID)}
    message['time'] = datetime.datetime.strptime(str(datetime.datetime.utcnow()), '%Y-%m-%d %H:%M:%S.%f').isoformat() + "Z"
    try:
        print(payload)
        list = payload.decode('utf-8').replace("\"","").split(',')
        print(list)
        if "Schichtdickensensor" in topic:
            series = {}
            series["Qualitaet"] = {"value": float(list[0])}
            series["Schichtdicke"] = {"value": float(list[1])}
            series["Inkrementalgeber"] = {"value": float(list[2])}
            message[str(topic)] = series
            logger.info(json.dumps(message))
            API.measurement.createMeasurement(json.dumps(message))
        elif "Laserscanner" in topic:
            series = {}
            measurement = {}
            series["Drahtseite kurz"] = {"value": list[0]}
            series["Drahtseite lang"] = {"value": list[1]}
            series["Drahtposition 1"] = {"value": list[2]}
            series["Drahtposition 2"] = {"value": list[3]}
            series["Inkrementalgeber"] = {"value":list[4]}
            measurement[str(topic)] = series
            API.measurement.createMeasurement(json.dumps(message))
        else:
            raise ValueError
    except ValueError as e:
        return logger.error('Not valid json or valid structure')
    except Exception as e:
        logger.error('The following error occured: ' + str(e))


def on_message_msgs(mosq, obj, msg):
    #print("Withing Callback")
    # This callback will only be called for messages with topics that matchs the assigned topics
    try:
        logger.debug('Callback function was initiated')
        logger.debug('The following topic triggered a callback function: %s', msg.topic)
        logger.debug('The following payload arrived: %s', msg.payload)
        logger.debug('Object with Event-Class will be created')
        threadEvent = threading.Thread(target=event, kwargs=dict(topic=msg.topic,payload=msg.payload), daemon=True)
        threadEvent.start()
    except Exception as e:
        logger.error('The following error occured: ' + str(e))


def main():
    try:
        logger.debug('Setting prefix within MQTT broker for machine from config file')
        mqttSettings = utils.settings.mqtt()
        logger.debug('Initialising MQTT client with loaded credentials for listener')
        client = mqtt.Client()
        logger.debug('MQTT client with loaded credentials was initialised')
        client.message_callback_add("raw/#", on_message_msgs)
        logger.debug('Connecting to MQTT Broker')
        client.connect(mqttSettings['broker'], int(mqttSettings['port']), 60)
        client.subscribe("#", 0)
        logger.debug('Start Loop forever and listening')
        client.loop_forever()
    except Exception as e:
        logger.error('The following error occured: ' + str(e))
        client.stop_loop()
        logger.warning('Loop forever stopped, disconnecting')
        client.disconnect()
        logger.debug('disconnected')

def start():
    try:
        while True:
            main()
            logger.error('Main loop left')
            time.sleep(10)
        logger.error('Main loop left')
    except KeyboardInterrupt:
        sys.exit(1)
    except Exception as e:
        logger.error('The following error occured: ' + str(e))
        pass

def stop():
    print("Stopping")
