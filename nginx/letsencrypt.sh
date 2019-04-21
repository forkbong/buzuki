#!/bin/bash

if [[ $EUID -ne 0 ]]; then
    echo please run as root
    exit 1
fi

function finish {
    nginx
}
trap finish EXIT
nginx -s stop

if ! certbot renew -nv --standalone > /var/log/letsencrypt/renew.log 2>&1; then
    echo Automated renewal failed:
    cat /var/log/letsencrypt/renew.log
    exit 1
fi
