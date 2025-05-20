#!/bin/bash
PORT=${1:-8000}
pid=$(lsof -t -i:$PORT)
if [ ! -z "$pid" ]; then
    echo "Killing process on port $PORT"
    kill -9 $pid
fi
