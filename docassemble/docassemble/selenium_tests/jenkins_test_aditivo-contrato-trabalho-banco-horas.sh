#!/bin/bash
source /opt/venvs/educalegal/bin/activate
pytest -n 2 -p no:cacheprovider test_aditivo-contrato-trabalho-banco-horas.py
