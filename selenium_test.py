import unittest
from selenium import webdriver
import requests
import os
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

class LoginForm(unittest.TestCase):
    def setUp(self):

        # Put your username and authkey below
        # You can find your authkey at crossbrowsertesting.com/account
        self.username = os.environ.get('CBT_USERNAME')
        self.authkey  = os.environ.get('CBT_AUTHKEY')

        self.api_session = requests.Session()
        self.api_session.auth = (self.username,self.authkey)

        self.test_result = None

        caps = {}

        caps['name'] = 'Github Actions Example'
        caps['browserName'] = 'Chrome'
        caps['platform'] = 'Windows 10'
        caps['screenResolution'] = '1366x768'
        caps['username'] = self.username
        caps['password'] = self.authkey


        self.driver = webdriver.Remote(
            desired_capabilities=caps,
            #command_executor="http://%s:%s@hub.crossbrowsertesting.com:80/wd/hub"%(self.username,self.authkey)
            command_executor="http://hub.crossbrowsertesting.com:80/wd/hub"
        )

        self.driver.implicitly_wait(20)

    def test_CBT(self):
    
        try:
            self.driver.get('http://crossbrowsertesting.github.io/login-form.html')
            self.driver.maximize_window()
            self.driver.find_element_by_name('username').send_keys('tester@crossbrowsertesting.com')
            self.driver.find_element_by_name('password').send_keys('test123')
            self.driver.find_element_by_css_selector('body > div > div > div > div > form > div.form-actions > button').click()

            elem = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id=\"logged-in-message\"]/h2'))
            )

            welcomeText = elem.text
            self.assertEqual("Welcome tester@crossbrowsertesting.com", welcomeText)

            print("Taking snapshot")
            snapshot_hash = self.api_session.post('https://crossbrowsertesting.com/api/v3/selenium/' + self.driver.session_id + '/snapshots').json()['hash']

            self.test_result = 'pass'

        except AssertionError as e:
            # log the error message, and set the score to "during tearDown()".
            self.api_session.put('https://crossbrowsertesting.com/api/v3/selenium/' + self.driver.session_id + '/snapshots/' + snapshot_hash,
                data={'description':"AssertionError: " + str(e)})
            self.test_result = 'fail'
            raise

    def tearDown(self):
        print("Done with session %s" % self.driver.session_id)
        self.driver.quit()
        # Here we make the api call to set the test's score.
        # Pass it it passes, fail if an assertion fails, unset if the test didn't finish
        if self.test_result is not None:
            self.api_session.put('https://crossbrowsertesting.com/api/v3/selenium/' + self.driver.session_id,
                data={'action':'set_score', 'score':self.test_result})


if __name__ == '__main__':
    unittest.main()
