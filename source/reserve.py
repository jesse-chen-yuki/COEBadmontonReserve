from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from datetime import date, timedelta, datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException

# TODO:
# add logging feature
# add unit testing stuff
# examine booking issue conditions each time to check for resubmission.
# real world test with test = 0
# log the output for analysis

# need to resolve uncomplete order after submission

# waited too long, too many attempts after list not fulfillables -- done, need more test
# need to cut down on response time as spots get taken.
# set up if statement when available session less than minimum of session requested -- done, need more test

# look for error as the cart becomes unavailable and cancel the unavailable item

# resolve access to checkout too soon before complete session


# testing variables
test = 1
cancel = 0
debug = 1
PATH = "C:\Program Files (x86)\chromedriver_win32\chromedriver.exe"
driver = webdriver.Chrome(PATH)


def preProcess():
    sessionsToBeBooked = 3
    dayahead = 14
    if test:
        # current day ahead point to oct 8
        # Need to cancel all of: oct 8: 3:45
        # used up testing date oct *7
        dayahead = 2

    targetday = date.today() + timedelta(days=dayahead)
    # default add 14 days, for programming may set to be closer

    dateOfTargetDay = targetday.strftime("%w")
    if debug:
        print("date of target day: ", dateOfTargetDay)
    if dateOfTargetDay == "0":
        # Sunday starting 1045 as session 2
        print("in Sunday")
        session = 1
    elif dateOfTargetDay == "1":
        # Mon start 1545 as session 7
        print("in Monday")
        session = 5
    elif dateOfTargetDay == "2":
        # Tues start 1545 as session 7
        print("in Tuesday")
        session = 5
    elif dateOfTargetDay == "3":
        # Wed start 1415 as session 6
        print("in Wednesday")
        session = 6
    elif dateOfTargetDay == "4":
        # Thurs start 1415 as session 6
        print("in Thursday")
        session = 6
    elif dateOfTargetDay == "5":
        # Wed start 1415 as session 6
        print("in Friday")
        session = 4
    elif dateOfTargetDay == "6":
        # Sat start 1345 as session 5
        print("in Saturday")
        session = 5
    else:
        session = 6

    if test:
        # for testing
        sessionsToBeBooked = 3
        session = 1  # to be changed every successful confirmation

    sessionList = makeSessionList(sessionsToBeBooked, session)
    # sessionList.reverse()

    # change targetday into input format
    targetday = targetday.strftime('%m/%d/%Y')
    return sessionList, targetday


def standby():
    now = datetime.now()
    if test:
        today830 = now.replace(hour=8, minute=25, second=50, microsecond=0)
    else:
        today830 = now.replace(hour=8, minute=29, second=58, microsecond=0)
        # use a close time to test the while

    while now < today830:
        if int(today830.strftime("%H")) - int(now.strftime("%H")) > 1:
            print("more than 1 hr early")
            time.sleep(3600)
        elif int(today830.strftime("%M")) - int(now.strftime("%M")) > 10:
            print("more than 10 min early")
            time.sleep(600)
        elif int(today830.strftime("%M")) - int(now.strftime("%M")) >= 1:
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
    maxtry = len(sessionList) + 10
    while len(sessionList) > 0:
        # while more sessions to be booked
        if debug:
            print("attempt: ", attempt)
            print(datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
            print("to be booked session list: ", sessionList)
        sessionList = bookOneSession(sessionList, targetday)
        attempt += 1
        # print(len(sessionList), sessionList, min(sessionList))
        if attempt > maxtry:
            if debug:
                print("reached max try")
            # if there is something in the cart
            if len(sessionList) < origListSize:
                # things in the cart
                if cancel:
                    if debug:
                        print("cancelling cart")
                    cancelCart()
                else:
                    if debug:
                        print("checkout")
                    checkout()
            break


def cartEmpty():
    driver.get("https://movelearnplay.edmonton.ca/COE/public/Basket/CheckoutBasket")
    try:
        list = driver.find_element_by_xpath("//*[contains(text(),'Your Cart is currently empty')]")
        return 1
        # element=driver.find_element_by_partial_link_text("Your Cart is currently empty")
    except NoSuchElementException:
        # print("No element found")
        return 0


def bookOneSession(sessionList, targetday):
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
        # no available booking spots
        if debug:
            print("no available booking")
        return sessionList
    elif len(links) < min(sessionList):
        #  available spot become less than the target session
        if not cartEmpty():
            if cancel:
                cancelCart()
            else:
                checkout()
        print("did not complete ", sessionList)
        sessionList.clear()
        return sessionList
    currentSessionIndex = sessionList.pop()
    try:
        # try to get the aimed session assuming all session available
        if debug:
            print("try to click on specific session")
        links[currentSessionIndex - 1].send_keys(Keys.RETURN)
    except:
        # return with original list
        if debug:
            print("specific session becomes unavailable ")
        sessionList.insert(0, currentSessionIndex)
        return sessionList
    try:
        qty = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.NAME, "PriceGroupQuantities[MEMBER]"))
        )
        qty.clear()
        qty.send_keys("1")
        qty.send_keys(Keys.RETURN)

    except:
        print("cant find price quantity to enter")
        time.sleep(5)

    try:
        element = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.ID, "BookingModal"))
        )
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

    driver.get("https://movelearnplay.edmonton.ca/COE/public/category/browse/TCRCCOURTBAD")
    return sessionList


