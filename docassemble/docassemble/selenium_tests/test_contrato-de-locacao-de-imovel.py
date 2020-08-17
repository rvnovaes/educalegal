import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from .web_test import WebTest
from .parameters import CPF, RUN_TESTS_AUTOTEST, RUN_TESTS_PRODUCTION


class TestContratodeLocaodeImvel(WebTest):
    # indica em qual ambiente o teste deve ser executado
    environment = list()
    if RUN_TESTS_AUTOTEST:
        environment.append(("https://test.educalegal.com.br/", "autotest@educalegal.com.br", "Silex2109",
                            "Autotest_Contrato de locação de imóvel"),)
    if RUN_TESTS_PRODUCTION:
        environment.append(("https://app.educalegal.com.br/", "maria.secretaria@educalegal.com.br", "silex@568",
                            "Contrato de locação de imóvel"),)

    @pytest.mark.parametrize("server,user,password,document_name", environment,)
    def test_contratodeLocaodeImvel(self, server, user, password, document_name):
        self.driver.get(server)
        self.driver.find_element(By.ID, "id_login").send_keys(user)
        self.driver.find_element(By.ID, "id_password").send_keys(password)
        self.driver.find_element(By.CSS_SELECTOR, ".btn").click()
        self.driver.find_element(By.ID, "id_name").send_keys(document_name)
        self.driver.find_element(By.ID, "id_name").send_keys(Keys.ENTER)
        self.vars["window_handles"] = self.driver.window_handles
        self.driver.find_element(By.CSS_SELECTOR, ".btn-success").click()
        self.vars["win471"] = self.wait_for_window(2000)
        self.driver.switch_to.window(self.vars["win471"])
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
            EC.text_to_be_present_in_element(
                (By.XPATH, "//h1"),
                "Qual o tipo da parte é a escola?",
            )
        )
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[2]/div/fieldset/label/span[2]"
        ).click()
        self.driver.find_element(By.XPATH, "//button[contains(.,'Continuar')]").click()
        self.wait.until(
            EC.text_to_be_present_in_element((By.XPATH, "//h1"), "Gestor do Contrato da parte Locadora")
        )
        self.driver.find_element(By.CSS_SELECTOR, ".btn-light:nth-child(5)").click()
        self.driver.find_element(By.XPATH, "//button[contains(.,'Continuar')]").click()
        self.wait.until(
            EC.text_to_be_present_in_element((By.XPATH, "//h1"), "Número de Locatários")
        )
        self.driver.find_element(By.XPATH, "//button[contains(.,'Continuar')]").click()
        self.wait.until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//h1"), "Dados do(a) primeiro(a) locatário(a)"
            )
        )
        self.driver.find_element(
            By.CSS_SELECTOR,
            ".form-group:nth-child(2) .btn-light:nth-child(3) > .labelauty-unchecked",
        ).click()
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[3]/div/div/input"
        ).click()
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[3]/div/div/input"
        ).send_keys("PAULO VITOR VALERIANO DOS SANTOS")
        for k in CPF:
            self.driver.find_element(
                By.XPATH, "//form[@id='daform']/div[4]/div/div/input"
            ).send_keys(k)
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[5]/div/div/input"
        ).click()
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[5]/div/div/input"
        ).send_keys("32432423432")
        self.driver.find_element(By.CSS_SELECTOR, ".btn-light:nth-child(3)").click()
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[8]/div/div/input"
        ).click()
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[8]/div/div/input"
        ).send_keys("ADVOGADO júnior")
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[11]/div/div/input"
        ).send_keys("escola.educalegal@gmail.com")
        self.driver.find_element(By.XPATH, "//button[contains(.,'Continuar')]").click()
        self.wait.until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//h1"), "Endereço do(a) PAULO VITOR VALERIANO DOS SANTOS"
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
            EC.text_to_be_present_in_element((By.XPATH, "//h1"), "Locatários:")
        )
        self.driver.find_element(By.XPATH, "//button[contains(.,'Continuar')]").click()
        self.wait.until(
            EC.text_to_be_present_in_element((By.XPATH, "//h1"), "Gestor do Contrato da parte Locatária")
        )
        self.driver.find_element(
            By.CSS_SELECTOR, ".btn-light:nth-child(3)"
        ).click()  # SIM
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[3]/div/div/input"
        ).send_keys("Roberto Vasconcelos Novaes")
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[4]/div/div/input"
        ).send_keys("roberto.novaes@educalegal.com.br")
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[5]/div/div/input"
        ).click()
        self.driver.find_element(By.XPATH, "//input[@id='X2ZpZWxkXzM']").send_keys(
            "(31) 98447-9085"
        )
        self.driver.find_element(By.XPATH, "//button[contains(.,'Continuar')]").click()
        self.wait.until(
            EC.text_to_be_present_in_element((By.XPATH, "//h1"), "Número de Fiadores")
        )
        self.driver.find_element(By.XPATH, "//button[contains(.,'Continuar')]").click()
        self.wait.until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//h1"), "Dados do(a) primeiro(a) fiador(a)"
            )
        )
        self.driver.find_element(
            By.XPATH, "//span[contains(.,'Pessoa Física')]"
        ).click()
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[3]/div/div/input"
        ).send_keys("Helena Gomes")
        for k in CPF:
            self.driver.find_element(
                By.XPATH, "//form[@id='daform']/div[4]/div/div/input"
            ).send_keys(k)
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[5]/div/div/input"
        ).send_keys("MG 1.987.987")
        self.driver.find_element(By.XPATH, "//span[contains(.,'solteiro(a)')]").click()
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[8]/div/div/input"
        ).send_keys("Empresária")
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[11]/div/div/input"
        ).send_keys("helena.gomes@educalegal.com.br")
        self.driver.find_element(By.XPATH, "//span[contains(.,'Continuar')]").click()
        self.wait.until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//h1"), "Endereço do(a) Helena Gomes"
            )
        )
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[2]/div/input"
        ).send_keys("30220-220")
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[4]/div/input"
        ).send_keys("123")
        self.wait.until(
            EC.text_to_be_present_in_element_value(
                (By.XPATH, "//form[@id='daform']/div[3]/div/input"),
                "Rua Manoel Gomes Pereira",
            )
        )
        self.driver.find_element(By.XPATH, "//span[contains(.,'Continuar')]").click()
        self.wait.until(
            EC.text_to_be_present_in_element((By.XPATH, "//h1"), "Fiadores:")
        )
        self.driver.find_element(By.XPATH, "//span[contains(.,'Continuar')]").click()
        self.wait.until(
            EC.text_to_be_present_in_element((By.XPATH, "//h1"), "Gestor do Contrato")
        )
        self.driver.find_element(
            By.CSS_SELECTOR, ".btn-light:nth-child(5)"
        ).click()  # NÃO
        self.driver.find_element(By.XPATH, "//span[contains(.,'Continuar')]").click()
        self.wait.until(
            EC.text_to_be_present_in_element((By.XPATH, "//h1"), "Dados do Imóvel")
        )
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[2]/div/input"
        ).send_keys("17800")
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[3]/div/input"
        ).send_keys("123124123123")
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[4]/div/textarea"
        ).send_keys("Cartório do 4º Ofício de Belo Horizonte")
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[5]/div/input"
        ).send_keys("30220-210")
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[7]/div/input"
        ).click()
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[7]/div/input"
        ).send_keys("123")
        self.wait.until(
            EC.text_to_be_present_in_element_value(
                (By.XPATH, "//form[@id='daform']/div[6]/div/input"),
                "Rua São Sebastião",
            )
        )
        self.driver.find_element(By.XPATH, "//span[contains(.,'Continuar')]").click()
        self.wait.until(
            EC.text_to_be_present_in_element((By.XPATH, "//h1"), "Prazo do Contrato")
        )
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[2]/div/input"
        ).send_keys("48")
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[3]/div/input"
        ).click()
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[3]/div/input"
        ).send_keys("2020-03-28")
        self.driver.find_element(By.XPATH, "//button[contains(.,'Continuar')]").click()
        self.wait.until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//h1"), "Valor e Condições de Pagamento"
            )
        )
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[2]/div/div/input"
        ).send_keys("340000")
        self.driver.find_element(By.XPATH, "//label[contains(.,'Não')]").click()
        self.driver.find_element(
            By.XPATH, "//span[contains(.,'boleto bancário')]"
        ).click()
        self.driver.find_element(By.XPATH, "//span[contains(.,'IPC-A')]").click()
        self.driver.find_element(By.XPATH, "//span[contains(.,'Continuar')]").click()
        self.wait.until(
            EC.text_to_be_present_in_element((By.XPATH, "//h1"), "Eleição do Foro")
        )
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[2]/p/span/input"
        ).send_keys("Belo Horizonte")
        dropdown = self.driver.find_element(By.ID, "c3RhdGU")
        dropdown.find_element(By.XPATH, "//option[. = 'MG']").click()
        self.driver.find_element(By.XPATH, "//span[contains(.,'Continuar')]").click()
        self.wait.until(
            EC.text_to_be_present_in_element((By.XPATH, "//h1"), "Local e Data")
        )
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[2]/div/input"
        ).send_keys("Belo Horizonte")
        self.driver.find_element(By.XPATH, "//span[contains(.,'Continuar')]").click()
        try:
            self.driver.find_element(
                By.XPATH, "//h1[contains(.,'Seu documento foi gerado com sucesso!')]"
            )
            print(" Tela final exibida com sucesso!")
        except NoSuchElementException:
            print(" Erro ao enviar o documento para o GED")
            raise