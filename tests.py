import unittest
import time
import os
import random
import subprocess
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = os.environ.get("APP_BASE_URL", "http://127.0.0.1:5000")

def get_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    return webdriver.Chrome(options=options)


class FlaskAppTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Seed the database with testuser1 before any tests run."""
        seed_script = """
import sys
sys.path.insert(0, '/app')
from app import app, db, User
from werkzeug.security import generate_password_hash
with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='testuser1').first():
        u = User(
            username='testuser1',
            email='testuser1@gmail.com',
            password=generate_password_hash('Test@1234')
        )
        db.session.add(u)
        db.session.commit()
        print('testuser1 seeded')
"""
        subprocess.run(['python3', '-c', seed_script], check=True)
        time.sleep(1)

    def setUp(self):
        self.driver = get_driver()
        self.wait = WebDriverWait(self.driver, 10)

    def tearDown(self):
        self.driver.quit()

    # TC01
    def test_01_login_page_loads(self):
        self.driver.get(f"{BASE_URL}/login")
        self.assertIn("Login", self.driver.page_source)

    # TC02
    def test_02_register_page_loads(self):
        self.driver.get(f"{BASE_URL}/register")
        self.assertIn("Register", self.driver.page_source)

    # TC03
    def test_03_register_form_fields_exist(self):
        self.driver.get(f"{BASE_URL}/register")
        self.assertTrue(self.driver.find_element(By.ID, "username"))
        self.assertTrue(self.driver.find_element(By.ID, "email"))
        self.assertTrue(self.driver.find_element(By.ID, "password"))

    # TC04
    def test_04_login_form_fields_exist(self):
        self.driver.get(f"{BASE_URL}/login")
        self.assertTrue(self.driver.find_element(By.ID, "username"))
        self.assertTrue(self.driver.find_element(By.ID, "password"))

    # TC05
    def test_05_successful_registration(self):
        random_id = random.randint(10000, 99999)
        self.driver.get(f"{BASE_URL}/register")
        self.driver.find_element(By.ID, "username").send_keys(f"testuser{random_id}")
        self.driver.find_element(By.ID, "email").send_keys(f"testuser{random_id}@gmail.com")
        self.driver.find_element(By.ID, "password").send_keys("Test@1234")
        self.driver.find_element(By.ID, "register-btn").click()
        time.sleep(2)
        self.assertIn("login", self.driver.current_url)

    # TC06
    def test_06_duplicate_username(self):
        self.driver.get(f"{BASE_URL}/register")
        self.driver.find_element(By.ID, "username").send_keys("testuser1")
        self.driver.find_element(By.ID, "email").send_keys("different99@gmail.com")
        self.driver.find_element(By.ID, "password").send_keys("Test@1234")
        self.driver.find_element(By.ID, "register-btn").click()
        time.sleep(1)
        self.assertIn("already exists", self.driver.page_source)

    # TC07
    def test_07_duplicate_email(self):
        self.driver.get(f"{BASE_URL}/register")
        self.driver.find_element(By.ID, "username").send_keys("newuser99")
        self.driver.find_element(By.ID, "email").send_keys("testuser1@gmail.com")
        self.driver.find_element(By.ID, "password").send_keys("Test@1234")
        self.driver.find_element(By.ID, "register-btn").click()
        time.sleep(1)
        self.assertIn("already registered", self.driver.page_source)

    # TC08
    def test_08_successful_login(self):
        self.driver.get(f"{BASE_URL}/login")
        self.driver.find_element(By.ID, "username").send_keys("testuser1")
        self.driver.find_element(By.ID, "password").send_keys("Test@1234")
        self.driver.find_element(By.ID, "login-btn").click()
        time.sleep(1)
        self.assertIn("dashboard", self.driver.current_url)

    # TC09
    def test_09_invalid_password(self):
        self.driver.get(f"{BASE_URL}/login")
        self.driver.find_element(By.ID, "username").send_keys("testuser1")
        self.driver.find_element(By.ID, "password").send_keys("WrongPass")
        self.driver.find_element(By.ID, "login-btn").click()
        time.sleep(1)
        self.assertIn("Invalid", self.driver.page_source)

    # TC10
    def test_10_nonexistent_user_login(self):
        self.driver.get(f"{BASE_URL}/login")
        self.driver.find_element(By.ID, "username").send_keys("ghostuser")
        self.driver.find_element(By.ID, "password").send_keys("pass123")
        self.driver.find_element(By.ID, "login-btn").click()
        time.sleep(1)
        self.assertIn("Invalid", self.driver.page_source)

    # TC11
    def test_11_dashboard_welcome_message(self):
        self.driver.get(f"{BASE_URL}/login")
        self.driver.find_element(By.ID, "username").send_keys("testuser1")
        self.driver.find_element(By.ID, "password").send_keys("Test@1234")
        self.driver.find_element(By.ID, "login-btn").click()
        time.sleep(1)
        welcome = self.driver.find_element(By.ID, "welcome-msg").text
        self.assertIn("testuser1", welcome)

    # TC12
    def test_12_logout(self):
        random_id = random.randint(10000, 99999)
        self.driver.get(f"{BASE_URL}/register")
        self.driver.find_element(By.ID, "username").send_keys(f"logoutuser{random_id}")
        self.driver.find_element(By.ID, "email").send_keys(f"logoutuser{random_id}@gmail.com")
        self.driver.find_element(By.ID, "password").send_keys("Test@1234")
        self.driver.find_element(By.ID, "register-btn").click()
        time.sleep(2)
        self.driver.find_element(By.ID, "username").send_keys(f"logoutuser{random_id}")
        self.driver.find_element(By.ID, "password").send_keys("Test@1234")
        self.driver.find_element(By.ID, "login-btn").click()
        time.sleep(2)
        self.driver.get(f"{BASE_URL}/logout")
        time.sleep(2)
        self.assertNotIn("dashboard", self.driver.current_url)

    # TC13
    def test_13_dashboard_requires_login(self):
        self.driver.get(f"{BASE_URL}/dashboard")
        time.sleep(1)
        self.assertIn("login", self.driver.current_url)

    # TC14
    def test_14_register_link_on_login_page(self):
        self.driver.get(f"{BASE_URL}/login")
        link = self.driver.find_element(By.ID, "register-link")
        self.assertTrue(link.is_displayed())

    # TC15
    def test_15_login_link_on_register_page(self):
        self.driver.get(f"{BASE_URL}/register")
        link = self.driver.find_element(By.ID, "login-link")
        self.assertTrue(link.is_displayed())


if __name__ == "__main__":
    unittest.main(verbosity=2)