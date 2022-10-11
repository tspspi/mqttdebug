# Simple MQTT debug helper

This is a simple tool that allows subscribing to an arbitrary number of
MQTT topics as well as publishing to an MQTT broker using a command line
utility.

## Example usage

### Configuration file

The configuration file that's sourced by both tools is supplied in JSON
format:

```
{
	"broker" : {
		"broker" : "example.com",
		"port" : 1883
	},
	"auth" : {
		"user" : "exampleuser",
		"password" : "examplepassword"
	}
}
```

### Subscribing to all topics

Dumping as plain text:

```
$ mqttsubscribe --cfg /path/to/configfile --topic "#"
```

Dumping as JSON:

```
$ mqttsubscribe --cfg /path/to/configfile --topic "#" --json
```

### Subscribing to specific topics

```
$ mqttsubscribe --cfg /path/to/configfile --topic "quakesr/experiment/camera/ebeam/raw/stored" --json
```

### Publishing a message from the CLI

```
$ mqttpublish --cfg /path/to/configfile --topic "examples/testtopic" --payload "Test payload"
```