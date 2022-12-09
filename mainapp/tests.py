from django.core import mail as django_mail

from mainapp import tasks as mainapp_tasks


class TestTaskMailSend(TestCase):
    fixtures = ("authapp/fixtures/001_user_admin.json",)

    def test_mail_send(self):
        message_text = "test_message_text"
        user_obj = authapp_models.CustomUser.objects.first()
        mainapp_tasks.send_feedback_mail({"user_id": user_obj.id, "message": message_text})
        self.assertEqual(django_mail.outbox[0].body, message_text)


from django.conf import settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class TestNewsSelenium(StaticLiveServerTestCase):

    fixtures = (
        "authapp/fixtures/001_user_admin.json",
        "mainapp/fixtures/001_news.json",
    )

    def setUp(self):
        super().setUp()
        self.selenium = WebDriver(executable_path=settings.SELENIUM_DRIVER_PATH_FF)
        self.selenium.implicitly_wait(10)
        # Login
        self.selenium.get(f"{self.live_server_url}{reverse('authapp:login')}")
        button_enter = WebDriverWait(self.selenium, 5).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, '[type="submit"]'))
        )
        self.selenium.find_element("id_username").send_keys("admin")
        self.selenium.find_element("id_password").send_keys("admin")
        button_enter.click()
        # Wait for footer
        WebDriverWait(self.selenium, 5).until(EC.visibility_of_element_located((By.CLASS_NAME, "mt-auto")))

    def test_create_button_clickable(self):
        path_list = f"{self.live_server_url}{reverse('mainapp:news')}"
        path_add = reverse("mainapp:news_create")
        self.selenium.get(path_list)
        button_create = WebDriverWait(self.selenium, 5).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, f'[href="{path_add}"]'))
        )
        print("Trying to click button ...")
        button_create.click()  # Test that button clickable
        WebDriverWait(self.selenium, 5).until(EC.visibility_of_element_located((By.ID, "id_title")))
        print("Button clickable!")
        # With no element - test will be failed
        # WebDriverWait(self.selenium, 5).until(
        #     EC.visibility_of_element_located((By.ID, "id_title111"))
        # )

    def test_pick_color(self):
        path = f"{self.live_server_url}{reverse('mainapp:main_page')}"
        self.selenium.get(path)
        navbar_el = WebDriverWait(self.selenium, 5).until(EC.visibility_of_element_located((By.CLASS_NAME, "navbar")))
        try:
            self.assertEqual(
                navbar_el.value_of_css_property("background-color"),
                "rgb(255, 255, 155)",
            )
        except AssertionError:
            with open("var/screenshots/001_navbar_el_scrnsht.png", "wb") as outf:
                outf.write(navbar_el.screenshot_as_png)
            raise

    def tearDown(self):
        # Close browser
        self.selenium.quit()
        super().tearDown()
