from robocorp.tasks import task
from robocorp.tasks import get_output_dir
from RPA.Browser.Selenium import Selenium

@task
def minimal_task():
    browser = Selenium()
    browser.open_available_browser('https://www.google.co.uk')