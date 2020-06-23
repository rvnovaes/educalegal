import time
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from .parameters import LOCAL_DRIVER, WAIT_TIME


class WebTest:
    def setup_method(self, method):
        if LOCAL_DRIVER:
            self.driver = webdriver.Chrome()
        else:
            self.driver = webdriver.Remote(
                command_executor="http://jenkins.educalegal.com.br:8444/wd/hub",
                desired_capabilities={"browserName": "chrome", "javascritptEnabled": True},
            )

        self.driver.implicitly_wait(WAIT_TIME)
        self.wait = WebDriverWait(self.driver, WAIT_TIME)
        self.vars = {}

    def teardown_method(self, method):
        self.driver.quit()

    def wait_for_window(self, timeout=2):
        time.sleep(round(timeout / 1000))
        wh_now = self.driver.window_handles
        wh_then = self.vars["window_handles"]
        if len(wh_now) > len(wh_then):
            return set(wh_now).difference(set(wh_then)).pop()