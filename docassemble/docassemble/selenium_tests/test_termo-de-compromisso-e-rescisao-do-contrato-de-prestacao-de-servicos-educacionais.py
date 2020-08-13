import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from .web_test import WebTest
from .parameters import CPF, RUN_TESTS_AUTOTEST, RUN_TESTS_PRODUCTION


class TestTermodecompromissoerescisaodocontratodeprestacaodeservicoseducacionais(WebTest):
    # indica em qual ambiente o teste deve ser executado
    environment = list()
    if RUN_TESTS_AUTOTEST:
        environment.append(("https://test.educalegal.com.br/", "autotest@educalegal.com.br", "Silex2109",
                            "Autotest_Termo de Compromisso e Rescisão do Contrato de Prestação de Serviços Educacionais"),)
    if RUN_TESTS_PRODUCTION:
        environment.append(("https://app.educalegal.com.br/", "maria.secretaria@educalegal.com.br", "silex@568",
                            "Termo de Compromisso e Rescisão do Contrato de Prestação de Serviços Educacionais"),)

    @pytest.mark.parametrize("server,user,password,document_name", environment,)
    def test_termodecompromissoerescisaodocontratodeprestacaodeservicoseducacionais(self, server, user, password, document_name):
        self.driver.get(server)
        self.driver.find_element(By.ID, "id_login").click()
        self.driver.find_element(By.ID, "id_login").send_keys(user)
        self.driver.find_element(By.ID, "id_password").send_keys(password)
        self.driver.find_element(By.CSS_SELECTOR, ".btn").click()
        self.driver.find_element(By.ID, "id_name").click()
        self.driver.find_element(By.ID, "id_name").send_keys(document_name)
        self.driver.find_element(By.ID, "id_name").send_keys(Keys.ENTER)
        self.vars["window_handles"] = self.driver.window_handles
        self.driver.find_element(By.CSS_SELECTOR, ".btn-success").click()
        self.vars["win6352"] = self.wait_for_window(2000)
        self.driver.switch_to.window(self.vars["win6352"])
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
            EC.text_to_be_present_in_element((By.XPATH, "//h1"), "Dados do(a) Rescindente"))
        self.driver.find_element(By.XPATH, "//form[@id=\'daform\']/div[2]/div/input").send_keys("JOSUE SIGNATARIO")
        for k in CPF:
            self.driver.find_element(
                By.XPATH, "//form[@id=\'daform\']/div[3]/div/input"
            ).send_keys(k)
        self.driver.find_element(By.XPATH, "//form[@id=\'daform\']/div[4]/div/input").send_keys("4234324234")
        self.driver.find_element(By.XPATH, "//form[@id=\'daform\']/div[5]/div/input").send_keys(
            "josue.signatario@gmail.com")
        self.driver.find_element(By.XPATH, "//button[contains(.,\'Continuar\')]").click()
        self.wait.until(
            EC.text_to_be_present_in_element((By.XPATH, "//h1"), "Rescindente(s):"))
        self.driver.find_element(By.XPATH, "//button[contains(.,\'Continuar\')]").click()
        self.wait.until(
            EC.text_to_be_present_in_element((By.XPATH, "//h1"), "Número de Alunos"))
        self.driver.find_element(By.XPATH, "//form[@id=\'daform\']/div[2]/div/input").clear()
        self.driver.find_element(By.XPATH, "//form[@id=\'daform\']/div[2]/div/input").send_keys("2")
        self.driver.find_element(By.XPATH, "//button[contains(.,\'Continuar\')]").click()
        self.wait.until(
            EC.text_to_be_present_in_element((By.XPATH, "//h1"), "Dados do(a) primeiro(a) Aluno(a)"))
        self.driver.find_element(By.XPATH, "//form[@id=\'daform\']/div[2]/div/input").send_keys("BRUNO")
        self.driver.find_element(By.XPATH, "//form[@id=\'daform\']/div[3]/div/input").send_keys("432423432")
        self.driver.find_element(By.XPATH, "//form[@id=\'daform\']/div[4]/div/input").send_keys("2020-03-18")
        self.driver.find_element(By.XPATH, "//form[@id=\'daform\']/div[5]/div/input").send_keys("2020")
        dropdown = self.driver.find_element(By.XPATH, "//form[@id=\'daform\']/div[6]/div/select")
        dropdown.find_element(By.XPATH, "//option[. = '1º período do ensino infantil']").click()
        self.driver.find_element(By.XPATH, "//button[contains(.,\'Continuar\')]").click()
        self.wait.until(
            EC.text_to_be_present_in_element((By.XPATH, "//h1"), "Dados do(a) segundo(a) Aluno(a)"))
        self.driver.find_element(By.XPATH, "//form[@id=\'daform\']/div[2]/div/input").send_keys("SOFIA")
        self.driver.find_element(By.XPATH, "//form[@id=\'daform\']/div[3]/div/input").send_keys("432432423")
        self.driver.find_element(By.XPATH, "//form[@id=\'daform\']/div[4]/div/input").send_keys("2020-07-09")
        self.driver.find_element(By.XPATH, "//form[@id=\'daform\']/div[5]/div/input").send_keys("2020")
        dropdown = self.driver.find_element(By.XPATH, "//form[@id=\'daform\']/div[6]/div/select")
        dropdown.find_element(By.XPATH, "//option[. = '7º ano do ensino fundamental']").click()
        self.driver.find_element(By.XPATH, "//button[contains(.,\'Continuar\')]").click()
        self.wait.until(
            EC.text_to_be_present_in_element((By.XPATH, "//h1"), "Diretoria Regional de Ensino"))
        self.driver.find_element(By.XPATH, "//form[@id=\'daform\']/div[2]/p/span/input").send_keys("LAVRAS")
        self.driver.find_element(By.XPATH, "//button[contains(.,\'Continuar\')]").click()
        self.wait.until(EC.text_to_be_present_in_element((By.XPATH, "//h1"),
                                                                                                  "Endereço da Diretoria de Ensino da Regional de(o) LAVRAS"))
        self.driver.find_element(By.XPATH, "//form[@id=\'daform\']/div[2]/div/input").send_keys("30180-090")
        self.driver.find_element(By.XPATH, "//form[@id=\'daform\']/div[4]/div/input").send_keys("000")
        self.driver.find_element(By.XPATH, "//form[@id=\'daform\']/div[5]/div/input").send_keys("APTO 00")
        self.wait.until(
            EC.text_to_be_present_in_element_value(
                (By.XPATH, "//form[@id='daform']/div[3]/div/input"), "Rua Paracatu",
            )
        )
        self.driver.find_element(By.XPATH, "//button[contains(.,\'Continuar\')]").click()
        self.wait.until(
            EC.text_to_be_present_in_element((By.XPATH, "//h1"), "Local e Data"))
        self.driver.find_element(By.XPATH, "//form[@id=\'daform\']/div[2]/div/input").send_keys("BELO HORIZONTE")
        self.driver.find_element(By.XPATH, "//button[contains(.,\'Continuar\')]").click()
        try:
            self.driver.find_element(
                By.XPATH, "//h1[contains(.,'Seu documento foi gerado com sucesso!')]"
            )
            print(" Tela final exibida com sucesso!")
        except NoSuchElementException:
            print(" Erro ao enviar o documento para o GED")
            raise