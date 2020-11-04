#!/bin/bash
TZF="/etc/timezone"
DACONFIG="/usr/share/docassemble/config/config.yml"
# Apaga o arquivo /etc/timezone e cria novo arquivpo troca a primeira linha por America/Sao_Paulo
rm $TZF
touch $TZF
echo "America/Sao_Paulo" >> $TZF
# Reconfigura a timezone
dpkg-reconfigure -f noninteractive tzdata
# Edita o arquivo de configuração do docassemble
sed -i "s/exitpage: https:\/\/docassemble.org/exitpage: https:\/\/test.educalegal.com.br/" $DACONFIG
sed -i "s/behind https load balancer: false/behind https load balancer: true/" $DACONFIG
sed -i "s/language: en/language: pt/" $DACONFIG
sed -i "s/locale: en_US.utf8/locale: pt_BR.utf8/" $DACONFIG
sed -i "s/us-words.yml/pt-br-words.yml/" $DACONFIG
# Adiciona as linhas no final do arquivo.
{
  echo -e "\n"
  "admin full width: true"
  "el environment: test"
  "el log to console: true"
  "allow non-idempotent questions: false"
} >> $DACONFIG