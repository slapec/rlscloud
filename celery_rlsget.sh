#!/usr/bin/env bash

celery -A rlscloud worker -Q rlsget -n rlsget.%h -l debug