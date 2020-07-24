#!/bin/bash
source /opt/venvs/educalegal/bin/activate
pytest -n 2 -p no:cacheprovider test_termo-de-compromisso-e-rescisao-do-contrato-de-prestacao-de-servicos-educacionais.py
