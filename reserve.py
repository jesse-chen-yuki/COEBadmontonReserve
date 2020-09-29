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
# early login before start time -- REJECT due to slower process
# find book element into wait for element to exist. -- REJECT due to logical order
# change bookonesession to have precise session booking instead of iteration. -- DONE
# implement list of session to be booked in priority order or reverse order -- DONE by list pop
# add logging feature
# add unit testing stuff
# real world test with test = 0
# log the output for analysis


# testing variables
test = 0
cancel = 0
debug = 1
PATH = "C:\Program Files (x86)\chromedriver_win32\chromedriver.exe"
driver = webdriver.Chrome(PATH)

def preProcess():
    sessionsToBeBooked = 3
    dayahead = 14
    if test:
        # current 4 day ahead point to 10/02
        # used up testing date oct 01 09
        # Need to cancel all of: 10/02
        dayahead = 15

    targetday = date.today() + timedelta(days=dayahead)
    # default add 14 days, for programming may set to be closer

    dateOfTargetDay = targetday.strftime("%w")
    if debug:
        print("date of target day: ", dateOfTargetDay)
    if dateOfTargetDay == "0":
        # Sunday starting 1045 as session 2
        print("in Sunday")
        session = 2
    elif dateOfTargetDay == "1":
        # Mon start 1545 as session 7
        print("in Tuesday")
        session = 2
    elif dateOfTargetDay == "2":
        # Tues start 1545 as session 7
        print("in Tuesday")
        session = 7
    elif dateOfTargetDay == "3":
        # Wed start 1545 as session 7
        print("in Wednesday")
        session = 7
    elif dateOfTargetDay == "5":
        # Wed start 1415 as session 6
        print("in Friday")
        session = 6
    elif dateOfTargetDay == "6":
        # Sat start 1345 as session 5
        print("in Saturday")
        session = 5
    else:
        session = 3

    if test:
        # for testing
        sessionsToBeBooked = 2
        session = 2  # to be changed every successful confirmation

    sessionList = makeSessionList(sessionsToBeBooked, session)
    # sessionList.reverse()

    # change targetday into input format
    targetday = targetday.strftime('%m/%d/%Y')
    return sessionList, targetday



def login():
    id = driver.find_element_by_id("EmailAddress")
    id.send_keys("jesse.chen@yahoo.ca")
    pw = driver.find_element_by_id("Password")
    pw.send_keys("AyanamiRei:0COER")
    pw.send_keys(Keys.RETURN)


def standby():
    now = datetime.now()
    if test:
        today830 = now.replace(hour=0, minute=1, second=0, microsecond=0)
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


def makeSessionList(sessionsToBeBooked, session):
    aList = [session]
    sessionsToBeBooked -= 1
    while sessionsToBeBooked > 0:
        session += 1
        aList.append(session)
        sessionsToBeBooked -= 1
    return aList


def reserve(sessionList, targetday):
    origListSize = len(sessionList)
    attempt = 1
    maxtry = len(sessionList) + 5
    while len(sessionList) > 0:
        if debug:
            print("attempt: ", attempt)
            print(datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
            print("to be booked session list: ", sessionList)
        sessionList = bookOneSession(sessionList, targetday)
        attempt += 1
        if attempt > maxtry:
            # if there is something in the cart
            if debug:
                print("reached max try")
            if len(sessionList) < origListSize:
                #things in the cart
                if cancel:
                    if debug:
                        print("cancelling cart")
                    cancelCart()
                else:
                    if debug:
                        print("checkout")
                    checkout()

            break


def bookOneSession(sessionList, targetday):
    # while more sessions to be booked
    driver.get("https://movelearnplay.edmonton.ca/COE/public/category/browse/TCRCCOURTBAD")
    if test:
        endDateBox = driver.find_element_by_id("EndDate")
        endDateBox.clear()
        endDateBox.send_keys(targetday)
        endDateBox.send_keys(Keys.RETURN)
    startDateBox = driver.find_element_by_id("StartDate")
    startDateBox.clear()
    startDateBox.send_keys(targetday)
    startDateBox.send_keys(Keys.RETURN)
    startDateBox.send_keys(Keys.RETURN)
    if debug:
        # print(sessionList)
        print(driver.find_element_by_class_name("table").text)
    links = driver.find_elements_by_class_name("BookNow")

    if len(links) == 0:
        if debug:
            print("no available booking")
        return sessionList
    currentSessionIndex = sessionList.pop()
    try:
        # try to get the aimed session assuming all session available
        links[currentSessionIndex - 1].send_keys(Keys.RETURN)
    except:
        sessionList.insert(0,currentSessionIndex)
        return sessionList
    try:
        qty = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.NAME, "PriceGroupQuantities[MEMBER]"))
        )

        # element = WebDriverWait(driver, 3).until(
        #    EC.presence_of_element_located((By.NAME, "PriceGroupQuantities[MEMBER]"))
        # )

    except:
        print("cant find price quantity to enter")
        time.sleep(50)

    # time.sleep(1)
    # qty = driver.find_element_by_name("PriceGroupQuantities[MEMBER]")
    qty.clear()
    qty.send_keys("1")
    qty.send_keys(Keys.RETURN)

    try:
        element = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.ID, "BookingModal"))
        )
        # sessionsToBeBooked -= 1
    except:
        print("can't find cart")
        time.sleep(50)
    # time.sleep(1)

    if len(sessionList) == 0:
        if cancel:
            cancelCart()
        else:
            checkout()
        return sessionList

    # session += 1
    driver.get("https://movelearnplay.edmonton.ca/COE/public/category/browse/TCRCCOURTBAD")
    return sessionList


def cancelCart():
    time.sleep(2)
    driver.get("https://movelearnplay.edmonton.ca/COE/public/Basket/ConfirmBasketCancellation")
    # time.sleep(2)
    ccart = driver.find_element_by_xpath("//input[@type='submit']")
    ccart.send_keys(Keys.RETURN)
    time.sleep(2)


def checkout():
    # assuming card is non-empty
    time.sleep(1)
    driver.get("https://movelearnplay.edmonton.ca/COE/public/Basket/CheckoutBasket")
    print(datetime.now().strftime("submit order: %m/%d/%Y, %H:%M:%S"))
    login()
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
            # element = driver.find_element_by_id("BasketConfirmed")
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
    # pre-login is slower
    sessionList, targetday = preProcess()
    standby()
    print(datetime.now().strftime("start reserve time: %m/%d/%Y, %H:%M:%S"))
    reserve(sessionList, targetday)
    print(datetime.now().strftime("end reserve time: %m/%d/%Y, %H:%M:%S"))
    time.sleep(2)
    driver.quit()


main()
