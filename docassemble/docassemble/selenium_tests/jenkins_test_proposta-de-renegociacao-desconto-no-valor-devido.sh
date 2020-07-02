#!/bin/bash
source /opt/venvs/educalegal/bin/activate
pytest -n 2 -p no:cacheprovider test_proposta-de-renegociacao-desconto-no-valor-devido.py