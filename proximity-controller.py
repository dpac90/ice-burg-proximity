#!/usr/bin/env python
import time
import pika
import RPi.GPIO as GPIO
import yaml
from optparse import OptionParser
from proximity import Sensor

# GPIO
GPIO.setmode(GPIO.BCM)
DEBUG = 1

#
# set up the SPI interface pins
#
# ultrasonic sensor connected to adc #0
#
ultrasonic_adc_0 = 0
sensor_msg_delay = 0
msg_bus_host = ''
iceburg_id  = ''
sensor_trigger_distance_limit = 0

def main():
    parser = OptionParser()
    parser.add_option('-c', '--yaml-config', dest='config', help="The configuration file for the sensors")
    (options, args) = parser.parse_args()

    if options.config:
        try:
            sensors = init_sensors(options.config)
            print msg_bus_host
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=msg_bus_host))
            channel = connection.channel()
            channel.exchange_declare(exchange='events', type='topic')

            while True:
                for sensor in sensors:
                    distance = sensor.readadc()
                    print "The distance of sensor", sensor.number, " is :", distance
                    publish_msg(channel, sensor, distance)

                #
                # hang out and do nothing, based on the configured delay
                #
                time.sleep(sensor_msg_delay)
        
        except KeyboardInterrupt:
            GPIO.cleanup()
    else:
        parser.print_help()

def publish_msg(channel, sensor, distance):
    key = '{}.proximity.event'.format(iceburg_id)
    ms = int(round(time.time() * 1000))
    body = '{{"type":"PROXIMITY", "personPresent": true, "icebergId":"{}", "time":{}}}'.format(iceburg_id, ms)
    print body

    #
    # Publish only when within distance of the limit
    #
    if distance <= sensor_trigger_distance_limit:
        channel.basic_publish(exchange='events', routing_key=(key), body=body)
        print "Publishing the sensor {} event".format(body)
    else:
        print "{} is a distance that is not in range".format(distance)

def load(yml):
    return yaml.load(open(yml, 'r'))

def init_sensors(config_yml):
    global ultrasonic_adc_0
    global msg_bus_host
    global sensor_msg_delay
    global iceburg_id
    global sensor_trigger_distance_limit

    config = load(config_yml)
    sensor_trigger_distance_limit = config['sensor_trigger_distance_limit']
    iceburg_id = config['iceburg_id']
    sensor_msg_delay = config['sensor_msg_delay']
    msg_bus_host = config['msg_bus_host']
    sensor_configs = config['sensors']

    return map(lambda c: Sensor(c, ultrasonic_adc_0), sensor_configs)
   
if __name__ == "__main__":
    main()

