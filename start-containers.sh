#!/bin/bash -eux
docker build -t meetup-bot:latest .
docker run -d -p 50000:50000 --restart unless-stopped meetup-bot
