#!/bin/bash
source /opt/venvs/docassemble-brcomeducalegal/bin/activate
pytest -n 2 -p no:cacheprovider test_termo-de-acordo-individual-de-banco-de-horas-mp-927-2020.py