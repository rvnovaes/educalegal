import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from .web_test import WebTest
from .parameters import CPF, RUN_TESTS_AUTOTEST, RUN_TESTS_PRODUCTION


class TestAditivodereparcelamentodocontratodoaluno(WebTest):
    # indica em qual ambiente o teste deve ser executado
    environment = list()
    if RUN_TESTS_AUTOTEST:
        environment.append(("https://test.educalegal.com.br/", "autotest@educalegal.com.br", "Silex2109",
                            "Autotest_Aditivo de Reparcelamento do Contrato do Aluno"),)
    if RUN_TESTS_PRODUCTION:
        environment.append(("https://app.educalegal.com.br/", "maria.secretaria@educalegal.com.br", "silex@568",
                            "Aditivo de Reparcelamento do Contrato do Aluno"),)

    @pytest.mark.parametrize("server,user,password,document_name", environment,)
    def test_aditivodereparcelamentodocontratodoaluno(self, server, user, password, document_name):
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
        self.vars["win9982"] = self.wait_for_window(2000)
        self.driver.switch_to.window(self.vars["win9982"])
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
            EC.text_to_be_present_in_element((By.XPATH, "//h1"), "Número de Contratantes"))
        self.driver.find_element(By.XPATH, "//form[@id=\'daform\']/div[2]/div/input").clear()
        self.driver.find_element(By.XPATH, "//form[@id=\'daform\']/div[2]/div/input").send_keys("2")
        self.driver.find_element(By.XPATH, "//button[contains(.,\'Continuar\')]").click()
        self.wait.until(EC.text_to_be_present_in_element((By.XPATH, "//h1"),
                                                                                                  "Dados do(a) primeiro(a) Contratante"))
        self.driver.find_element(By.XPATH, "//form[@id=\'daform\']/div[2]/div/input").send_keys("JOSUÉ SIGNATÁRIO")
        for k in CPF:
            self.driver.find_element(
                By.XPATH, "//form[@id=\'daform\']/div[3]/div/input"
            ).send_keys(k)
        self.driver.find_element(By.XPATH, "//form[@id=\'daform\']/div[4]/div/input").send_keys("15.434.545")
        self.driver.find_element(By.XPATH, "//form[@id=\'daform\']/div[5]/div/input").send_keys("SSP/MG")
        self.driver.find_element(By.XPATH, "//label[contains(.,\'solteiro(a)\')]").click()
        self.driver.find_element(By.XPATH, "//form[@id=\'daform\']/div[8]/div/input").send_keys("EMPRESÁRIO")
        self.driver.find_element(By.XPATH, "//form[@id=\'daform\']/div[9]/div/input").send_keys(
            "josue.signatario@gmail.com")
        self.driver.find_element(By.XPATH, "//form[@id=\'daform\']/div[10]/div/input").send_keys("(31)90000-0000")
        self.driver.find_element(By.XPATH, "//form[@id=\'daform\']/div[11]/div/input").send_keys("(31)3454-0000")
        self.driver.find_element(By.XPATH, "//form[@id=\'daform\']/div[12]/div/input").send_keys("(31)90000-0000")
        self.driver.find_element(By.XPATH, "//button[contains(.,\'Continuar\')]").click()
        self.wait.until(
            EC.text_to_be_present_in_element((By.XPATH, "//h1"), "Endereço de JOSUÉ SIGNATÁRIO"))
        self.driver.find_element(By.XPATH, "//form[@id=\'daform\']/div[2]/div/input").send_keys("30180-090")
        self.driver.find_element(By.XPATH, "//form[@id=\'daform\']/div[4]/div/input").send_keys("000")
        self.driver.find_element(By.XPATH, "//form[@id=\'daform\']/div[5]/div/input").send_keys("apto 00")
        self.wait.until(
            EC.text_to_be_present_in_element_value(
                (By.XPATH, "//form[@id='daform']/div[3]/div/input"), "Rua Paracatu",
            )
        )
        self.driver.find_element(By.XPATH, "//button[contains(.,\'Continuar\')]").click()
        self.wait.until(
            EC.text_to_be_present_in_element((By.XPATH, "//h1"), "Dados do(a) segundo(a) Contratante"))
        self.driver.find_element(By.XPATH, "//form[@id=\'daform\']/div[2]/div/input").send_keys("FRANCISCO CHICO")
        for k in CPF:
            self.driver.find_element(
                By.XPATH, "//form[@id=\'daform\']/div[3]/div/input"
            ).send_keys(k)
        self.driver.find_element(By.XPATH, "//form[@id=\'daform\']/div[4]/div/input").send_keys("43.6565.4343")
        self.driver.find_element(By.XPATH, "//form[@id=\'daform\']/div[5]/div/input").send_keys("SSP/MG")
        self.driver.find_element(By.XPATH, "//form[@id=\'daform\']/div[7]/div/fieldset/label/span[2]").click()
        self.driver.find_element(By.XPATH, "//form[@id=\'daform\']/div[8]/div/input").send_keys("PROFESSOR")
        self.driver.find_element(By.XPATH, "//form[@id=\'daform\']/div[9]/div/input").send_keys(
            "fiador.educalegal@gmail.com")
        self.driver.find_element(By.XPATH, "//form[@id=\'daform\']/div[10]/div/input").send_keys("(31)90000-0000")
        self.driver.find_element(By.XPATH, "//form[@id=\'daform\']/div[11]/div/input").send_keys("(31)3454-0000")
        self.driver.find_element(By.XPATH, "//form[@id=\'daform\']/div[12]/div/input").send_keys("(31)90000-0000")
        self.driver.find_element(By.XPATH, "//button[contains(.,\'Continuar\')]").click()
        self.wait.until(
            EC.text_to_be_present_in_element((By.XPATH, "//h1"), "Endereço de FRANCISCO CHICO"))
        self.driver.find_element(By.XPATH, "//form[@id=\'daform\']/div[2]/div/input").send_keys("30180-090")
        self.driver.find_element(By.XPATH, "//form[@id=\'daform\']/div[4]/div/input").send_keys("000")
        self.driver.find_element(By.XPATH, "//form[@id=\'daform\']/div[5]/div/input").send_keys("apto 00")
        self.wait.until(
            EC.text_to_be_present_in_element_value(
                (By.XPATH, "//form[@id='daform']/div[3]/div/input"), "Rua Paracatu",
            )
        )
        self.driver.find_element(By.XPATH, "//button[contains(.,\'Continuar\')]").click()
        self.wait.until(
            EC.text_to_be_present_in_element((By.XPATH, "//h1"), "Contratantes:"))
        self.driver.find_element(By.XPATH, "//button[contains(.,\'Continuar\')]").click()
        self.driver.find_element(By.XPATH, "//form[@id=\'daform\']/div[2]/div/input").send_keys("André")
        self.driver.find_element(By.XPATH, "//form[@id=\'daform\']/div[3]/div/input").send_keys("Inglês")
        self.driver.find_element(By.XPATH, "//button[contains(.,\'Continuar\')]").click()
        self.wait.until(
            EC.text_to_be_present_in_element((By.XPATH, "//h1"), "Preço e Forma de Pagamento"))
        self.driver.find_element(By.XPATH, "//form[@id=\'daform\']/div[2]/div/fieldset/label[2]/span[2]").click()
        self.driver.find_element(By.XPATH, "//form[@id=\'daform\']/div[5]/div/div/fieldset/label").click()
        self.driver.find_element(By.XPATH, "//form[@id=\'daform\']/div[6]/div/div/div/input").send_keys("1000")
        self.driver.find_element(By.XPATH, "//form[@id=\'daform\']/div[7]/div/div/input").send_keys("2020-07-01")
        self.driver.find_element(By.XPATH, "//form[@id=\'daform\']/div[8]/div/div/input").send_keys("3")
        self.driver.find_element(By.XPATH, "//form[@id=\'daform\']/div[9]/div/div/div/input").send_keys("500")
        self.driver.find_element(By.XPATH, "//form[@id=\'daform\']/div[10]/div/div/input").send_keys("2020-07-15")
        self.driver.find_element(By.XPATH, "//button[contains(.,\'Continuar\')]").click()
        self.wait.until(
            EC.text_to_be_present_in_element((By.XPATH, "//form[@id=\'daform\']/div/h1"),
                                                              "Local e Data"))
        self.driver.find_element(By.XPATH, "//form[@id=\'daform\']/div[2]/div/input").send_keys("Belo Horizonte")
        self.driver.find_element(By.XPATH, "//button[contains(.,\'Continuar\')]").click()




        try:
            self.driver.find_element(
                By.XPATH, "//h1[contains(.,'Seu documento foi gerado com sucesso!')]"
            )
            print(" Tela final exibida com sucesso!")
        except NoSuchElementException:
            print(" Erro ao enviar o documento para o GED")
            raise