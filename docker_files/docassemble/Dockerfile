FROM jhpyle/docassemble:stable

USER www-data
RUN LC_CTYPE=C.UTF-8 LANG=C.UTF-8 \
bash -c \
"source /usr/share/docassemble/local3.6/bin/activate \
&& pip3 install --upgrade \
   docassemble-wrappers \
   num2words \
   validator-collection-br \
   retry-requests"
ENV \
CONTAINERROLE="all" \
LOCALE="pt_BR.UTF-8 UTF-8" \
TIMEZONE="America/Sao_Paulo" \
DAPYTHONVERSION="3"

USER root
CMD ["/usr/bin/supervisord", "-n", "-c", "/etc/supervisor/supervisord.conf"]
