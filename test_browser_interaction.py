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
        caps['record_video'] = 'true'

        self.driver = webdriver.Remote(
            desired_capabilities=caps,
            #command_executor="http://%s:%s@hub.crossbrowsertesting.com:80/wd/hub"%(self.username,self.authkey)
            command_executor="http://hub.crossbrowsertesting.com:80/wd/hub"
        )

        self.driver.implicitly_wait(20)

    def test_CBT(self):

        try:
            baseUrl = "https://webdevel01.ltgc.com/rate-quote/external/residential'"
            self.driver.maximize_window()
            # Refreshing the browser clears the a popup that only appears in Chrome
            self.driver.get(baseUrl)

            # Get Title
            title = self.driver.title
            print("PASS:  Title of the web page is: " + title)
            # Get Current Url
            currentUrl = self.driver.current_url
            print("PASS:  Current Url of the web page is: " + currentUrl)
            self.driver.refresh()        # Browser Refresh

            print("PASS:  Browser Refreshed 1st time")
            self.driver.get(self.driver.current_url)
            print("PASS:  Browser Refreshed 2nd time")
            # Open another Url
            self.driver.get("https://www.ltgc.com/rates/calc")
            currentUrl = self.driver.current_url
            print("PASS:  Current Url of the web page is: " + currentUrl)
            # Browser Back
            self.driver.back()
            print("PASS:  Go one step back in browser history")
            currentUrl = self.driver.current_url
            print("PASS:  Current Url of the web page is: " + currentUrl)
            # Browser Forward
            self.driver.forward()
            print("PASS:  Go one step forward in browser history")
            currentUrl = self.driver.current_url
            print("PASS:  Current Url of the web page is: " + currentUrl)
            # Get Page Source
            pageSource = self.driver.page_source
            print(pageSource)
            # Browser Close / Quit
            # driver.close()

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
