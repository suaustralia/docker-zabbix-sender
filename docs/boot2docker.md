# Using with Boot2docker

`docker-zabbix-sender` alsos supports MacOs, where Docker daemon is running on a virtual machine.

First run boot2docker in your shell:
```bash
$ $(boot2docker shellinit)
Writing /Users/you/.boot2docker/certs/boot2docker-vm/ca.pem
Writing /Users/you/.boot2docker/certs/boot2docker-vm/cert.pem
Writing /Users/you/.boot2docker/certs/boot2docker-vm/key.pem
export DOCKER_HOST=tcp://192.168.59.103:2376
export DOCKER_CERT_PATH=/Users/you/.boot2docker/certs/boot2docker-vm
export DOCKER_TLS_VERIFY=1
```

You can then use `docker-zabbix-sender` in the same session, which reads those variables to connect to the proper Docker daemon.

If you're encountering the following error:
`SSLError: hostname '192.168.59.103' doesn't match 'boot2docker'`, you can:

1. Add an entry to your /etc/hosts file matching boot2docker to the daemon's IP
1. Disable hostname validation (but please consider the security implications
   in doing this)

```shell
$ docker-zabbix-sender --tlsverify=false ...
```
