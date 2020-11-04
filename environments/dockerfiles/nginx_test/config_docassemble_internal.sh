#!/bin/bash
DACONFIGFILE='/usr/share/docassemble/config/config.yml'
# Edita o arquivo /etc/timezone e troca a primeira linha por America/Sao_Paulo
sed -i "1 s/^.*$/America/Sao_Paulo" /etc/timezone
# Reconfigura a timezone
dpkg-reconfigure -f noninteractive tzdata
 # Edita o arquivo de configuração do docassemble
sed -i "s/exitpage: https:\/\/docassemble.org/exitpage: https:\/\/test.educalegal.com.br/" $DACONFIGFILE
sed -i "s/behind https load balancer: false/behind https load balancer: true/" $DACONFIGFILE
sed -i "s/language: en/language: pt/" $DACONFIGFILE
sed -i "s/locale: en_US.utf8/locale: pt_BR.utf8/" $DACONFIGFILE
sed -i "s/us-words.yml/pt-br-words.yml/" $DACONFIGFILE
# Adiciona as linhas no final do arquivo.
echo "admin full width: true" >> $DACONFIGFILE
echo "el environment: test" >> $DACONFIGFILE
echo "el log to console: true"  >> $DACONFIGFILE
echo "allow non-idempotent questions: false" >> $DACONFIGFILE