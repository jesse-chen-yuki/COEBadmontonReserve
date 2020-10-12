from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from datetime import date, timedelta, datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ex_cond
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException

# TODO:
# add logging feature
# add unit testing stuff
# examine booking issue conditions each time to check for resubmission.
# real world test with test = 0
# log the output for analysis

# need to resolve incomplete order after submission
# need to cut down on response time as spots get taken.
# look for error as the cart becomes unavailable and cancel the unavailable item
# examine closely when does check drop cart problem occur, retry from beginning

# branch, continuously find session, if not available keep trying until fulfilled.

# try again after 21 minutes
# case to look at 10-22

# change in strategy: book 2 only, wait for 20 min for second round


# testing variables
test = 1
cancel = 1
debug = 1
PATH = "C:\Program Files (x86)\chromedriver_win32\chromedriver.exe"
driver = webdriver.Chrome(PATH)


def pre_process():
    sessions_to_book = 2
    days_ahead = 14
    if test:
        # available test dates 15 19 22 23
        # current day ahead point to oct 16
        # Need to cancel all of: oct 15 16 19
        days_ahead = 8

    target_day = date.today() + timedelta(days=days_ahead)
    # default add 14 days, for programming may set to be closer

    date_of_target_day = target_day.strftime("%w")
    if debug:
        print("date of target day: ", date_of_target_day)

    session = session_selector(date_of_target_day)

    if test:
        # for testing
        sessions_to_book = 2
        session = 1  # to be changed every successful confirmation

    session_list = make_session_list(sessions_to_book, session)
    # session_list.reverse()

    # change target_day into input format
    target_day = target_day.strftime('%m/%d/%Y')
    return session_list, target_day


def session_selector(date_of_target_day):
    if date_of_target_day == "0":
        # Sunday
        print("in Sunday")
        session = 3
    elif date_of_target_day == "1":
        # Mon
        print("in Monday")
        session = 6
    elif date_of_target_day == "2":
        # Tues
        print("in Tuesday")
        session = 5
    elif date_of_target_day == "3":
        # Wed
        print("in Wednesday")
        session = 4
    elif date_of_target_day == "4":
        # Thurs
        print("in Thursday")
        session = 6
    elif date_of_target_day == "5":
        # Fri
        print("in Friday")
        session = 7
    elif date_of_target_day == "6":
        # Sat
        print("in Saturday")
        session = 5
    else:
        session = 3
    return session


