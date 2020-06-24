import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from .web_test import WebTest
from .parameters import CNPJ, CPF


class TestTermodeConfidencialidadeNDA(WebTest):
    @pytest.mark.parametrize(
        "server,user,password,document_name",
        [
            ("https://test.educalegal.com.br/","autotest@educalegal.com.br", "Silex2109", "Autotest_Termo de confidencialidade - NDA"),
            ("https://generation.educalegal.com.br/","maria.secretaria@educalegal.com.br", "silex@568", "Termo de confidencialidade - NDA"),

        ],
    )
    def test_termodeConfidencialidadeNDA(self, server, user, password, document_name):
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
            EC.text_to_be_present_in_element(
                (By.XPATH, "//h1"),
                "Número de reveladores das informações confidenciais",
            )
        )
        self.driver.find_element(By.XPATH, "//button[contains(.,'Continuar')]").click()
        self.wait.until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//h1"),
                "Dados do(a) primeiro(a) revelador das informações confidenciais",
            )
        )
        self.driver.find_element(
            By.CSS_SELECTOR,
            ".form-group:nth-child(2) .btn-light:nth-child(5) > .labelauty-unchecked",
        ).click()
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[9]/div/div/input"
        ).click()
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[9]/div/div/input"
        ).send_keys("Aurora Sistemas Ltda.")
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[10]/div/div/input"
        ).click()
        for k in CNPJ:
            self.driver.find_element(
                By.XPATH, "//form[@id='daform']/div[10]/div/div/input"
            ).send_keys(k)
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[11]/div/div/input"
        ).click()
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[11]/div/div/input"
        ).send_keys("escola.educalegal@gmail.com")
        self.driver.find_element(By.XPATH, "//button[contains(.,'Continuar')]").click()
        self.wait.until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//h1"), "Endereço do(a) Aurora Sistemas Ltda."
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
        ).send_keys("09")
        self.wait.until(
            EC.text_to_be_present_in_element_value(
                (By.XPATH, "//form[@id='daform']/div[3]/div/input"), "Rua Paracatu",
            )
        )
        self.driver.find_element(By.XPATH, "//button[contains(.,'Continuar')]").click()
        self.wait.until(
            EC.text_to_be_present_in_element((By.XPATH, "//h1"), "Reveladores:")
        )
        self.driver.find_element(By.XPATH, "//button[contains(.,'Continuar')]").click()
        self.wait.until(
            EC.text_to_be_present_in_element((By.XPATH, "//h1"), "Prazo do Acordo")
        )
        self.driver.find_element(By.XPATH, "//button[contains(.,'Continuar')]").click()
        self.wait.until(
            EC.text_to_be_present_in_element((By.XPATH, "//h1"), "Eleição do Foro")
        )
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[2]/p/span/input"
        ).send_keys("Belo Horizonte")
        dropdown = self.driver.find_element(By.ID, "c3RhdGU")
        dropdown.find_element(By.XPATH, "//option[. = 'MG']").click()
        self.driver.find_element(By.ID, "c3RhdGU").click()
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
                By.XPATH, "//h5[contains(.,'Seu documento foi inserido no GED!')]"
            )
            print(" Tela final exibida com sucesso!")
        except NoSuchElementException:
            print(" Erro ao enviar o documento para o GED")
