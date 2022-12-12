#!/bin/bash

export TERM=xterm
tmux new -d -s lab3 \; split-window -h ;\ 
tmux send-keys -t lab3.0 "streamlit run dashboard.py --server.port=80" ENTER
tmux send-keys -t lab3.1 "uvicorn src.main:app" ENTER

tmux a -t lab3
