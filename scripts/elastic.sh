#!/bin/bash

set -e

VERSION=7.9.2
DIRECTORY=elasticsearch-$VERSION
TARBALL=elasticsearch-$VERSION-linux-x86_64.tar.gz

usage() {
    echo "Usage: $(basename "$0") COMMAND"
    echo ""
    echo "Commands:"
    echo "  install"
    echo "  start"
    echo "  stop"
    echo "  status"
    exit
}

install_elasticsearch() {
    if [[ -d $DIRECTORY ]]; then
        echo "Directory $DIRECTORY already exists"
        exit 1
    fi
    wget https://artifacts.elastic.co/downloads/elasticsearch/$TARBALL
    tar xf $TARBALL
    rm $TARBALL
    sed -i -e 's/1g/256m/' $DIRECTORY/config/jvm.options
}

start_elasticsearch() {
    if running; then
        echo "elasticsearch is already running"
        exit 1
    fi
    $DIRECTORY/bin/elasticsearch -d -p /tmp/elasticsearch.pid
}

stop_elasticsearch() {
    if ! running; then
        echo "elasticsearch is not running"
        exit 1
    fi
    kill "$(cat /tmp/elasticsearch.pid)"
}

running() {
    pgrep -a java | grep elasticsearch > /dev/null
    return $?
}

case $1 in
    install)
        install_elasticsearch
        ;;
    start)
        start_elasticsearch
        ;;
    stop)
        stop_elasticsearch
        ;;
    status)
        if running; then
            echo "elasticsearch is running"
        else
            echo "elasticsearch is not running"
        fi
        ;;
    *)
        usage
        ;;
esac
