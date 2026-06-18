#!/bin/bash

cd /app
supervisord -n -c ./supervisord.conf
