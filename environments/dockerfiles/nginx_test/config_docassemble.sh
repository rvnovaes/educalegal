#!/bin/bash
docker exec docassemble mkdir -p /opt/config_docassemble_internal
docker cp config_docassemble_internal.sh docassemble:/opt/config_docassemble_internal
docker exec docassemble chmod +x /opt/config_docassemble_internal/config_docassemble_internal.sh
docker exec docassemble /opt/config_docassemble_internal/config_docassemble_internal.sh
docker restart docassemble