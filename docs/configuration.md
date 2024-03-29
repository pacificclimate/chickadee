# Configuration
- [Command-line options](#command-line-options)
- [Use a custom configuration file](#use-a-custom-configuration-file)

## Command-line options
You can overwrite the default [PyWPS](http://pywps.org/) configuration by using command-line options.
See the chickadee help which options are available:
```
(venv)$ chickadee start --help
--hostname HOSTNAME        hostname in PyWPS configuration.
--port PORT                port in PyWPS configuration.
```
Start service with different hostname and port:
```
(venv)$ chickadee start --hostname localhost --port 5000
```

## Use a custom configuration file
You can overwrite the default [PyWPS](http://pywps.org/) configuration by providing your own PyWPS configuration file (just modifiy the options you want to change). Use one of the existing `sample-*.cfg` files as example and copy them to `etc/custom.cfg`.

For example change the hostname (*demo.org*) and logging level:
```
$ cd chickadee
$ vim etc/custom.cfg
$ cat etc/custom.cfg
[server]
url = http://demo.org:5000/wps
outputurl = http://demo.org:5000/outputs

[logging]
level = DEBUG
```
Start the service with your custom configuration:
```
# start the service with this configuration
(venv)$ chickadee start -c etc/custom.cfg
```
