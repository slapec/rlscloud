#!/usr/bin/env bash

celery -A rlscloud worker -Q rlscloud -n rlscloud.%h -l info