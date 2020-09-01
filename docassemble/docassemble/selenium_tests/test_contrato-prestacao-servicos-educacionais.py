import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from .web_test import WebTest
from .parameters import CPF, RUN_TESTS_AUTOTEST, RUN_TESTS_PRODUCTION


class TestContratodoaluno(WebTest):
    # indica em qual ambiente o teste deve ser executado
    environment = list()
    if RUN_TESTS_AUTOTEST:
        environment.append(("https://test.educalegal.com.br/", "autotest@educalegal.com.br", "Silex2109",
                            "Autotest_Contrato de Prestação de Serviços Educacionais"),)
    if RUN_TESTS_PRODUCTION:
        environment.append(("https://app.educalegal.com.br/", "maria.secretaria@educalegal.com.br", "silex@568",
                            "Contrato de Prestação de Serviços Educacionais"),)

    @pytest.mark.parametrize("server,user,password,document_name", environment,)
    def test_contratodoaluno(self, server, user, password, document_name):
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
        try:
            self.driver.find_element(
                By.XPATH, "//h1[contains(.,'Escolha a unidade escolar')]"
            )
            self.wait.until(
                EC.text_to_be_present_in_element(
                    (By.XPATH, "//h1"), "Escolha a unidade escolar"
                )
            )
            self.driver.find_element(
                By.XPATH, "//form[@id='daform']/fieldset/div/div/label"
            ).click()
            self.driver.find_element(
                By.XPATH, "//button[contains(.,'Continuar')]"
            ).click()
        except NoSuchElementException:
            pass
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[2]/div/input"
        ).send_keys("Josué Signatário Filho")
        for k in CPF:
            self.driver.find_element(
                By.XPATH, "//form[@id='daform']/div[3]/div/input"
            ).send_keys(k)
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[4]/div/input"
        ).send_keys("MG 9.088.343")
        self.driver.find_element(By.XPATH, "//span[contains(.,'Continuar')]").click()
        self.wait.until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//h1"), "Endereço do(a) Aluno(a)"
            )
        )
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[2]/div/input"
        ).send_keys("30220-220")
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[4]/div/input"
        ).click()
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[4]/div/input"
        ).send_keys("123")
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[5]/div/input"
        ).send_keys("Apto. 201")
        self.wait.until(
            EC.text_to_be_present_in_element_value(
                (By.XPATH, "//form[@id='daform']/div[3]/div/input"),
                "Rua Manoel Gomes Pereira",
            )
        )
        self.driver.find_element(By.XPATH, "//span[contains(.,'Continuar')]").click()
        self.wait.until(
            EC.text_to_be_present_in_element((By.XPATH, "//h1"), "Dados escolares")
        )
        dropdown = self.driver.find_element(By.ID, "c3R1ZGVudHNbaV0uZ3JhZGU")
        dropdown.find_element(
            By.XPATH, "//option[. = '1º ano do ensino fundamental']"
        ).click()
        dropdown = self.driver.find_element(By.ID, "c3R1ZGVudHNbaV0ucGVyaW9k")
        dropdown.find_element(By.XPATH, "//option[. = 'matutino']").click()
        self.driver.find_element(By.XPATH, "//span[contains(.,'Continuar')]").click()
        self.wait.until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//h1"), "Número de Contratantes"
            )
        )
        self.driver.find_element(By.XPATH, "//span[contains(.,'Continuar')]").click()
        self.wait.until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//h1"), "Dados do(a) primeiro(a) Contratante"
            )
        )
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[2]/div/input"
        ).send_keys("Josué Pereira Signatário")
        for k in CPF:
            self.driver.find_element(
                By.XPATH, "//form[@id='daform']/div[3]/div/input"
            ).send_keys(k)
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[4]/div/input"
        ).send_keys("MG 10.406.279")
        self.driver.find_element(
            By.XPATH, "//span[contains(.,'divorciado(a)')]"
        ).click()
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[7]/div/input"
        ).send_keys("Engenheiro Civil")
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[8]/div/input"
        ).send_keys("josue.signatario@gmail.com")
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[9]/div/input"
        ).send_keys("31-98765-9090")
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[10]/div/input"
        ).send_keys("31-98765-9090")
        self.driver.find_element(By.XPATH, "//span[contains(.,'Continuar')]").click()
        self.wait.until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//h1"), "Endereço de Josué Pereira Signatário"
            )
        )
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[2]/div/input"
        ).send_keys("30220-220")
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[4]/div/input"
        ).click()
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[4]/div/input"
        ).send_keys("123")
        self.driver.find_element(
            By.XPATH, "//form[@id='daform']/div[5]/div/input"
        ).send_keys("Apto. 201")
        self.wait.until(
            EC.text_to_be_present_in_element_value(
                (By.XPATH, "//form[@id='daform']/div[3]/div/input"),
                "Rua Manoel Gomes Pereira",
            )
        )
        self.driver.find_element(By.XPATH, "//span[contains(.,'Continuar')]").click()
        self.wait.until(
            EC.text_to_be_present_in_element((By.XPATH, "//h1"), "Contratantes:")
        )
        self.driver.find_element(By.XPATH, "//span[contains(.,'Continuar')]").click()
        self.wait.until(
            EC.text_to_be_present_in_element((By.XPATH, "//h1"), "Ano Letivo")
        )
        self.driver.find_element(By.XPATH, "//span[contains(.,'Continuar')]").click()
        self.wait.until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//h1"), "Preço e Forma de Pagamento"
            )
        )
        self.driver.find_element(By.XPATH, "//form[@id=\'daform\']/div[2]/div/div/input").send_keys("14500")
        self.driver.find_element(By.XPATH, "//form[@id=\'daform\']/div[3]/div/fieldset/label").click()
        self.driver.find_element(By.XPATH, "//form[@id=\'daform\']/div[4]/div/div/textarea").send_keys(
            "foi concedido 10% sobre o valor anual")
        self.driver.find_element(By.XPATH, "//form[@id=\'daform\']/div[5]/div/fieldset/label[2]/span[2]").click()
        self.driver.find_element(By.XPATH, "//form[@id=\'daform\']/div[11]/div/div/input").send_keys("10")
        self.driver.find_element(By.XPATH, "//form[@id=\'daform\']/div[12]/div/div/div/input").send_keys("1000")
        self.driver.find_element(By.XPATH, "//form[@id=\'daform\']/div[13]/div/div/input").send_keys("2020-08-31")
        self.driver.find_element(By.XPATH, "//form[@id=\'daform\']/div[8]/div/div/fieldset/label").click()
        self.driver.find_element(By.XPATH, "//form[@id=\'daform\']/div[9]/div/div/div/input").send_keys("2000")
        self.driver.find_element(By.XPATH, "//form[@id=\'daform\']/div[10]/div/div/input").send_keys("2020-08-21")
        self.driver.find_element(By.XPATH, "//span[contains(.,'Continuar')]").click()
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