import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from .web_test import WebTest
from .parameters import CPF, CNPJ


class TestContratodeCessaodeEspaco(WebTest):
    @pytest.mark.parametrize(
        "server,user,password,document_name",
        [
            ("https://test.educalegal.com.br/","autotest@educalegal.com.br","Silex2109","Autotest_Contrato de cessão de espaço"),
            ("https://app.educalegal.com.br/","maria.secretaria@educalegal.com.br", "silex@568", "Contrato de cessão de espaço"),

        ],
    )
    def test_contratodeCessaodeEspaco(self, server, user, password, document_name):
        self.driver.get(server)
        self.driver.find_element(By.ID, "id_login").click()
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
            EC.text_to_be_present_in_element((By.XPATH, "//h1"), "Gestor do Contrato da parte Cedente",)
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
        ).send_keys("3132230227")
        self.driver.find_element(By.XPATH, "//button[contains(.,'Continuar')]").click()
        self.wait.until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//h1"), "Número de Cessionárias",
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
                (By.XPATH, "//h1"), "Dados do(a) primeiro(a) Cessionária",
            )
        )
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[2]/div/fieldset/label/span[2]"
        ).click()
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[3]/div/div/input"
        ).send_keys("JOSUÉ SIGNATARIO")
        for k in CPF:
            self.driver.find_element(
                By.XPATH, "//form[@id='daform']/div[4]/div/div/input"
            ).send_keys(k)
        self.driver.find_element(By.ID, "X2ZpZWxkXzM").send_keys("32432423432")
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[7]/div/div/fieldset/label"
        ).click()
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[8]/div/div/input"
        ).send_keys("empresario")
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[11]/div/div/input"
        ).send_keys("josue.signatario@gmail.com")
        self.driver.find_element(By.XPATH, "//button[contains(.,'Continuar')]").click()
        self.wait.until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//h1"), "Endereço do(a) JOSUÉ SIGNATARIO",
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
                (By.XPATH, "//h1"), "Dados do(a) segundo(a) Cessionária",
            )
        )
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[2]/div/fieldset/label[2]/span[2]"
        ).click()
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[9]/div/div/input"
        ).send_keys("FRANCISCO")
        for k in CNPJ:
            self.driver.find_element(
                By.XPATH, "//form[@id='daform']/div[10]/div/div/input"
            ).send_keys(k)
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[11]/div/div/input"
        ).send_keys("fiador.educalegal@gmail.com")
        self.driver.find_element(By.XPATH, "//button[contains(.,'Continuar')]").click()
        self.wait.until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//h1"), "Endereço do(a) FRANCISCO",
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
            EC.text_to_be_present_in_element((By.XPATH, "//h1"), "Cessionárias:")
        )
        self.driver.find_element(By.XPATH, "//button[contains(.,'Continuar')]").click()
        self.wait.until(
            EC.text_to_be_present_in_element((By.XPATH, "//h1"), "Gestor do Contrato da parte Cessionária",)
        )
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[2]/div/fieldset/label"
        ).click()
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[3]/div/div/input"
        ).send_keys("PAULO")
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[4]/div/div/input"
        ).send_keys("valeriano@gmail.com")
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[5]/div/div/input"
        ).send_keys("991925443")
        self.driver.find_element(By.XPATH, "//button[contains(.,'Continuar')]").click()
        self.wait.until(EC.text_to_be_present_in_element((By.XPATH, "//h1"), "Objeto"))
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[2]/p/span/input"
        ).send_keys("biblioteca")
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[3]/div/fieldset/label"
        ).click()
        self.driver.find_element(By.XPATH, "//button[contains(.,'Continuar')]").click()
        self.wait.until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//h1"), "Preço e forma de pagamento",
            )
        )
        dropdown = self.driver.find_element(By.ID, "cGF5bWVudF90eXBl")
        dropdown.find_element(By.XPATH, "//option[. = 'anual']").click()
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[2]/p/span[2]/span[2]/input"
        ).send_keys("10000")
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[3]/div/div/fieldset/label[2]/span[2]"
        ).click()
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[4]/div/div/input"
        ).click()
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[4]/div/div/input"
        ).send_keys("2")
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[5]/div/fieldset/label"
        ).click()
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[6]/div/div/input"
        ).send_keys("BANCO DO BRASIL")
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[7]/div/div/input"
        ).send_keys("4234324")
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[8]/div/div/input"
        ).send_keys("4234324324")
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[9]/div/div/fieldset/label"
        ).click()
        for k in CPF:
            self.driver.find_element(
                By.XPATH, "//form[@id='daform']/div[11]/div/div/input"
            ).send_keys(k)
        self.driver.find_element(By.XPATH, "//button[contains(.,'Continuar')]").click()
        self.wait.until(EC.text_to_be_present_in_element((By.XPATH, "//h1"), "Prazo"))
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[2]/p/span/input"
        ).send_keys("2020-04-09")
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[2]/p/span[2]/input"
        ).send_keys("2020-04-30")
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
