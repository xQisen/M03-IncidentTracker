from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class SecurityRegressionTests(StaticLiveServerTestCase):
    fixtures = ['testdb.json']  # Càrrega de dades (Punt 2.2.2)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        opts = Options()
        opts.add_argument("--headless=new")  # mode Headless per Chrome
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        cls.selenium = WebDriver(options=opts)
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def test_role_restriction(self):
        """AUDITORIA: L'analista no ha d'entrar a /admin/"""
        # Anar a la pàgina de login
        self.selenium.get('%s%s' % (self.live_server_url, '/accounts/login/'))
        
        # Esperar que carregui el formulari
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        
        # Login amb analista1
        self.selenium.find_element(By.NAME, "username").send_keys("analista1")
        self.selenium.find_element(By.NAME, "password").send_keys("password123")
        self.selenium.find_element(By.XPATH, "//button[@type='submit']").click()
        
        # Esperar redirecció a /perfil/
        WebDriverWait(self.selenium, 10).until(
            EC.url_contains("/perfil/")
        )
        
        # Intentar forçar URL d'admin
        self.selenium.get('%s%s' % (self.live_server_url, '/admin/'))
        
        # ASSERT de Seguretat
        self.assertNotEqual(self.selenium.title, "Site administration | Django site admin")
