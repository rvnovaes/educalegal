import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from .web_test import WebTest
from .parameters import CPF, RUN_TESTS_AUTOTEST, RUN_TESTS_PRODUCTION


class TestAcordoIndividualReduodeJornadaeReduoSalarial(WebTest):
    # indica em qual ambiente o teste deve ser executado
    environment = list()
    if RUN_TESTS_AUTOTEST:
        environment.append(("https://apptest.educalegal.com.br/", "autotest@educalegal.com.br", "Silex2109",
                            "Autotest_Acordo Individual de Trabalho - Redução de Jornada/Redução Salarial MP 936-2020"),)
    if RUN_TESTS_PRODUCTION:
        environment.append(("https://app.educalegal.com.br/", "maria.secretaria@educalegal.com.br", "silex@568",
                            "Acordo Individual de Trabalho - Redução de Jornada/Redução Salarial MP 936-2020"),)

    @pytest.mark.parametrize("server,user,password,document_name", environment,)
    def test_acordoIndividualReduodeJornadaeReduoSalarial(self, server, user, password, document_name):
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
            EC.text_to_be_present_in_element((By.XPATH, "//h1"), "Dados do(a) Empregado"))
        self.driver.find_element(By.XPATH, "//form[@id=\'daform\']/div[2]/div/input").send_keys("Josué Signatario")
        for k in CPF:
            self.driver.find_element(
                By.XPATH, "//form[@id=\'daform\']/div[3]/div/input"
            ).send_keys(k)
        self.driver.find_element(By.XPATH, "//form[@id=\'daform\']/div[4]/div/input").send_keys("MG102030")
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[6]/div/fieldset/label/span[2]"
        ).click()
        self.driver.find_element(By.XPATH, "//form[@id=\'daform\']/div[7]/div/input").send_keys("36478")
        self.driver.find_element(By.XPATH, "//form[@id=\'daform\']/div[8]/div/input").send_keys("001-3")
        self.driver.find_element(By.XPATH, "//form[@id=\'daform\']/div[9]/div/input").send_keys(
            "josue.signatario@gmail.com")
        self.driver.find_element(By.XPATH, "//button[contains(.,\'Continuar\')]").click()
        self.wait.until(
            EC.text_to_be_present_in_element((By.XPATH, "//h1"), "Endereço do(a) Josué Signatario"))
        self.driver.find_element(By.XPATH, "//form[@id=\'daform\']/div[2]/div/input").send_keys("30180-090")
        self.driver.find_element(By.XPATH, "//form[@id=\'daform\']/div[4]/div/input").send_keys("683")
        self.driver.find_element(By.XPATH, "//form[@id=\'daform\']/div[5]/div/input").send_keys("apartamento 09")
        self.wait.until(
            EC.text_to_be_present_in_element_value(
                (By.XPATH, "//form[@id='daform']/div[3]/div/input"), "Rua Paracatu",
            )
        )
        self.driver.find_element(By.XPATH, "//button[contains(.,\'Continuar\')]").click()

        self.wait.until(
            EC.text_to_be_present_in_element((By.XPATH, "//h1"), "Empregado:"))
        self.driver.find_element(By.XPATH, "//button[contains(.,\'Continuar\')]").click()

        self.wait.until(
            EC.text_to_be_present_in_element((By.XPATH, "//h1"), "Dados do acordo"))
        self.driver.find_element(By.XPATH, "//form[@id=\'daform\']/div[2]/ol/li/p/span/input").send_keys("1000")
        self.driver.find_element(By.XPATH, "//form[@id=\'daform\']/div[2]/ol/li[2]/p/span/span[2]/input").send_keys(
            "2000")
        self.driver.find_element(By.XPATH, "//form[@id=\'daform\']/div[2]/ol/li[3]/p/span/span[2]/input").send_keys(
            "454")
        self.driver.find_element(By.XPATH, "//form[@id=\'daform\']/div[2]/ol/li[4]/p/span/input").send_keys("90")
        self.driver.find_element(By.XPATH, "//button[contains(.,\'Continuar\')]").click()

        self.wait.until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//h1"),
                "Cláusula de estabilidade de emprego conforme padrão definido por:",
            )
        )
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[2]/div/fieldset/label/span[4]"
        ).click()
        self.driver.find_element(By.XPATH, "//button[contains(.,'Continuar')]").click()

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