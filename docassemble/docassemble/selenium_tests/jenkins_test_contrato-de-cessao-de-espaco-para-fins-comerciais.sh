#!/bin/bash
source /opt/venvs/educalegal/bin/activate
pytest -n 2 -p no:cacheprovider test_contrato-de-cessao-de-espaco-para-fins-comerciais.py
