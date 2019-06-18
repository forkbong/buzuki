#!/bin/bash

set -e

config_dir=/etc/systemd/system/buzuki.service.d
config=$config_dir/local.conf

sudo mkdir -p $config_dir

echo "[Service]" > /tmp/config
echo "Environment=\"BUZUKI_PWHASH=$BUZUKI_PWHASH\"" >> /tmp/config
echo "Environment=\"BUZUKI_SECRET_KEY=$BUZUKI_SECRET_KEY\"" >> /tmp/config

sudo mv /tmp/config $config

for service in *.service; do
    echo "$service"
    sudo systemctl stop "$service" || true
    sudo cp -f "$service" /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable --now "$service"
done
