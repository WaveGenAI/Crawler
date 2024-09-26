#!/bin/sh


XVFB_WHD=${XVFB_WHD:-1280x720x16}

Xvfb :99 -ac -screen 0 $XVFB_WHD -nolisten tcp > /dev/null 2>&1 &
sleep 2

# Run python script on display 0
DISPLAY=:99 python multi_crawler/crawlers/poo_gen.py