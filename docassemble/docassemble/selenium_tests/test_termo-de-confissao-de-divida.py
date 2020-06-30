import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from .web_test import WebTest
from .parameters import CNPJ, CPF


class TestTermodeconfissaodedivida(WebTest):
    @pytest.mark.parametrize(
        "server,user,password,document_name",
        [
            ("https://test.educalegal.com.br/","autotest@educalegal.com.br", "Silex2109", "Autotest_Termo de confissão de dívida"),
            ("https://app.educalegal.com.br/","maria.secretaria@educalegal.com.br", "silex@568", "Termo de confissão de dívida"),

        ],
    )
    def test_termodeconfissaodedivida(self, server, user, password, document_name):
        self.driver.get(server)
        self.driver.find_element(By.ID, "id_login").send_keys(user)
        self.driver.find_element(By.ID, "id_password").send_keys(password)
        self.driver.find_element(By.CSS_SELECTOR, ".btn").click()
        self.driver.find_element(By.ID, "id_name").send_keys(document_name)
        self.driver.find_element(By.CSS_SELECTOR, ".btn-primary").click()
        self.vars["window_handles"] = self.driver.window_handles
        self.driver.find_element(By.CSS_SELECTOR, ".btn-success").click()
        self.vars["win3478"] = self.wait_for_window(2000)
        self.driver.switch_to.window(self.vars["win3478"])
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
                (By.XPATH, "//h1"), "Gestor do Contrato da Escola"
            )
        )
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[2]/div/fieldset/label"
        ).click()
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[3]/div/div/input"
        ).send_keys("Miguel")
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[4]/div/div/input"
        ).send_keys("miguel@gmail.com")
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[5]/div/div/input"
        ).send_keys("423423423423")
        self.driver.find_element(By.XPATH, "//button[contains(.,'Continuar')]").click()
        self.wait.until(
            EC.text_to_be_present_in_element((By.XPATH, "//h1"), "Número de devedores")
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
                (By.XPATH, "//h1"), "Dados do(a) primeiro(a) Devedor"
            )
        )
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[2]/div/fieldset/label"
        ).click()
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[3]/div/div/input"
        ).send_keys("JOSUÉ SIGNATÁRIO")
        for k in CPF:
            self.driver.find_element(
                By.XPATH, "//form[@id='daform']/div[4]/div/div/input"
            ).send_keys(k)
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[5]/div/div/input"
        ).send_keys("234234234")
        self.driver.find_element(By.XPATH, "//label[contains(.,'solteiro(a)')]").click()
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[8]/div/div/input"
        ).send_keys("Empresário")
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[11]/div/div/input"
        ).send_keys("josue.signatario@gmail.com")
        self.driver.find_element(By.XPATH, "//button[contains(.,'Continuar')]").click()
        self.wait.until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//h1"), "Endereço do(a) JOSUÉ SIGNATÁRIO",
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
                (By.XPATH, "//h1"), "Dados do(a) segundo(a) Devedor"
            )
        )
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[2]/div/fieldset/label[2]"
        ).click()
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[9]/div/div/input"
        ).send_keys("JOSUÉ SIGNATÁRIO LTDA")
        for k in CNPJ:
            self.driver.find_element(
                By.XPATH, "//form[@id='daform']/div[10]/div/div/input"
            ).send_keys(k)
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[11]/div/div/input"
        ).send_keys("josue.signatario@gmail.com")
        self.driver.find_element(By.XPATH, "//button[contains(.,'Continuar')]").click()
        self.wait.until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//h1"), "Endereço do(a) JOSUÉ SIGNATÁRIO LTDA"
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
            EC.text_to_be_present_in_element((By.XPATH, "//h1"), "Devedores:")
        )
        self.driver.find_element(By.XPATH, "//button[contains(.,'Continuar')]").click()
        self.wait.until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//h1"), "Gestor do Contrato da parte Devedora"
            )
        )
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[2]/div/fieldset/label"
        ).click()
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[3]/div/div/input"
        ).send_keys("Paulo")
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[4]/div/div/input"
        ).send_keys("valeriano@gmail.com")
        self.driver.find_element(By.ID, "X2ZpZWxkXzM").send_keys("423432443")
        self.driver.find_element(By.XPATH, "//button[contains(.,'Continuar')]").click()
        self.wait.until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//h1"), "Há algum fiador da dívida?"
            )
        )
        self.driver.find_element(By.XPATH, "//button[contains(.,'Sim')]").click()
        self.wait.until(
            EC.text_to_be_present_in_element((By.XPATH, "//h1"), "Fiadores")
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
                (By.XPATH, "//h1"), "Dados do(a) primeiro(a) Fiador"
            )
        )
        self.driver.find_element(
            By.XPATH, "//label[contains(.,'Pessoa Física')]"
        ).click()
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[3]/div/div/input"
        ).send_keys("Francisco")
        for k in CPF:
            self.driver.find_element(
                By.XPATH, "//form[@id='daform']/div[4]/div/div/input"
            ).send_keys(k)
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[5]/div/div/input"
        ).send_keys("4323423423")
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[7]/div/div/fieldset/label"
        ).click()
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[8]/div/div/input"
        ).send_keys("empresário")
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[11]/div/div/input"
        ).send_keys("fiador.educalegal@gmail.com")
        self.driver.find_element(By.XPATH, "//button[contains(.,'Continuar')]").click()
        self.wait.until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//h1"), "Endereço do(a) Francisco"
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
                (By.XPATH, "//h1"), "Dados do(a) segundo(a) Fiador"
            )
        )
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[2]/div/fieldset/label[2]"
        ).click()
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[9]/div/div/input"
        ).send_keys("FRANCISCO LTDA")
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
                (By.XPATH, "//h1"), "Endereço do(a) FRANCISCO LTDA"
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
            EC.text_to_be_present_in_element((By.XPATH, "//h1"), "Fiadores:")
        )
        self.driver.find_element(By.XPATH, "//button[contains(.,'Continuar')]").click()
        self.wait.until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//h1"), "Gestor do Contrato da parte Fiadora"
            )
        )
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[2]/div/fieldset/label"
        ).click()
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[3]/div/div/input"
        ).send_keys("Luís")
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[4]/div/div/input"
        ).send_keys("luis@gmail.com")
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[5]/div/div/input"
        ).send_keys("423423423")
        self.driver.find_element(By.XPATH, "//button[contains(.,'Continuar')]").click()
        self.wait.until(
            EC.text_to_be_present_in_element((By.XPATH, "//h1"), "Dívida Confessada")
        )
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[2]/p/span/span[2]/input"
        ).send_keys("1000")
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[2]/p/span[3]/input"
        ).send_keys("André")
        self.driver.find_element(By.XPATH, "//button[contains(.,'Continuar')]").click()
        self.wait.until(
            EC.text_to_be_present_in_element((By.XPATH, "//h1"), "Forma de pagamento")
        )
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[2]/div/fieldset/label[2]"
        ).click()
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[3]/div/div/input"
        ).send_keys("2")
        self.driver.find_element(
            By.XPATH, "//label[contains(.,'conta corrente')]"
        ).click()
        self.wait.until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//form[@id='daform']/div[6]/div/label"), "Banco:"
            )
        )
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[6]/div/div/input"
        ).send_keys("Banco Brasil")
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[7]/div/div/input"
        ).send_keys("423423")
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[8]/div/div/input"
        ).send_keys("4323423")
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[9]/div/div/fieldset/label"
        ).click()
        for k in CPF:
            self.driver.find_element(
                By.XPATH, "//form[@id='daform']/div[11]/div/div/input"
            ).send_keys(k)
        self.driver.find_element(By.XPATH, "//button[contains(.,'Continuar')]").click()
        self.wait.until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//h1"), "Anexo"
            )
        )
        self.driver.find_element(By.XPATH, "//label[contains(.,'Não')]").click()
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
