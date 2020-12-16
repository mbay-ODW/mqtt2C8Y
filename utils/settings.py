import configparser
from os import path
import logging
import os
import API.inventory
import API.authentication as auth
import subprocess

logger = logging.getLogger('Settings')
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger.info('Logger for settings was initialised')

def basics():
    logger.info('Basic function was called')
    configInit = configparser.ConfigParser(interpolation=None)
    configInit.read('./config/config.ini')
    basics = {}
    basics['tenantInstance'] = configInit['C8Y']['tenantInstance']
    try:
        basics['deviceID'] = subprocess.Popen(["cat", "/etc/hostname"],stdout=subprocess.PIPE).stdout.read().decode('utf-8').replace('\n','')
    except:
        basics['deviceID'] = "6221"
    return basics

def credentials():
    logger.info('Credentials function was called, checking if file exists')
    if path.exists('./config/credentials.key'):
        logger.info('Credential key file exists')
        configCredentials = configparser.ConfigParser(interpolation=None)
        configCredentials.read('./config/credentials.key')
        logger.info('Key file was read')
        credentials = {}
        credentials['c8yUser'] = configCredentials['Credentials']['Username']
        logger.debug('Following user was found in key file: ' + str(credentials['c8yUser']))
        credentials['tenantID'] = configCredentials['Credentials']['tenantID']
        logger.debug('Following user was found in key file: ' + str(credentials['tenantID']))
        credentials['c8yPassword'] = configCredentials['Credentials']['Password']
        return credentials
    else:
        print("No file")


def mqtt():
    if path.exists('./config/credentials.key'):
        configInit = configparser.ConfigParser(interpolation=None)
        configInit.read('./config/config.ini')
        mqtt = {}
        mqtt['broker'] = configInit['MQTT']['broker']
        mqtt['port'] = configInit['MQTT']['port']
        logger.debug('Returning the mqtt settings: %s' % (str(mqtt)))
        return mqtt
    else:
        logger.error('There is no config file, returning False')
        return False
