#!/bin/bash

python app/warmup_models.py
streamlit run app/main.py --server.port 8501 --server.address localhost --server.runOnSave=true --logger.level=debug --global.developmentMode=false --server.fileWatcherType=none
