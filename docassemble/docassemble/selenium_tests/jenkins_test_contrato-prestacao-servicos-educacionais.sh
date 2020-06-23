#!/bin/bash
source /opt/venvs/docassemble-brcomeducalegal/bin/activate
pytest -n 2 -p no:cacheprovider test_contrato-prestacao-servicos-educacionais.py