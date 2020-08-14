import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from .web_test import WebTest
from .parameters import CNPJ, CPF, RUN_TESTS_AUTOTEST, RUN_TESTS_PRODUCTION


class TestContratodeConsultoria(WebTest):
    # indica em qual ambiente o teste deve ser executado
    environment = list()
    if RUN_TESTS_AUTOTEST:
        environment.append(("https://test.educalegal.com.br/", "autotest@educalegal.com.br", "Silex2109",
                            "Autotest_Contrato de consultoria"),)
    if RUN_TESTS_PRODUCTION:
        environment.append(("https://app.educalegal.com.br/", "maria.secretaria@educalegal.com.br", "silex@568",
                            "Contrato de consultoria"),)

    @pytest.mark.parametrize("server,user,password,document_name", environment,)
    def test_contratodeConsultoria(self, server, user, password, document_name):
        self.driver.get(server)
        self.driver.find_element(By.ID, "id_login").send_keys(user)
        self.driver.find_element(By.ID, "id_password").send_keys(password)
        self.driver.find_element(By.CSS_SELECTOR, ".btn").click()
        self.driver.find_element(By.ID, "id_name").send_keys(document_name)
        self.driver.find_element(By.CSS_SELECTOR, ".btn-primary").click()
        self.vars["window_handles"] = self.driver.window_handles
        self.driver.find_element(By.CSS_SELECTOR, ".btn-success").click()
        self.vars["win2255"] = self.wait_for_window(2000)
        self.driver.switch_to.window(self.vars["win2255"])
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
            EC.text_to_be_present_in_element((By.XPATH, "//h1"), "Gestor do Contrato da Escola")
        )
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[2]/div/fieldset/label"
        ).click()
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[3]/div/div/input"
        ).send_keys("Miguel Gestor 01")
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[4]/div/div/input"
        ).send_keys("miguel@gmail.com")
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[5]/div/div/input"
        ).send_keys("2156892356")
        self.driver.find_element(By.XPATH, "//button[contains(.,'Continuar')]").click()
        self.wait.until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//h1"), "Número de Contratadas"
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
                (By.XPATH, "//h1"), "Dados do(a) primeiro(a) Contratada"
            )
        )
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[2]/div/input"
        ).send_keys("JOSUE SIGNATARIO")
        for k in CNPJ:
            self.driver.find_element(
                By.XPATH, "//form[@id='daform']/div[3]/div/input"
            ).send_keys(k)
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[4]/div/input"
        ).send_keys("josue.signatario@gmail.com")
        self.driver.find_element(By.XPATH, "//button[contains(.,'Continuar')]").click()
        self.wait.until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//h1"), "Endereço do(a) JOSUE SIGNATARIO"
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
        ).send_keys("APARTAMENTO 09")
        self.wait.until(
            EC.text_to_be_present_in_element_value(
                (By.XPATH, "//form[@id='daform']/div[3]/div/input"), "Rua Paracatu",
            )
        )
        self.driver.find_element(By.XPATH, "//button[contains(.,'Continuar')]").click()
        self.wait.until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//h1"), "Dados do(a) segundo(a) Contratada"
            )
        )
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[2]/div/input"
        ).send_keys("FRANCISCO")
        for k in CNPJ:
            self.driver.find_element(
                By.XPATH, "//form[@id='daform']/div[3]/div/input"
            ).send_keys(k)
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[4]/div/input"
        ).send_keys("fiador.educalegal@gmail.com")
        self.driver.find_element(By.XPATH, "//button[contains(.,'Continuar')]").click()
        self.wait.until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//h1"), "Endereço do(a) FRANCISCO"
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
        ).send_keys("APARTAMENTO 09")
        self.wait.until(
            EC.text_to_be_present_in_element_value(
                (By.XPATH, "//form[@id='daform']/div[3]/div/input"), "Rua Paracatu",
            )
        )
        self.driver.find_element(By.XPATH, "//button[contains(.,'Continuar')]").click()
        self.wait.until(
            EC.text_to_be_present_in_element((By.XPATH, "//h1"), "Contratadas:")
        )
        self.driver.find_element(By.XPATH, "//button[contains(.,'Continuar')]").click()
        self.wait.until(
            EC.text_to_be_present_in_element((By.XPATH, "//h1"), "Gestor do Contrato")
        )
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[2]/div/fieldset/label"
        ).click()
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[3]/div/div/input"
        ).send_keys("PAULO VITOR VALERIANO DOS SANTOS")
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[4]/div/div/input"
        ).send_keys("valeriano@gmail.com")
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[5]/div/div/input"
        ).send_keys("99192542343")
        self.driver.find_element(By.XPATH, "//button[contains(.,'Continuar')]").click()
        self.wait.until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//h1[contains(.,'Objeto')]"), "Objeto"
            )
        )
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[2]/p/span/input"
        ).send_keys("CONSULTORIA JURÍDICA")
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[3]/div/fieldset/label"
        ).click()
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[4]/div/fieldset/label[2]"
        ).click()
        self.driver.find_element(By.XPATH, "//button[contains(.,'Continuar')]").click()
        self.wait.until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//h1"), "Preço e forma de pagamento"
            )
        )
        dropdown = self.driver.find_element(By.ID, "dGlwb1BhcmNlbGE")
        dropdown.find_element(By.XPATH, "//option[. = 'anual']").click()
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[2]/p/span[2]/span[2]/input"
        ).send_keys("13213")
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[3]/div/div/fieldset/label[2]"
        ).click()
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[4]/div/div/input"
        ).send_keys("2")
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[5]/div/fieldset/label/span[2]"
        ).click()
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[6]/div/div/input"
        ).send_keys("BANCO DO BRASIL")
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[7]/div/div/input"
        ).send_keys("423442342")
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[8]/div/div/input"
        ).send_keys("234234234234")
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[9]/div/div/fieldset/label"
        ).click()
        for k in CPF:
            self.driver.find_element(By.ID, "X2ZpZWxkXzEw").send_keys(k)
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[12]/div/fieldset/label"
        ).click()
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[13]/div/div/textarea"
        ).send_keys("CONDIÇÃO 01")
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[14]/div/fieldset/label/span[2]"
        ).click()
        self.driver.find_element(By.XPATH, "//button[contains(.,'Continuar')]").click()
        self.wait.until(EC.text_to_be_present_in_element((By.XPATH, "//h1"), "Prazo"))
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[2]/p/span/input"
        ).send_keys("2020-03-31")
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[2]/p/span[2]/input"
        ).send_keys("2020-04-10")
        self.driver.find_element(By.XPATH, "//button[contains(.,'Continuar')]").click()
        self.wait.until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//h1"),
                "O presente Contrato prevê exclusividade por parte da Contratada no que se refere ao segmento de atuação da Contratante?",
            )
        )
        self.driver.find_element(By.XPATH, "//button[contains(.,'Sim')]").click()
        self.wait.until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//h1"),
                "Existem outras obrigações da Contratada além das previstas no Contrato?",
            )
        )
        self.driver.find_element(By.XPATH, "//button[contains(.,'Sim')]").click()
        self.wait.until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//h1"), "Cite as outras obrigações da Contratada."
            )
        )
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[3]/div/input"
        ).send_keys("OBRIGAÇÃO 01")
        self.driver.find_element(By.XPATH, "//button[contains(.,'Continuar')]").click()
        self.wait.until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//h1"), "Local da prestação dos serviços"
            )
        )
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[2]/div/fieldset/label"
        ).click()
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[4]/div/fieldset/label"
        ).click()
        self.driver.find_element(By.XPATH, "//button[contains(.,'Continuar')]").click()
        self.wait.until(
            EC.text_to_be_present_in_element((By.XPATH, "//h1"), "Eleição do Foro")
        )
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[2]/p/span/input"
        ).send_keys("Belo Horizonte")
        dropdown = self.driver.find_element(By.ID, "c3RhdGU")
        dropdown.find_element(By.XPATH, "//option[. = 'MG']").click()
        self.driver.find_element(By.XPATH, "//button[contains(.,'Continuar')]").click()
        self.wait.until(
            EC.text_to_be_present_in_element((By.XPATH, "//h1"), "Local e Data")
        )
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[2]/div/input"
        ).send_keys("Belo Horizonte")
        self.driver.find_element(By.XPATH, "//button[contains(.,'Continuar')]").click()
        try:
            self.driver.find_element(
                By.XPATH, "//h1[contains(.,'Seu documento foi gerado com sucesso!')]"
            )
            print(" Tela final exibida com sucesso!")
        except NoSuchElementException:
            print(" Erro ao enviar o documento para o GED")
            raise
