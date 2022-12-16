#!/bin/bash

streamlit run dashboard.py --server.port=80 &>/dev/null &
uvicorn src.main:app &>/dev/null &
