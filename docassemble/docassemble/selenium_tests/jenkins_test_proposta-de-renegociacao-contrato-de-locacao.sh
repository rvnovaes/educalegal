#!/bin/bash
source /opt/venvs/educalegal/bin/activate
pytest -n 2 -p no:cacheprovider test_proposta-de-renegociacao-contrato-de-locacao.py