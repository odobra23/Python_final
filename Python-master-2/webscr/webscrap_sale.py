from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import operator
from functools import reduce
import pandas as pd
import csv

options = webdriver.ChromeOptions()
options.binary_location = '/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary'
options.add_argument('window-size=800x841')
# options.add_argument('headless')

driver = webdriver.Chrome(chrome_options=options)
driver.get('http://sportowa.warszawa.pl/ksiazka-adresowa/obiekty_sportowe-258/sale_gimnastyczne-274')

sale = []

while True:
    try:
        ### arrays of selenium objects ###
        sale_elements_xpath = ("//div[@class='Label ui-accordion-header']")
        sale_elements = driver.find_elements_by_xpath(sale_elements_xpath)
        sale.append([x.text for x in sale_elements])

        #### pagination ####
        nextsite = driver.find_element_by_xpath("//span[@class='Next']//a")
        driver.execute_script("arguments[0].click();", nextsite)

    except NoSuchElementException:
        break
driver.quit()

### creating one list out of list of lists ###
all_gyms = reduce(operator.concat, sale)
dframe = pd.DataFrame(all_gyms)
dframe.to_csv("./gyms_WS.csv", encoding='utf-8', index=False, quoting=csv.QUOTE_ALL)
