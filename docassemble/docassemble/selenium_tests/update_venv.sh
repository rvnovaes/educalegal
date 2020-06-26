#!/bin/bash
source /opt/venvs/educalegal/bin/activate
pip3 install --upgrade -r /var/lib/jenkins/workspace/'Autotest Pipeline'/docassemble/docassemble/selenium_tests/requirements.txt
