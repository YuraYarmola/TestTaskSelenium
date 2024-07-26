from RPA.Browser.Selenium import Selenium


def open_google():
    browser = Selenium()
    browser.open_available_browser("https://www.google.com")
    browser.screenshot("google_homepage.png")
    browser.close_all_browsers()


if __name__ == "__main__":
    open_google()
