#!/bin/bash
source /opt/venvs/educalegal/bin/activate
pytest -n 2 -p no:cacheprovider pytest -v