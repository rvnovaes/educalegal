#!/bin/bash
source /opt/venvs/docassemble-brcomeducalegal/bin/activate
pytest -n 2 -p no:cacheprovider test_contrato-de-inscricao-em-programa-de-viagem-pedagogica.py