def cancelCart():
    time.sleep(1)
    driver.get("https://movelearnplay.edmonton.ca/COE/public/Basket/ConfirmBasketCancellation")
    # time.sleep(2)

    try:
        ccart = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.XPATH, "//input[@type='submit']"))
        )
        ccart.send_keys(Keys.RETURN)
    except:
        print("cant find price quantity to enter")
        time.sleep(600)
    time.sleep(2)


def login():
    id = driver.find_element_by_id("EmailAddress")
    id.send_keys("jesse.chen@yahoo.ca")
    pw = driver.find_element_by_id("Password")
    pw.send_keys("AyanamiRei:0COER")
    pw.send_keys(Keys.RETURN)


def checkout():
    confirmation = 0
    # assuming cart is non-empty

    time.sleep(1)
    driver.get("https://movelearnplay.edmonton.ca/COE/public/Basket/CheckoutBasket")

    # try:
    #     txt = WebDriverWait(driver, 3).until(
    #         EC.presence_of_element_located((By.XPATH,"//*[contains(text(),'Existing Client')]"))
    #     )
    # except:
    #     print("did not jump to checkout page")
    #     time.sleep(60)

    print(datetime.now().strftime("submit order: %m/%d/%Y, %H:%M:%S"))

    # ISSUE
    # verify no error, if no error then login, if error then cancel cart item with error
    try:
        if debug:
            print("finding email to enter")
            print("check if on the correct checkout page")
        id = WebDriverWait(driver, 1).until(
            EC.presence_of_element_located((By.ID, "EmailAddress"))
        )
    except:
        print("cant find email to enter")
        driver.get("https://movelearnplay.edmonton.ca/COE/public/Basket/CheckoutBasket")
    login()
    # time.sleep(2)
    # may or may not get a request to agree to condition

    try:
        element = driver.find_elements_by_css_selector("input[type='radio'][id='AGREE']")[0]
    except:
        # no agree condition, submit order
        while confirmation == 0:
            try:
                # ISSUE:
                # check for potential submission error need code to automatically resubmit order.
                # need to check for redirection to the cart
                if debug:
                    print("waiting for confirmation")
                element = WebDriverWait(driver, 60).until(
                    EC.presence_of_element_located((By.ID, "BasketConfirmed"))
                )
                print(element.text)
                confirmation = 1
            except:
                if debug:
                    print("did not find basket confirmation")

                # wait for presence of error message
                # element = WebDriverWait(driver, 60).until(
                #   EC.presence_of_element_located((By.ID, "BasketConfirmed"))
                # )

                time.sleep(60)
        return ()

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
        if debug:
            print("need manual assistance")
        time.sleep(180)


def main():
    sessionList, targetday = preProcess()
    standby()
    print(datetime.now().strftime("start reserve time: %m/%d/%Y, %H:%M:%S"))
    reserve(sessionList, targetday)
    print(datetime.now().strftime("end reserve time: %m/%d/%Y, %H:%M:%S"))
    time.sleep(2)
    driver.quit()


main()
