#!/bin/bash

python app/warmup_models.py
streamlit run app/main.py --server.port 8501 --server.address 0.0.0.0 --server.runOnSave=true
