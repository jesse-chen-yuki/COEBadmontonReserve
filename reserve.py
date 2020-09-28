from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from datetime import date, timedelta, datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import logging

# TODO:
# implement list of session to be booked in priority order.
# add logging feature
# real world test with test = 0
# add unit testing stuff

PATH = "C:\Program Files (x86)\chromedriver_win32\chromedriver.exe"
driver = webdriver.Chrome(PATH)
# testing variables
test = 0
cancel = 0
debug = 1


def standby():
    now = datetime.now()
    if test:
        today830 = now.replace(hour=0, minute=11, second=0, microsecond=0)
    else:
        today830 = now.replace(hour=8, minute=30, second=0, microsecond=0)
        # use a close time to test the while

    while now < today830:

        if int(today830.strftime("%H")) - int(now.strftime("%H")) > 1:
            print("more than 1 hr early")
            time.sleep(3600)
        elif int(today830.strftime("%M")) - int(now.strftime("%M")) > 10:
            print("more than 10 min early")
            time.sleep(600)
        elif int(today830.strftime("%M")) - int(now.strftime("%M")) > 1:
            print("more than 1 min early")
            time.sleep(60)
        else:
            time.sleep(1)
            print(datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
        now = datetime.now()


def reserve():
    sessionsToBeBooked = 3
    maxtry = sessionsToBeBooked + 3
    attempt = 1
    dayahead = 14
    if test:
        dayahead = 1

    targetday = date.today() + timedelta(days=dayahead)
    # default add 14 days, for programming may set to be closer

    dateOfToday = targetday.strftime("%w")
    if debug:
        print("dateoftoday: %i", dateOfToday)
    if dateOfToday == "0":
        # Sunday starting 1045 as session 2
        print("in Sunday")
        session = 2
    elif dateOfToday == "1":
        # Mon start 1715 as session 8
        print("in Tuesday")
        session = 2
    elif dateOfToday == "2":
        # Tues start 1715 as session 8
        print("in Tuesday")
        session = 8
    elif dateOfToday == "3":
        # Wed start 1715 as session 8
        print("in Wednesday")
        session = 8
    elif dateOfToday == "6":
        # Sat start 1345 as session 5
        print("in Saturday")
        session = 5
    else:
        session = 3

    if test:
        # for testing
        sessionsToBeBooked = 3
        session = 2  # to be changed every successful confirmation

    # change targetday into input format
    targetday = targetday.strftime('%m/%d/%Y')

    # PATH = "C:\Program Files (x86)\chromedriver_win32\chromedriver.exe"
    # global driver
    # driver = webdriver.Chrome(PATH)

    while sessionsToBeBooked:
        if debug:
            print("attempt: %i", attempt)
            print(datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
        sessionsToBeBooked, session = bookOneSession(session, sessionsToBeBooked, targetday)

        if debug:
            print(sessionsToBeBooked, session)
        attempt += 1
        if attempt > maxtry:
            checkout()
            break


def bookOneSession(session, sessionsToBeBooked, targetday):
    # while more sessions to be booked
    driver.get("https://movelearnplay.edmonton.ca/COE/public/category/browse/TCRCCOURTBAD")
    startDateBox = driver.find_element_by_id("StartDate")
    startDateBox.clear()
    startDateBox.send_keys(targetday)
    startDateBox.send_keys(Keys.RETURN)
    startDateBox.send_keys(Keys.RETURN)
    if debug:
        print("sessionsToBeBooked: %i", sessionsToBeBooked)
        print(driver.find_element_by_class_name("table").text)
    links = driver.find_elements_by_class_name("BookNow")
    counter = 1
    for link in links:
        # print("enter link")
        if counter == session:
            # if current link is the target link
            link.send_keys(Keys.RETURN)
            try:
                element = WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located((By.NAME, "PriceGroupQuantities[MEMBER]"))
                )
            except:
                print("cant find price quantity to enter")
                time.sleep(50)

            # time.sleep(1)
            qty = driver.find_element_by_name("PriceGroupQuantities[MEMBER]")
            qty.clear()
            qty.send_keys("1")
            qty.send_keys(Keys.RETURN)

            try:
                element = WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located((By.ID, "BookingModal"))
                )
            except:
                print("can't find cart")
                time.sleep(50)
            # time.sleep(1)

            sessionsToBeBooked -= 1
            if sessionsToBeBooked == 0:
                if cancel:
                    cancelCart()
                else:
                    checkout()
                return sessionsToBeBooked, session

            session += 1
            driver.get("https://movelearnplay.edmonton.ca/COE/public/category/browse/TCRCCOURTBAD")
            break

        elif counter == 15:
            logging.DEBUT("counter over 15")
            break

        counter += 1
        # increase target link
    return sessionsToBeBooked, session


def cancelCart():
    time.sleep(2)
    driver.get("https://movelearnplay.edmonton.ca/COE/public/Basket/ConfirmBasketCancellation")
    ccart = driver.find_element_by_xpath("//input[@type='submit']")
    ccart.send_keys(Keys.RETURN)
    time.sleep(2)


def checkout():
    time.sleep(1)
    driver.get("https://movelearnplay.edmonton.ca/COE/public/Basket/CheckoutBasket")
    id = driver.find_element_by_id("EmailAddress")
    id.send_keys("jesse.chen@yahoo.ca")
    pw = driver.find_element_by_id("Password")
    pw.send_keys("AyanamiRei:0COER")
    print(datetime.now().strftime("submit order: %m/%d/%Y, %H:%M:%S"))
    pw.send_keys(Keys.RETURN)
    # time.sleep(2)

    # may or may not get a request to agree to condition

    try:
        element = driver.find_elements_by_css_selector("input[type='radio'][id='AGREE']")[0]
    except:
        # no agree condition, show confirmation
        try:
            element = WebDriverWait(driver, 240).until(
                EC.presence_of_element_located((By.ID, "BasketConfirmed"))
            )
            element = driver.find_element_by_id("BasketConfirmed")
            print(element.text)
        except:
            time.sleep(240)
        return ()

    # element = driver.find_dlement_by_xpath()
    # elm = driver.find_element_by_id("AGREE")
    # try:
    #     elm = WebDriverWait(driver, 5).until(
    #      EC.element_to_be_clickable((By.CLASS_NAME, "radio"))
    #  )
    # except:
    #     time.sleep(10)
    try:
        ActionChains(driver).move_to_element(element).perform()
    except:
        time.sleep(2)
        print("scroll stuff")

    element.click()
    submit = driver.find_elements_by_css_selector("input[type='submit'][value='Submit']")[0]
    if not test:
        submit.send_keys(Keys.RETURN)

    try:
        element = WebDriverWait(driver, 180).until(
            EC.presence_of_element_located((By.ID, "BasketConfirmed"))
        )
        element = driver.find_element_by_id("BasketConfirmed")
        print(element.text)
    except:
        time.sleep(180)


def main():
    # login with account
    # login()

    standby()
    print(datetime.now().strftime("start reserve time: %m/%d/%Y, %H:%M:%S"))
    reserve()
    print(datetime.now().strftime("end reserve time: %m/%d/%Y, %H:%M:%S"))
    time.sleep(2)
    driver.quit()


main()
