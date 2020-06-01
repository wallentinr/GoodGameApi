#!/bin/bash

cd server
daphne server.asgi:application
