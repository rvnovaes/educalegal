#!/bin/bash
# Renova o certificado e reinicia o nginx
docker exec nginx certbot renew && docker restart nginx