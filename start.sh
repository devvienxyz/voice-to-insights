#!/bin/bash

# python app/warmup_models.py
streamlit run main.py --server.fileWatcherType=watchdog
# streamlit run app/main.py --server.runOnSave true --server.fileWatcherType=watchdog