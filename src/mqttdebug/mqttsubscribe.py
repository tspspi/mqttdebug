import paho.mqtt.client as mqtt
import atexit
import json
import numpy
import argparse

class NumpyArrayEncoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, numpy.ndarray):
			return obj.tolist()
		elif isinstance(obj, datetime):
			return obj.__str__()
		elif isinstance(obj, timedelta):
			return obj.__str__()
		elif isinstance(obj, Webcam):
			return obj.__str__()
		elif isinstance(obj, ElectronGunControl):
			return obj.__str__()
		else:
			return json.JSONEncoder.default(self, obj)


class MqttSubscriber:
	def __init__(self, options):
		self._options = options

		self._mqtt = mqtt.Client(reconnect_on_failure=True)
		self._mqtt.on_connect = self._mqtt_on_connect
		self._mqtt.on_message = self._mqtt_on_message
		self._mqtt.on_disconnect = self._mqtt_on_disconnect

		if "auth" in options:
			if "user" in options['auth']:
				if options['auth']['user'] is not None:
					self._mqtt.username_pw_set(options['auth']['user'], options['auth']['password'])

		if options['broker']['broker'] is None:
			raise ValueError("No broker specified")

		self._mqtt.connect(options['broker']['broker'], options['broker']['port'])

		self._mqtt.loop_forever()

	def _mqtt_on_connect(self, client, userdata, flags, rc):
		if rc == 0:
			if self._options['json']:
				print('{ "event" : "connected" }')
			else:
				print("[MQTT] Connected to broker")

			for top in self._options['topics']:
				client.subscribe(top)
		else:
			if self._options['json']:
				print('{ "event" : "connectfailed" }')
			else:
				print("[MQTT] FAILED to connect to broker")

	def _mqtt_on_disconnect(self, client, userdata, rc=0):
		if self._options['json']:
			print('{ "event" : "disconnect" }')
		else:
			print("[MQTT] Disconnected")

	def _mqtt_on_message(self, client, userdata, msg):
		try:
			msg.payload = str(msg.payload.decode('utf-8', 'ignore'))
			msg.payload = json.loads(msg.payload)
		except json.JSONDecodeError:
			pass

		if self._options['json']:
			if isinstance(msg.payload, str):
				print('{ "topic" : "' + msg.topic + '", "payload" : "' + msg.payload + '" }')
			else:
				print('{ "topic" : "' + msg.topic + '", "payload" : ' + json.dumps(msg.payload, cls=NumpyArrayEncoder) + ' }')
		else:
			print(f"[{msg.topic}]: {msg.payload}")


def mainStartup():
	# Process commandline
	ap = argparse.ArgumentParser(description = 'MQTT message subscriber (debugging tool)')
	ap.add_argument('-c', '--cfg', type=str, required=False, default=None, help="Configuration file to read options from that are processed before command line arguments")
	ap.add_argument('-b', '--broker', type=str, required=False, default=None, help="MQTT broker to connect to")
	ap.add_argument('--port', type=int, required=False, default=1883, help="Port to connect to (default 1883)")
	ap.add_argument('-u', '--user', type=str, required =False, default=None, help="User to use during authentication process")
	ap.add_argument('-p', '--password', type=str, required=False, default=None, help="Password to use during authentication process")
	ap.add_argument('-t', '--topic', type=str, nargs='*', default=[], help="Topics to subscribe to (allowed multiple times)")
	ap.add_argument('-j', '--json', action='store_true', help="Output data as JSON")

	args = ap.parse_args()

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
			if 'topics' in jsonOpts:
				for t in jsonOpts['topics']:
					options['topics'].append(t)

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
	if args.topic is not None:
		for t in args.topic:
			if t not in options['topics']:
				options['topics'].append(t)
	if args.json:
		options['json'] = True

	MqttSubscriber(options)

if __name__ == "__main__":
	mainStartup()