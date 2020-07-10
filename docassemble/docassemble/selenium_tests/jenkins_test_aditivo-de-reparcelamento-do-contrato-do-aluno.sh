#!/bin/bash
source /opt/venvs/educalegal/bin/activate
pytest -n 2 -p no:cacheprovider test_aditivo-de-reparcelamento-do-contrato-do-aluno.py
