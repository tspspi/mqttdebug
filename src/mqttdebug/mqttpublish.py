import paho.mqtt.client as mqtt
import atexit
import json
import numpy
import argparse


targetMsg_Topic = None
targetMsg_Payload = None

def mainStartup():
	global targetMsg_Payload, targetMsg_Topic

	ap = argparse.ArgumentParser(description = 'MQTT message subscriber (debugging tool)')
	ap.add_argument('-c', '--cfg', type=str, required=False, default=None, help="Configuration file to read options from that are processed before command line arguments")
	ap.add_argument('-b', '--broker', type=str, required=False, default=None, help="MQTT broker to connect to")
	ap.add_argument('--port', type=int, required=False, default=1883, help="Port to connect to (default 1883)")
	ap.add_argument('-u', '--user', type=str, required =False, default=None, help="User to use during authentication process")
	ap.add_argument('-p', '--password', type=str, required=False, default=None, help="Password to use during authentication process")
	ap.add_argument('-t', '--topic', type=str, required=True, help="Topic to publish to")
	ap.add_argument('-d', '--payload', type=str, default=None, help="Payload to transmit (raw string)")

	_mqtt = mqtt.Client(reconnect_on_failure=True)
	_mqtt.on_connect = _mqtt_on_connect
	_mqtt.on_message = _mqtt_on_message
	_mqtt.on_disconnect = _mqtt_on_disconnect

	args = ap.parse_args()

	targetMsg_Topic = args.topic
	targetMsg_Payload = args.payload

	options = {
		'broker' : {
			'broker' : None,
			'port' : 1883
		},
		'auth' : {
			'user' : None,
			'password' : None
		},
		'topics' : [ ],
		'json' : False
	}

	# If specified load a configuration file ...
	if args.cfg is not None:
		with open(args.cfg) as cfgfile:
			jsonOpts = json.load(cfgfile)

			if 'broker' in jsonOpts:
				if 'broker' in jsonOpts['broker']:
					options['broker']['broker'] = jsonOpts['broker']['broker']
				if 'port' in jsonOpts['broker']:
					newPort = int(jsonOpts['broker']['port'])
					if (newPort < 1) or (newPort > 65535):
						raise ValueError("Port value out of allowed range")
					options['broker']['port'] = newPort
			if 'auth' in jsonOpts:
				if 'user' in jsonOpts['auth']:
					options['auth']['user'] = jsonOpts['auth']['user']
				if 'password' in jsonOpts['auth']:
					options['auth']['password'] = jsonOpts['auth']['password']

	# Process commandline arguments
	if args.broker is not None:
		options['broker']['broker'] = args.broker
	if args.port is not None:
		if (args.port < 1) or (args.port > 65535):
			raise ValueError("Port value out of allowed range")
		options['broker']['port'] = args.port
	if args.user is not None:
		options['auth']['user'] = args.user
	if args.password is not None:
		options['auth']['password'] = args.password

	if "auth" in options:
		if "user" in options['auth']:
			if options['auth']['user'] is not None:
				_mqtt.username_pw_set(options['auth']['user'], options['auth']['password'])


	_mqtt.connect(options['broker']['broker'], options['broker']['port'])

	_mqtt.loop_forever()


def _mqtt_on_connect(client, userdata, flags, rc):
	global targetMsg_Payload, targetMsg_Topic

	if rc == 0:
		print("[MQTT] Connected to broker")
	else:
		print("[MQTT] FAILED to connect to broker")

	print(f"Publish to {targetMsg_Topic}")

	if targetMsg_Payload is None:
		client.publish(targetMsg_Topic, qos=0, retain=False)
	else:
		client.publish(targetMsg_Topic, payload=targetMsg_Payload, qos=0, retain=False)

	client.disconnect()

def _mqtt_on_message(client, userdata, msg):
	pass

def _mqtt_on_disconnect(client, userdata, rc=0):
	client.loop_stop()


if __name__ == "__main__":
	mainStartup()