#!/usr/bin/env bash

celery -A rlscloud worker -Q encode -n encode.%h