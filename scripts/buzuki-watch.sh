#!/bin/bash

# https://stackoverflow.com/questions/8699293
# https://unix.stackexchange.com/questions/24952

inotifywait -m "/home/pi/documents/buzuki/songs" -e modify,create,delete,move -r 2>/dev/null |
    while read -r path action file; do
        echo "$action $path$file"
        redis-cli flushall
        # This assumes that buzuki-search is restarted each time it's
        # killed. If we restarted it explicitly here, it would happen
        # multiple times because multiple events fire each time, and
        # everything would be be re-indexed again and again. `redis-cli
        # flushall` does that, but we don't care because redis gets
        # re-indexed lazily. Ideally the buzuki-search server should
        # accept a request to re-index stuff but who has time for that?
        killall -q stop buzuki-search
    done
