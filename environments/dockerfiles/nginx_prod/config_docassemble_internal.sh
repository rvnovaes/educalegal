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
sed -i "s/exitpage: https:\/\/docassemble.org/exitpage: https:\/\/production.educalegal.com.br/" $DACONFIG
sed -i "s/url root: http:\/\/.*/url root: https:\/\/generation.educalegal.com.br/" $DACONFIG
sed -i "s/behind https load balancer: false/behind https load balancer: true/" $DACONFIG
sed -i "s/language: en/language: pt/" $DACONFIG
sed -i "s/locale: en_US.utf8/locale: pt_BR.utf8/" $DACONFIG
sed -i "s/us-words.yml/pt-br-words.yml/" $DACONFIG
sed -i "s/server administrator email: .*/server administrator email: sistemas@educalegal.com.br/" $DACONFIG
sed -i "s/external hostname: .*/external hostname: generation.educalegal.com.br/" $DACONFIG
# Adiciona as linhas no final do arquivo.
echo -e "\n" >> $DACONFIG
echo "admin full width: true" >> $DACONFIG
echo "el environment: production" >> $DACONFIG
echo "el log to console: false"  >> $DACONFIG