def standby():
    now = datetime.now()
    if test:
        today830 = now.replace(hour=21, minute=59, second=59, microsecond=0)
    else:
        today830 = now.replace(hour=8, minute=29, second=58, microsecond=0)
        # use a close time to test the while

    while now < today830:
        if int(now.strftime("%H")) < int(today830.strftime("%H")):
            print("not in the right hour")
            time.sleep(60 * 25)
        elif int(now.strftime("%M")) < int(today830.strftime("%M")) - 10:
            print("more than 10 min early")
            time.sleep(60 * 9)
        elif int(now.strftime("%M")) < int(today830.strftime("%M")):
            print("more than 1 min early")
            time.sleep(50)
        else:
            time.sleep(1)
            print(datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
        now = datetime.now()


def make_session_list(sessions_to_book, session):
    session_list = [session]
    sessions_to_book -= 1
    while sessions_to_book > 0:
        session += 1
        session_list.append(session)
        sessions_to_book -= 1
    return session_list


def reserve(session_list, target_day):
    orig_list_size = len(session_list)
    attempt = 0
    max_try = len(session_list) + 8
    while len(session_list) > 0:
        # while more sessions to be booked
        attempt += 1
        if debug:
            print("attempt: ", attempt)
            print(datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
            print("to be booked session list: ", session_list)
        session_list = book_session(session_list, target_day)
        # print(len(session_list), session_list, min(session_list))
        if attempt > max_try:
            if debug:
                print("reached max try")
            # if there is something in the cart
            if len(session_list) < orig_list_size:
                # things in the cart
                # need to test this case
                if cancel:
                    if debug:
                        print("cancelling cart")
                    cancel_cart()
                else:
                    if debug:
                        print("checkout")
                    checkout()
            break


def cart_is_empty():
    driver.get("https://movelearnplay.edmonton.ca/COE/public/Basket/CheckoutBasket")
    try:
        driver.find_element_by_xpath("//*[contains(text(),'Your Cart is currently empty')]")
        # element=driver.find_element_by_partial_link_text("Your Cart is currently empty")
    except NoSuchElementException:
        # print("No element found")
        return 0
    return 1


def book_session(session_list, target_day):
    driver.get("https://movelearnplay.edmonton.ca/COE/public/category/browse/TCRCCOURTBAD")
    if test:
        end_date_box = driver.find_element_by_id("EndDate")
        end_date_box.clear()
        end_date_box.send_keys(target_day)
        end_date_box.send_keys(Keys.RETURN)
    start_date_box = driver.find_element_by_id("StartDate")
    start_date_box.clear()
    start_date_box.send_keys(target_day)
    start_date_box.send_keys(Keys.RETURN)
    start_date_box.send_keys(Keys.RETURN)
    if debug:
        # print(session_list)
        print(driver.find_element_by_class_name("table").text)
    links = driver.find_elements_by_class_name("BookNow")

    if len(links) == 0:
        # no available booking spots
        if debug:
            print("no available booking")
        return session_list
    elif len(links) < min(session_list):
        #  available spot become less than the target session
        if not cart_is_empty():
            if cancel:
                cancel_cart()
            else:
                checkout()
        print("did not complete ", session_list)
        session_list.clear()
        return session_list
    current_session = session_list.pop()
    try:
        # try to get the aimed session assuming all session available
        if debug:
            print("try to click on specific session")
        links[current_session - 1].send_keys(Keys.RETURN)
    except Exception as e:
        # return with original list
        if debug:
            print("specific session becomes unavailable ")
        print("Oops!", e.__class__, "occurred.")
        session_list.insert(0, current_session)
        return session_list
    try:
        qty = WebDriverWait(driver, 10).until(
            ex_cond.presence_of_element_located((By.NAME, "PriceGroupQuantities[MEMBER]"))
        )
        # qty.clear()
        qty.send_keys("1")
        qty.send_keys(Keys.RETURN)
    except Exception as e:
        print("Oops!", e.__class__, "occurred.")
        print("cant find price quantity to enter")

        time.sleep(5)

    try:
        # wait until find cart page
        if debug:
            print("try finding cart")
        WebDriverWait(driver, 10).until(
            ex_cond.presence_of_element_located((By.XPATH, "//*[contains(text(),'Cart')]"))
        )
    except Exception as e:
        print("Oops!", e.__class__, "occurred.")
        print("can't find cart")
        time.sleep(50)
    # time.sleep(1)

    if len(session_list) == 0:
        if cancel:
            cancel_cart()
        else:
            checkout()
        return session_list

    driver.get("https://movelearnplay.edmonton.ca/COE/public/category/browse/TCRCCOURTBAD")
    return session_list


def cancel_cart():
    cancel_option = 2
    driver.get("https://movelearnplay.edmonton.ca/COE/public/Basket")
    if cancel_option == 1:
        # cancel entire cart
        time.sleep(1)
        driver.get("https://movelearnplay.edmonton.ca/COE/public/Basket/ConfirmBasketCancellation")
        # time.sleep(2)

        try:
            cancel_cart_button = WebDriverWait(driver, 3).until(
                ex_cond.presence_of_element_located((By.XPATH, "//input[@type='submit']"))
            )
            cancel_cart_button.send_keys(Keys.RETURN)
        except Exception as e:
            print("Oops!", e.__class__, "occurred.")
            print("in bulk cancel")
            time.sleep(600)
        time.sleep(2)
    else:
        # cancel item by item
        try:
            if debug:
                print("going into cancel item by item")
            WebDriverWait(driver, 10).until(ex_cond.presence_of_element_located((By.CLASS_NAME, "table")))
            num_rows = len(driver.find_elements_by_xpath("//*[@class='table']/tbody/tr"))
            error_list = []
            for t_row in range(2, (num_rows + 1), 2):
                error_list.append(int(t_row / 2))
            print(error_list)
            for rm in reversed(error_list):
                remove_buttons = driver.find_elements_by_class_name("BasketItemRemoveLink")
                try:
                    ActionChains(driver).move_to_element(remove_buttons[rm - 1]).perform()
                except Exception as e:
                    print("Oops!", e.__class__, "occurred.")
                    print("scroll stuff")
                time.sleep(1)
                remove_buttons[rm - 1].click()
        except Exception as e:
            print("Oops!", e.__class__, "occurred.")
            return 0
        return 1


def login():
    email_box = driver.find_element_by_id("EmailAddress")
    email_box.send_keys("jesse.chen@yahoo.ca")
    pw_box = driver.find_element_by_id("Password")
    pw_box.send_keys("AyanamiRei:0COER")
    pw_box.send_keys(Keys.RETURN)


def handle_cart_error():
    before_xpath_1 = "//*[@class='table']/tbody/tr["
    before_xpath_2 = "/td["
    after_xpath = "]"
    # search_text = "The class is at or exceeding the maximum number of participants"

    try:
        if debug:
            print("in handle error trying to find session error")
        WebDriverWait(driver, 120).until(ex_cond.presence_of_element_located((By.CLASS_NAME, "table")))
        num_rows = len(driver.find_elements_by_xpath("//*[@class='table']/tbody/tr"))
        # num_columns = len(driver.find_elements_by_xpath("//*[@class = 'table']/tbody/tr[2]/td"))

        # elem_found = False

        error_list = []

        for t_row in range(2, (num_rows + 1), 2):
            final_xpath = before_xpath_1 + str(t_row) + after_xpath +\
                         before_xpath_2 + str(1) + after_xpath
            cell_text = driver.find_element_by_xpath(final_xpath).text
            if "Error" in cell_text:
                error_list.append(int(t_row / 2))

        print(error_list)

        for rm in reversed(error_list):
            remove_buttons = driver.find_elements_by_class_name("BasketItemRemoveLink")
            try:
                ActionChains(driver).move_to_element(remove_buttons[rm - 1]).perform()
            except Exception as e:
                print("Oops!", e.__class__, "occurred.")
                print("in removing error session place")
            time.sleep(1)
            remove_buttons[rm - 1].click()

    except Exception as e:
        print("Oops!", e.__class__, "occurred.")
        if debug:
            "error handle time out"
        return 0

    driver.get("https://movelearnplay.edmonton.ca/COE/public/Basket/CheckoutBasket")
    time.sleep(1)
    return 1


def checkout():
    confirmation = 0
    # assuming cart is non-empty
    time.sleep(1)
    driver.get("https://movelearnplay.edmonton.ca/COE/public/Basket/CheckoutBasket")
    print(datetime.now().strftime("submit order: %m/%d/%Y, %H:%M:%S"))

    try:
        if debug:
            print("finding email to enter")
            print("check if on the correct checkout page")
        WebDriverWait(driver, 10).until(
            ex_cond.presence_of_element_located((By.ID, "EmailAddress"))
        )
    except Exception as e:
        print("Oops!", e.__class__, "occurred.")
        print("cant find email to enter")
        driver.get("https://movelearnplay.edmonton.ca/COE/public/Basket/CheckoutBasket")
        time.sleep(1)
    login()

    # ISSUE:
    # check for potential submission error after login, need code to automatically resubmit order.
    # need to check for redirection to the cart and remove correct session

    # ISSUE
    # try to find error message
    try:
        assert handle_cart_error() == 1
    except Exception as e:
        print("Oops!", e.__class__, "occurred.")
        print("no error to handle")
    else:
        driver.get("https://movelearnplay.edmonton.ca/COE/public/Basket/CheckoutBasket")
        time.sleep(1)

    # may or may not get a request to agree to condition
    try:
        element = driver.find_elements_by_css_selector("input[type='radio'][id='AGREE']")[0]
    except Exception as e:
        print("Oops!", e.__class__, "occurred.")
        # no agree condition, submit order
        while confirmation == 0:
            try:
                if debug:
                    print("waiting for confirmation")
                element = WebDriverWait(driver, 120).until(
                    ex_cond.presence_of_element_located((By.ID, "BasketConfirmed"))
                )
                print(element.text)
                confirmation = 1
            except Exception as e:
                print("Oops!", e.__class__, "occurred.")
                if debug:
                    print("did not find basket confirmation")
                time.sleep(60)
        return ()

    try:
        ActionChains(driver).move_to_element(element).perform()
    except Exception as e:
        print("Oops!", e.__class__, "occurred.")
        time.sleep(2)
        print("scroll stuff")

    element.click()
    submit = driver.find_elements_by_css_selector("input[type='submit'][value='Submit']")[0]
    if not test:
        submit.send_keys(Keys.RETURN)

    try:
        WebDriverWait(driver, 180).until(
            ex_cond.presence_of_element_located((By.ID, "BasketConfirmed"))
        )
        element = driver.find_element_by_id("BasketConfirmed")
        print(element.text)
    except Exception as e:
        print("Oops!", e.__class__, "occurred.")
        if debug:
            print("need manual assistance")
        time.sleep(180)


def main():
    session_list, target_day = pre_process()
    standby()
    print(datetime.now().strftime("start reserve time: %m/%d/%Y, %H:%M:%S"))
    reserve(session_list, target_day)
    print(datetime.now().strftime("end reserve time: %m/%d/%Y, %H:%M:%S"))
    time.sleep(60)
    driver.quit()


main()
