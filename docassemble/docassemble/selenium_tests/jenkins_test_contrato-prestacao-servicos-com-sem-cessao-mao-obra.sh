#!/bin/bash
source /opt/venvs/docassemble-brcomeducalegal/bin/activate
pytest -n 2 -p no:cacheprovider test_contrato-prestacao-servicos-com-sem-cessao-mao-obra.py