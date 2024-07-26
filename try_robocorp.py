from robocorp.tasks import task
from robocorp.tasks import get_output_dir
from RPA.Browser.Selenium import Selenium
from selenium.webdriver.common.keys import Keys

@task
def minimal_task():
  browser = Selenium(auto_close = False)
  browser.open_available_browser('https://www.google.co.uk')
  browser.click_button('Accept all')
  browser.input_text('name:q','rpaframework' +Keys.ENTER)
