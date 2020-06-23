#!/bin/bash
source /opt/venvs/docassemble-brcomeducalegal/bin/activate
pip install -r /var/lib/jenkins/workspace/Autotest/docassemble/selenium_tests/requirements.txt
cd /var/lib/jenkins/workspace/Autotest/docassemble/selenium_tests
pytest
