# Installation
- [Install from Github](#install-from-github)
- [Install poethepoet](#install-poethepoet)
- [Start `chickadee` PyWPS service](#start-chickadee-pywps-service)
- [Run `chickadee` as Docker container](#run-chickadee-as-docker-container)
- [Use Ansible to deploy `chickadee` on your System](#use-ansible-to-deploy-chickadee-on-your-system)

## Install from GitHub

Check out code from the chickadee GitHub repo and start the installation:
```
$ git clone https://github.com/pacificclimate/chickadee.git
$ cd chickadee
```
## Install poethepoet
A task runner that works well with Poetry to replace Makefiles. 

```
$ python3 -m pip install --user pipx
$ python3 -m pipx ensurepath # Ensure directory where pipx stores apps is in your PATH environment variable 
$ pipx install poethepoet # Install globally
```
Install system libraries and dependencies:
```
$ poe install-apt
$ poe install-r-pkgs

```
Install requirements:
```
poe install
```

For development you can use this command:
```
poe develop
```

## Start `chickadee` PyWPS service
After successful installation you can start the service using the `chickadee` command-line.

```
poe start
```
The deployed WPS service is by default available on:

http://localhost:5000/wps?service=WPS&version=1.0.0&request=GetCapabilities.

NOTE:: Remember the process ID (PID) so you can stop the service with `kill PID`.

You can find which process uses a given port using the following command (here for port `5000`):

```
$ netstat -nlp | grep :5000
```

Check the log files for errors:
```
$ tail -f  pywps.log
```
... or do it the lazy way

You can also use the `Poe` to check the status and stop the service:
```
$ poe status
$ tail -f pywps.log
$ poe stop
```

## Run `chickadee` as Docker container
You can also run `chickadee` as a Docker container.
```
$ docker-compose build
$ docker-compose up
```

`chickadee` will be available on port `8102`.

## Use Ansible to deploy `chickadee` on your System
Use the [Ansible playbook](http://ansible-wps-playbook.readthedocs.io/en/latest/index.html) for PyWPS to deploy `chickadee` on your system.
