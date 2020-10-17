import time

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ex_cond

PATH = "C:\Program Files (x86)\chromedriver_win32\chromedriver.exe"
driver = webdriver.Chrome(PATH)

test_url = "file:///C:/Users/Yuki/PycharmProjects/COEBadmintonReserve/webpage/Cart%20-%20move.learn.play.html"

before_XPath_1 = "//*[@class='table']/tbody/tr["
before_XPath_2 = "/td["
after_XPath = "]"

search_text = "The class is at or exceeding the maximum number of participants"

driver.get(test_url)

# time.sleep(30)
WebDriverWait(driver, 6).until(ex_cond.presence_of_element_located((By.CLASS_NAME, "table")))

try:
    print(driver.find_element_by_class_name("table").text)
except Exception as e:
    print("Oops!", e.__class__, "occurred.")
    print("not able to print cart table")


num_rows = len(driver.find_elements_by_xpath("//*[@class='table']/tbody/tr"))
num_columns = len(driver.find_elements_by_xpath("//*[@class = 'table']/tbody/tr[2]/td"))

elem_found = False

error_list = []

for t_row in range(2, (num_rows + 1), 2):
    FinalXPath = before_XPath_1 + str(t_row) + after_XPath + before_XPath_2 + str(1) + after_XPath
    cell_text = driver.find_element_by_xpath(FinalXPath).text
    if "Error" in cell_text:
        error_list.append(int(t_row/2))

print(error_list)

for rm in reversed(error_list):
    remove_buttons = driver.find_elements_by_class_name("BasketItemRemoveLink")
    try:
        ActionChains(driver).move_to_element(remove_buttons[rm-1]).perform()
    except Exception as e:
        print(str(e))
        print("scroll stuff")
    time.sleep(1)
    remove_buttons[rm-1].click()
    driver.back()


driver.quit()
