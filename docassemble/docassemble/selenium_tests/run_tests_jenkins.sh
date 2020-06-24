#!/bin/bash
source /opt/venvs/educalegal/bin/activate
pip3 install -r /var/lib/jenkins/workspace/Autotest/docassemble/selenium_tests/requirements.txt
cd /var/lib/jenkins/workspace/Autotest/docassemble/selenium_tests
pytest
