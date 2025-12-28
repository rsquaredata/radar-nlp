#!/bin/bash
export PYTHONPATH="$(pwd)/src:${PYTHONPATH}"
streamlit run main.py