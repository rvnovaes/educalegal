import re


def config_hosts():
    """
    Altera o arquivo /etc/hosts.txt para inserir as linhas para o educalegal, docassemble e ged.
    :return:
    """
    # Menu de Desenvolvimento
    menu_regex = "127.0.1.1 +(menu)$"
    menu_entry = False
    # Front End
    educalegal_regex = "127.0.1.1 +(educalegal)$"
    educalegal_entry = False
    # Back End
    api_regex = "127.0.1.1 +(api)$"
    api_entry = False
    db_regex = "127.0.1.1 +(db)$"
    db_entry = False
    apiflower_regex = "127.0.1.1 +(apiflower)$"
    apiflower_entry = False
    apirabbitmq_regex = "127.0.1.1 +(apirabbitmq)$"
    apirabbitmq_entry = False
    apimongo_regex = "127.0.1.1 +(apimongo)$"
    apimongo_entry = False
    apimongoexpress_regex = "127.0.1.1 +(apimongoexpress)$"
    apimongoexpress_entry = False
    # GED
    ged_regex = "127.0.1.1 +(ged)$"
    ged_entry = False
    gedceleryflower_regex = "127.0.1.1 +(gedceleryflower)$"
    gedceleryflower_entry = False
    # Docassemble
    docassemble_regex = "127.0.1.1 +(docassemble)$"
    docassemble_entry = False
    # DB

    with open("/etc/hosts") as hosts_file:
        for line in hosts_file:
            line = line.rstrip()  # remove '\n' at end of line
            if re.match(menu_regex, line) is not None:
                print("Já existe configuração para o Menu em /etc/hosts.txt. Saltando...")
                menu_entry = True
            if re.match(educalegal_regex, line) is not None:
                print("Já existe configuração para o Educalegal em /etc/hosts.txt. Saltando...")
                educalegal_entry = True
            if re.match(api_regex, line) is not None:
                print("Já existe configuração para a Api em /etc/hosts.txt. Saltando...")
                api_entry = True
            if re.match(db_regex, line) is not None:
                print("Já existe configuração para a Api em /etc/hosts.txt. Saltando...")
                db_entry = True
            if re.match(apiflower_regex, line) is not None:
                print("Já existe configuração para o Flower da api em /etc/hosts.txt. Saltando...")
                apiflower_entry = True
            if re.match(apirabbitmq_regex, line) is not None:
                print("Já existe configuração para o Rabbitmq da api em /etc/hosts.txt. Saltando...")
                apirabbitmq_entry = True
            if re.match(apimongo_regex, line) is not None:
                print("Já existe configuração para o Mongo em /etc/hosts.txt. Saltando...")
                apimongo_entry = True
            if re.match(apimongoexpress_regex, line) is not None:
                print("Já existe configuração para o Mongo Express em /etc/hosts.txt. Saltando...")
                apimongoexpress_entry = True
            if re.match(ged_regex, line) is not None:
                print("Já existe configuração para o Ged em /etc/hosts.txt. Saltando...")
                ged_entry = True
            if re.match(gedceleryflower_regex, line) is not None:
                print("Já existe configuração para o Flower do Ged em /etc/hosts.txt. Saltando...")
                gedceleryflower_entry = True
            if re.match(docassemble_regex, line) is not None:
                print("Já existe configuração para o Docassemble em /etc/hosts.txt. Saltando...")
                docassemble_entry = True

    if not menu_entry:
        print("Não há entrada para o Menu em /etc/hosts.txt. Criando... ")
        with open("/etc/hosts", "a") as writeable_hosts_file:
            writeable_hosts_file.write("127.0.1.1  menu\n")
    if not educalegal_entry:
        print("Não há entrada para o Educalegal em /etc/hosts.txt. Criando... ")
        with open("/etc/hosts", "a") as writeable_hosts_file:
            writeable_hosts_file.write("127.0.1.1  educalegal\n")
    if not api_entry:
        print("Não há entrada para a Api em /etc/hosts.txt. Criando... ")
        with open("/etc/hosts", "a") as writeable_hosts_file:
            writeable_hosts_file.write("127.0.1.1  api\n")
    if not db_entry:
        print("Não há entrada para o DB em /etc/hosts.txt. Criando... ")
        with open("/etc/hosts", "a") as writeable_hosts_file:
            writeable_hosts_file.write("127.0.1.1  db\n")
    if not apiflower_entry:
        print("Não há entrada para o Flower da api em /etc/hosts.txt. Criando... ")
        with open("/etc/hosts", "a") as writeable_hosts_file:
            writeable_hosts_file.write("127.0.1.1  apiflower\n")
    if not apirabbitmq_entry:
        print("Não há entrada para o Rabbitmq da api em /etc/hosts.txt. Criando... ")
        with open("/etc/hosts", "a") as writeable_hosts_file:
            writeable_hosts_file.write("127.0.1.1  apirabbitmq\n")
    if not apimongo_entry:
        print("Não há entrada para o Mongo em /etc/hosts.txt. Criando... ")
        with open("/etc/hosts", "a") as writeable_hosts_file:
            writeable_hosts_file.write("127.0.1.1  apimongo\n")
    if not apimongoexpress_entry:
        print("Não há entrada para o Mongo Express em /etc/hosts.txt. Criando... ")
        with open("/etc/hosts", "a") as writeable_hosts_file:
            writeable_hosts_file.write("127.0.1.1  apimongoexpress\n")
    if not ged_entry:
        print("Não há entrada para o Ged em /etc/hosts.txt. Criando... ")
        with open("/etc/hosts", "a") as writeable_hosts_file:
            writeable_hosts_file.write("127.0.1.1  ged\n")
    if not gedceleryflower_entry:
        print("Não há entrada para o Flower do Ged em /etc/hosts.txt. Criando... ")
        with open("/etc/hosts", "a") as writeable_hosts_file:
            writeable_hosts_file.write("127.0.1.1  gedceleryflower\n")
    if not docassemble_entry:
        print("Não há entrada para o Docassemble em /etc/hosts.txt. Criando... ")
        with open("/etc/hosts", "a") as writeable_hosts_file:
            writeable_hosts_file.write("127.0.1.1  docassemble\n")


if __name__ == '__main__':
    config_hosts()
