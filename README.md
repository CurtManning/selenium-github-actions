<h1>Getting Started with GitHub Actions and CrossBrowserTesting</h1>
<p><em>For this document, we provide all example files in our <a href="https://github.com/crossbrowsertesting/selenium-github_actions">GitHub Actions GitHub Repository</a>.</em></p>
<p><a href="https://github.com/features/actions">GitHub Actions</a> is a CI/CD tool that lets you automate your development process.  <a href="https://github.com/features/actions">GitHub Actions</a> lets you build, test, and deploy your code all from GitHub quickly, safely, and at scale.  Every time you push, a build is created and automatically run, allowing you to easily test every commit.</p>
<p>In this guide we will use GitHub Actions for testing using the <a href="https://www.seleniumhq.org/">Selenium Webdriver</a> and <a href="https://www.python.org/">Python</a> programming language.</p>
<h2>Creating A GitHub Actions Work Flow</h2>
<p>1. Select the Actions button for your repository</p>
<p><img src="http://help.crossbrowsertesting.com/wp-content/uploads/2019/11/Github_actions_actions.png" /></p>
<p>2. We'll be using the Python Package Workflow for this example</p>
<p><img src="http://help.crossbrowsertesting.com/wp-content/uploads/2019/11/GitHub_actions_python_workflow.png" /></p>
<p>3. Make the following changes to the workflow .yml file and commit</p>
<p><img src="http://help.crossbrowsertesting.com/wp-content/uploads/2019/11/github_actions_pythonyml.png" /></p>
<pre><code>name: Python package
on: [push]

jobs:
  build:

    runs-on: ubuntu-latest
    strategy:
      max-parallel: 4
      matrix:
        python-version: [2.7, 3.5, 3.7]

    steps:
    - uses: actions/checkout@v1
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v1
      with:
        python-version: ${{ matrix.python-version }}
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    - name: Lint with flake8
      run: |
        pip install flake8
        # stop the build if there are Python syntax errors or undefined names
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
        # exit-zero treats all errors as warnings. The GitHub editor is 127 chars wide
        flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
    - name: Test With CrossBrowserTesting
      env:
        CBT_USERNAME: ${{ secrets.CBT_USERNAME }}
        CBT_AUTHKEY: ${{ secrets.CBT_AUTHKEY }}
      run: |
        python test.py </code></pre>
<h2>Setting up a test</h2>
<p>1. Create file test.py, add the following, and commit:</p>
<pre><code>import unittest
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
            self.driver.get('http://crossbrowsertesting.github.io/login-form.html')
            self.driver.maximize_window()
            self.driver.find_element_by_name('username').send_keys('tester@crossbrowsertesting.com')
            self.driver.find_element_by_name('password').send_keys('test123')
            self.driver.find_element_by_css_selector('body &gt; div &gt; div &gt; div &gt; div &gt; form &gt; div.form-actions &gt; button').click()

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
    unittest.main()</code></pre>
<p>2. Create file requirements.txt  and commit with the following:</p>
<pre><code>requests==2.22.0
selenium==3.141.0</code></pre>
<h2>Setting Your Username and Authkey For Your Workflow</h2>
<div class="blue-alert">You’ll need to use your Username and Authkey to run your tests on CrossBrowserTesting. To get yours, sign up for a <a href="https://crossbrowsertesting.com/freetrial"><b>free trial</b></a> or purchase a <a href="https://crossbrowsertesting.com/pricing"><b>plan</b></a>.</div>
<p>Your username and authkey will be used in your workflow as environment variables.</p>
<p>1. Settings</p>
<p><img src="http://help.crossbrowsertesting.com/wp-content/uploads/2019/11/github_actions_settings.png" /></p>
<p>2. Add the username and authkey as Secrets</p>
<p><img src="http://help.crossbrowsertesting.com/wp-content/uploads/2019/11/github_actions_secrets.png" /></p>
<p>3. Add CBT_USERNAME</p>
<p><img src="http://help.crossbrowsertesting.com/wp-content/uploads/2019/11/github_actions_secerts1.png" /></p>
<p>4. Add CBT_AUTHKEY</p>
<p><img src="http://help.crossbrowsertesting.com/wp-content/uploads/2019/11/github_actions_secerts2.png" /></p>
<p>Congratulations! You have now successfully integrated CBT and GitHub Actions. Now you are ready to see your build run from the GitHub Actions dashboard and in the <a href="https://app.crossbrowsertesting.com/selenium/results">Crossbrowsertesting app</a>.</p>
<h3>Conclusions</h3>
<p>By following the steps outlined in this guide, you are now able to seamlessly integrate GitHub Actions and CrossBrowserTesting. If you have any questions or concerns, please feel free to reach out to our <a href="mailto:support@crossbrowsertesting.com">support team</a>.</p>
