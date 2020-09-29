import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from .web_test import WebTest
from .parameters import CNPJ, CPF, RUN_TESTS_AUTOTEST, RUN_TESTS_PRODUCTION


class TestContratodeInscricaoemProgramadeViagemPedagogica(WebTest):
    # indica em qual ambiente o teste deve ser executado
    environment = list()
    if RUN_TESTS_AUTOTEST:
        environment.append(("https://apptest.educalegal.com.br/", "autotest@educalegal.com.br", "Silex2109",
                            "Autotest_Contrato de viagem de formação pedagógica"),)
    if RUN_TESTS_PRODUCTION:
        environment.append(("https://app.educalegal.com.br/", "maria.secretaria@educalegal.com.br", "silex@568",
                            "Contrato de viagem de formação pedagógica"),)

    @pytest.mark.parametrize("server,user,password,document_name", environment,)
    def test_contratodeInscricaoemProgramadeViagemPedagogica(self, server, user, password, document_name):
        self.driver.get(server)
        self.driver.find_element(By.ID, "id_login").click()
        self.driver.find_element(By.ID, "id_login").send_keys(user)
        self.driver.find_element(By.ID, "id_password").send_keys(password)
        self.driver.find_element(By.CSS_SELECTOR, ".btn").click()
        self.driver.find_element(By.ID, "id_name").send_keys(document_name)
        self.driver.find_element(By.CSS_SELECTOR, ".btn-primary").click()
        self.vars["window_handles"] = self.driver.window_handles
        self.driver.find_element(By.CSS_SELECTOR, ".btn-success").click()
        self.vars["win7220"] = self.wait_for_window(2000)
        self.driver.switch_to.window(self.vars["win7220"])
        try:
            self.driver.find_element(By.XPATH, "//h1[contains(.,'Escolha a escola')]")
            self.wait.until(
                EC.text_to_be_present_in_element((By.XPATH, "//h1"), "Escolha a escola")
            )
            self.driver.find_element(
                By.XPATH, "//form[@id='daform']/fieldset/div/div/label"
            ).click()
            self.driver.find_element(
                By.XPATH, "//button[contains(.,'Continuar')]"
            ).click()
        except NoSuchElementException:
            pass
        self.wait.until(
            EC.text_to_be_present_in_element((By.XPATH, "//h1"), "E-mail da Escola:"))
        self.driver.find_element(By.XPATH, "//form[@id=\'daform\']/div[3]/div/a").click()
        self.driver.find_element(By.XPATH, "//form[@id=\'daform\']/div[2]/div/input").clear()
        self.driver.find_element(By.XPATH, "//form[@id=\'daform\']/div[2]/div/input").send_keys("educalegal@gmail.com")
        self.driver.find_element(By.XPATH, "//button[contains(.,\'Continuar\')]").click()
        self.wait.until(
            EC.text_to_be_present_in_element((By.XPATH, "//h1"), "E-mail da Escola:"))
        self.driver.find_element(By.XPATH, "//button[contains(.,\'Continuar\')]").click()
        self.wait.until(
            EC.text_to_be_present_in_element((By.XPATH, "//h1"), "Dados da contratada")
        )
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[2]/div/input"
        ).send_keys("EDUCA LEGAL 01")
        for k in CNPJ:
            self.driver.find_element(
                By.XPATH, "//form[@id='daform']/div[3]/div/input"
            ).send_keys(k)
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[4]/div/input"
        ).send_keys("escola.educalegal@gmail.com")
        self.driver.find_element(By.XPATH, "//button[contains(.,'Continuar')]").click()
        self.wait.until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//h1"), "Endereço do(a) EDUCA LEGAL 01"
            )
        )
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[2]/div/input"
        ).send_keys("30180-090")
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[4]/div/input"
        ).send_keys("683")
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[5]/div/input"
        ).send_keys("APARTAMENTO 01")
        self.wait.until(
            EC.text_to_be_present_in_element_value(
                (By.XPATH, "//form[@id='daform']/div[3]/div/input"), "Rua Paracatu",
            )
        )
        self.driver.find_element(By.XPATH, "//button[contains(.,'Continuar')]").click()
        self.wait.until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//h1"), "Número de participantes"
            )
        )
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[2]/div/input"
        ).clear()
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[2]/div/input"
        ).send_keys("2")
        self.driver.find_element(By.XPATH, "//button[contains(.,'Continuar')]").click()
        self.wait.until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//h1"), "Dados do(a) primeiro(a) participante"
            )
        )
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[2]/div/input"
        ).send_keys("JOSUÉ SIGNATARIO")
        for k in CPF:
            self.driver.find_element(
                By.XPATH, "//form[@id='daform']/div[3]/div/input"
            ).send_keys(k)
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[4]/div/input"
        ).send_keys("423423423")
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[6]/div/fieldset/label"
        ).click()
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[7]/div/input"
        ).click()
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[7]/div/input"
        ).send_keys("2020-04-15")
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[8]/div/input"
        ).send_keys("PROFESSOR")
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[9]/div/input"
        ).send_keys("ESCOLA")
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[10]/div/input"
        ).send_keys("PROFESSOR")
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[11]/div/input"
        ).send_keys("32132133")
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[12]/div/input"
        ).send_keys("24342423")
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[13]/div/input"
        ).send_keys("josue.signatario@gmail.com")
        self.driver.find_element(By.XPATH, "//button[contains(.,'Continuar')]").click()
        self.wait.until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//h1"), "Endereço do(a) JOSUÉ SIGNATARIO"
            )
        )
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[2]/div/input"
        ).send_keys("30180-090")
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[4]/div/input"
        ).send_keys("683")
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[5]/div/input"
        ).send_keys("apartamento 01")
        self.wait.until(
            EC.text_to_be_present_in_element_value(
                (By.XPATH, "//form[@id='daform']/div[3]/div/input"), "Rua Paracatu",
            )
        )
        self.driver.find_element(By.XPATH, "//button[contains(.,'Continuar')]").click()
        self.wait.until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//h1"), "Dados do(a) segundo(a) participante"
            )
        )
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[2]/div/input"
        ).send_keys("FRANCISCO SIGNATÁRIO")
        for k in CPF:
            self.driver.find_element(
                By.XPATH, "//form[@id='daform']/div[3]/div/input"
            ).send_keys(k)
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[4]/div/input"
        ).send_keys("4234234")
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[6]/div/fieldset/label/span[2]"
        ).click()
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[7]/div/input"
        ).send_keys("2020-04-15")
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[8]/div/input"
        ).send_keys("PROFESSOR")
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[9]/div/input"
        ).send_keys("ESCOLA")
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[10]/div/input"
        ).send_keys("PROFESSOR")
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[11]/div/input"
        ).send_keys("3423432423")
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[12]/div/input"
        ).send_keys("4234234324")
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[13]/div/input"
        ).send_keys("fiador.educalegal@gmail.com")
        self.driver.find_element(By.XPATH, "//button[contains(.,'Continuar')]").click()
        self.wait.until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//h1"), "Endereço do(a) FRANCISCO SIGNATÁRIO"
            )
        )
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[2]/div/input"
        ).send_keys("30180-090")
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[4]/div/input"
        ).send_keys("683")
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[5]/div/input"
        ).send_keys("APARTAMENTO 01")
        self.wait.until(
            EC.text_to_be_present_in_element_value(
                (By.XPATH, "//form[@id='daform']/div[3]/div/input"), "Rua Paracatu",
            )
        )
        self.driver.find_element(By.XPATH, "//button[contains(.,'Continuar')]").click()
        self.wait.until(
            EC.text_to_be_present_in_element((By.XPATH, "//h1"), "Participantes:")
        )
        self.driver.find_element(By.XPATH, "//button[contains(.,'Continuar')]").click()
        self.wait.until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//h1"), "Número de contatos de emergência"
            )
        )
        self.driver.find_element(By.XPATH, "//button[contains(.,'Continuar')]").click()
        self.wait.until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//h1"), "Dados do(a) primeiro(a) contato de emergência"
            )
        )
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[2]/div/input"
        ).send_keys("MIGUEL")
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[3]/div/input"
        ).send_keys("423423423")
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[4]/div/input"
        ).send_keys("423423423")
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[5]/div/input"
        ).send_keys("miguel@gmail.com")
        self.driver.find_element(By.XPATH, "//button[contains(.,'Continuar')]").click()
        self.wait.until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//h1"), "Informações do programa"
            )
        )
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[2]/div/input"
        ).send_keys("Centro de convenções Ulisses Guimarães")
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[3]/div/input"
        ).send_keys("Hotel Hilton")
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[4]/div/input"
        ).send_keys("2020-04-15")
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[5]/div/input"
        ).send_keys("2020-04-30")
        self.driver.find_element(By.XPATH, "//button[contains(.,'Continuar')]").click()
        self.wait.until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//h1"), "Informações Financeiras"
            )
        )
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[2]/div/fieldset/label[2]"
        ).click()
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[3]/div/div/input"
        ).send_keys("3000")
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[4]/div/fieldset/label[2]/span[2]"
        ).click()
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[5]/div/fieldset/label"
        ).click()
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[6]/div/input"
        ).send_keys("Escola")
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[7]/div/fieldset/label[2]"
        ).click()
        for k in CNPJ:
            self.driver.find_element(
                By.XPATH, "//form[@id='daform']/div[9]/div/div/input"
            ).send_keys(k)
        self.driver.find_element(By.XPATH, "//button[contains(.,'Continuar')]").click()
        self.wait.until(
            EC.text_to_be_present_in_element((By.XPATH, "//h1"), "Eleição do Foro")
        )
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[2]/p/span/input"
        ).send_keys("Belo Horizonte")
        dropdown = self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[2]/p/span[2]/select"
        )
        dropdown.find_element(By.XPATH, "//option[. = 'MG']").click()
        self.driver.find_element(By.XPATH, "//button[contains(.,'Continuar')]").click()
        self.wait.until(
            EC.text_to_be_present_in_element((By.XPATH, "//h1"), "Local e Data")
        )
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[2]/div/input"
        ).send_keys("BELO HORIZONTE")
        self.driver.find_element(By.XPATH, "//button[contains(.,'Continuar')]").click()
        try:
            self.driver.find_element(
                By.XPATH, "//h1[contains(.,'Seu documento foi gerado com sucesso!')]"
            )
            print(" Tela final exibida com sucesso!")
        except NoSuchElementException:
            print(" Erro ao enviar o documento para o GED")
            raise