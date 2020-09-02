#!/bin/bash
source /opt/venvs/educalegal/bin/activate
pytest -n 2 -p no:cacheprovider test_termo-de-retificacao-de-acordo-individual-de-trabalho-coronavirus.py
