import os
from robocorp.tasks import task
from robocorp.tasks import get_output_dir
from robocorp import log
from RPA.Browser.Selenium import Selenium
from RPA.Excel.Files import Files as Excel
from RPA.HTTP import HTTP


@task
def browser_example():
    # open the browser anrpa challenged go to
    browser = Selenium()
    browser.open_available_browser('https://rpachallenge.com')

    # get the href attribute of the download link
    url = browser.get_element_attribute('//a[contains(text(),"Download Excel")]', 'href')
    file_path = os.path.join(get_output_dir(), 'challenge.xlsx')

    # download the file
    HTTP().download(url, file_path, overwrite=True)

    # open the work book
    excel = Excel()
    excel.open_workbook(file_path)

    # get the rows
    rows = excel.read_worksheet_as_table(header=True)
    excel.close_workbook()

    # start the challenge and do the data entry
    browser.click_button("Start")
    # loop through each record
    for row in rows:
        # loop through each column in the record and enter the text
        for column, value in row.items():
            browser.input_text(f"//div[label[text()='{column}']]/input", str(value))
        # submit the form
        browser.click_button('Submit')

    # get the result
    result = browser.get_text('css:div.message2')
    print(result)
    log.info(result)


if __name__ == '__main__':
    browser_example()