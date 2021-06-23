from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from datetime import date, timedelta, datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ex_cond
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
import source.secrets as ss

# TODO:
# short term goals:

#
# change finding correct slot as more pages exist now
# error detection and handling logic
# after deletion of error, need checkout
# change in strategy: book 2 only, wait for 20 min for second round manual
# part two of booking, wait until session change from full to book and book it.
# recording of online availability for 3 minutes with 1 sec interval


# need testing:
# rewrite session selector using start session, number of sessions, location select -- DONE

# long term goals:
# add logging feature
# add unit testing stuff
# log the output for analysis
# study branch pull merge git stuff
# branch make single session booking with multiple account, multi-thread.
# make function to print out availability as time elapse for the first 5 minutes, second by second


# Global testing variables
test = 1
cancel = 1
debug = 1
pre_login = 1
location_num = 1
# days ahead as of Mon 06-21
# 14 days is Mon July 5
# need 13, 14
#
days_ahead = 13

PATH = "C:\Program Files (x86)\chromedriver_win32\chromedriver.exe"
driver = webdriver.Chrome(PATH)


def login():
    email_box = driver.find_element_by_id("EmailAddress")
    email_box.send_keys(ss.user)
    pw_box = driver.find_element_by_id("Password")
    pw_box.send_keys(ss.pw)
    pw_box.send_keys(Keys.RETURN)


def pre_process():
    global days_ahead
    # dictionary containing the slot list per day
    time_slot_dict = {
        0: ['9:15 AM', '10:45 AM', '12:15 PM', '1:45 PM', '3:15 PM'],
        1: ['6:45 AM', '8:15 AM', '9:45 AM', '11:15 AM', '12:45 PM', '2:15 PM', '3:45 PM', '5:15 PM',
            '6:45 PM'],
        2: ['6:45 AM', '8:15 AM', '9:45 AM', '11:15 AM', '12:45 PM', '2:15 PM', '3:45 PM', '5:15 PM',
            '6:45 PM'],
        3: ['6:45 AM', '8:15 AM', '9:45 AM', '11:15 AM', '12:45 PM', '2:15 PM', '3:45 PM', '5:15 PM',
            '6:45 PM'],
        4: ['6:45 AM', '8:15 AM', '9:45 AM', '11:15 AM', '12:45 PM', '2:15 PM', '3:45 PM', '5:15 PM',
            '6:45 PM'],
        5: ['6:45 AM', '8:15 AM', '9:45 AM', '11:15 AM', '12:45 PM', '2:15 PM', '3:45 PM', '5:15 PM'],
        6: ['7:45 AM', '9:15 AM', '10:45 AM', '12:15 PM', '1:45 PM', '3:15 PM', '4:45 PM']
    }

    # location links may be changing as website updates
    def select_location(loc_num):
        # 1 as TCRC, 2 as Meadows, 3 as Stadium
        location = ''
        if loc_num == 1:
            location = 'TCRC'
        elif loc_num == 2:
            location = 'TMCRC'
        elif loc_num == 3:
            location = 'COMWTH'
        link_pre = 'https://movelearnplay.edmonton.ca/COE/public/category/browse/'
        # link_post = 'BADM'
        link_post = 'COURT'  # after covid
        return link_pre + location + link_post

    def make_session_list(first, num_to_book):
        session = first
        session_list_in = [session]
        num_to_book -= 1
        while num_to_book > 0:
            session += 1
            session_list_in.append(session)
            num_to_book -= 1
        return session_list_in

    # rule for deciding which session to book:
    # may change with different DATS signup
    # June 2021
    # book last 2 session on Monday, last 2 session on TuWTr
    # start with these and work to earlier
    def session_select(day_ahead_in, time_slot):
        # branch return list of timeSlots

        target_day_in = date.today() + timedelta(days=day_ahead_in)
        day = int(target_day_in.strftime("%w"))
        # change target_day into input format
        target_day_in = target_day_in.strftime('%m/%d/%Y')

        max_sessions_by_day = [len(time_slot[i]) for i in time_slot]
        if day == 0 or day == 6:
            # weekend
            sessions_book = 3
        elif day == 1:
            # Monday
            sessions_book = 2
        else:
            # Tues-Fri
            sessions_book = 3
        session_one = max_sessions_by_day[day] - sessions_book

        return session_one, sessions_book, target_day_in, day

    def get_book_slots(sessions, date_tar, time_slots):
        # may be different for different facilities
        # Mon-Thur, Fri, Sat, Sun
        # TCRC
        slots = time_slots[date_tar]
        str_list = []
        for i in sessions:
            str_list.append(slots[i])
        return str_list

    # login first before reserving sessions
    if pre_login:
        driver.get("https://movelearnplay.edmonton.ca/COE/public/Logon/Logon")
        login()
    # construct location link based on the choice
    location_link = select_location(location_num)
    driver.get(location_link)

    if test:
        # available test dates 20+
        # current day ahead point to oct
        # Need to cancel all of: 11-05 morning,
        # cancel queue: Oct
        # may be good to call to cancel
        days_ahead = 1
        first_session, sessions_to_book, target_day, date_of_target = session_select(days_ahead, time_slot_dict)
        # first_session = 7  # to be changed every successful confirmation
        # sessions_to_book = 2
    else:
        first_session, sessions_to_book, target_day, date_of_target = session_select(days_ahead, time_slot_dict)

    session_list = make_session_list(first_session, sessions_to_book)

    session_list_str = get_book_slots(session_list, date_of_target, time_slot_dict)

    print(session_list, session_list_str, target_day, location_link)
    return session_list, session_list_str, target_day, location_link


def standby():
    # wait a certain amount of time and go to target webpage
    # submit date request return list of booking items
    now = datetime.now()
    if test:
        today830 = now.replace(hour=6, minute=25, second=50, microsecond=0)
    else:
        today830 = now.replace(hour=8, minute=29, second=50, microsecond=0)
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


# make the reservation to all selected sessions
# session_list: session by number in the day
# session_list_str: session by the string of the start time
# target_day: the date of the target booking
# location_link: link to the target facility
def reserve(session_list_str, target_day, location_link):
    # finding the booking button in the table based on a specific session
    def get_book_link(location, target_d, target_session):
        # after covid reopen 2021
        # open reservation, may need to go to 2nd and 3rd page to book evening slots
        # may need to find row specific to badminton in the future

        # // *[ @ id = "classTimetable"] / div[3] / table / tbody / tr[1] / td[1]
        # // *[ @ id = "classTimetable"] / div[3] / table / tbody / tr[2] / td[2]

        # time text
        # // *[ @ id = "classTimetable"] / div[3] / table / tbody / tr[1] / td[2]
        # book button
        # // *[ @ id = "classTimetable"] / div[3] / table / tbody / tr[1] / td[7] / a

        # other pages
        # // *[ @ id = "classTimetable"] / div[4] / div / ul / li[4] / a

        # go to the table of the target date
        driver.get(location)
        try:
            if test:
                # print(links)
                end_date_box = driver.find_element_by_id("EndDate")
                end_date_box.clear()
                end_date_box.send_keys(target_d)
                end_date_box.send_keys(Keys.RETURN)
            start_date_box = driver.find_element_by_id("StartDate")
            start_date_box.clear()
            start_date_box.send_keys(target_d)
            start_date_box.send_keys(Keys.RETURN)
            start_date_box.send_keys(Keys.RETURN)
            # links = driver.find_elements_by_class_name("BookNow")
        except Exception as e:
            print('error in get_book_link')
            print(e)
            return 0

        max_try_link = 5
        counter = 0

        links = driver.find_elements_by_class_name("BookNow")
        # need to use different condition to refresh table. use unavailable
        # keep updating until booking open
        while len(links) == 0:
            # no available booking spots
            # may have bug when booking less than 2 week later

            if debug:
                print("no links to book yet")
                print(datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
                print(driver.find_element_by_class_name("table").text)
            try:
                if test:
                    # print(links)
                    end_date_box = driver.find_element_by_id("EndDate")
                    end_date_box.clear()
                    end_date_box.send_keys(target_d)
                    end_date_box.send_keys(Keys.RETURN)
                start_date_box = driver.find_element_by_id("StartDate")
                start_date_box.clear()
                start_date_box.send_keys(target_d)
                start_date_box.send_keys(Keys.RETURN)
                start_date_box.send_keys(Keys.RETURN)
                links = driver.find_elements_by_class_name("BookNow")
            except Exception as e:
                print('error in get_book_link')
                print(e)
                return 0
            counter += 1
            if counter > max_try_link:
                return 0

        # while linkFound == 0:
        session_found = 0
        page = 1

        while not session_found:
            if debug:
                # print(session_list)
                table = driver.find_element_by_class_name("table")
                print(table.text)

            table_xpath = "//*[@id='classTimetable']/ div[3] / table /tbody"
            row_xpath = "/tr"
            post_row_path = "]/td["
            post_col_path = "7]/a"

            # get all rows
            xpath = table_xpath + row_xpath
            table_rows = driver.find_elements_by_xpath(xpath)
            i = 0

            for row in table_rows:
                # if debug:
                #     print(row.text)
                #     print(session)
                # found the target session in the table, check for full
                # print('Now' in row.text)
                if target_session in row.text and 'Now' in row.text:
                    xpath2 = table_xpath + row_xpath + '[' + str(i + 1) + post_row_path + post_col_path
                    book_button = driver.find_element_by_xpath(xpath2)
                    # bookButton.send_keys(Keys.RETURN)
                    # session_list.remove(session)
                    return book_button
                i += 1
            page += 1
            # did not find any session that is open for the current target
            # switch to next page
            if page >= 4:
                # session_list.remove(session)
                return 0
            page_col = page + 2
            page_xpath = '// *[ @ id = "classTimetable"] / div[4] / div / ul / li[' + str(page_col) + '] / a'
            page_button = driver.find_element_by_xpath(page_xpath)
            page_button.send_keys(Keys.RETURN)

        return 0

    # assumes booking links already established proceed to click on it with condition permitting
    def book_session(link):
        # assume ready to click on 'book now'

        # if len(link) == 0:
        #     # no available booking spots
        #     if debug:
        #         print("no available booking")
        #     return session_list
        # elif len(link) < min(session_list):
        #     #  available spot become less than the target session
        #     if not cart_is_empty():
        #         if cancel:
        #             cancel_cart()
        #         else:
        #             checkout()
        #     print("did not complete ", session_list)
        #     session_list.clear()
        #     return session_list
        # current_session = session_list.pop()
        try:
            # try to click on aimed session assuming all session available
            if debug:
                print("try to click on specific session")
            link.send_keys(Keys.RETURN)
        except Exception as e:
            # return with original list
            if debug:
                print("specific session becomes unavailable ")
            print(str(e))
            # session_list.insert(0, current_session)
            return 0
        try:
            qty = WebDriverWait(driver, 10).until(
                ex_cond.presence_of_element_located((By.NAME, "PriceGroupQuantities[MEMBER]"))
            )
            # qty.clear()
            qty.send_keys("1")
            qty.send_keys(Keys.RETURN)
        except Exception as e:
            print(str(e))
            print("cant find price quantity to enter")
            time.sleep(5)
            return 0

        # driver.get(location_link)

        # driver.get(location_link)
        return 1

    # used for possible legacy code
    session_list = session_list_str
    orig_list_size = len(session_list)
    fail_list = []
    success_list = []

    attempt = 0
    max_try = 8
    # while there is more sessions to book, make the booking
    while len(session_list) > 0:
        attempt += 1
        if debug:
            print("attempt: ", attempt)
            print(datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
            print("to be booked session list: ", session_list)

        # make a booking for every session in the list
        # start with the last session
        session = session_list.pop()
        # find the book button, and update the session list in regards to the current session
        book_link = get_book_link(location_link, target_day, session)
        if book_link == 0:
            session_list.insert(0, session)
            # checkout or cancel after too many tries
            if attempt > max_try:
                fail_list.append(session_list)
                if debug:
                    print("reached max try")
                    print('failed: ' + str(fail_list))
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
            continue
        # click on the book link
        session_result = book_session(book_link)

        if session_result:
            success_list.append(session)
        else:
            fail_list.append(session)
            print('button press unsuccessful')

        # all sessions processed
        if len(session_list) == 0:
            if cancel:
                cancel_cart()
            else:
                checkout()
            return 1

        # from legacy
        # book_links = get_book_link(location_link, target_day)
        # if book_links == 0:
        #     print("error in reserve with book link")
        #     return 0
        # session_list = book_session(session_list, location_link, book_links)
        # # print(len(session_list), session_list, min(session_list))


def cart_is_empty():
    driver.get("https://movelearnplay.edmonton.ca/COE/public/Basket")
    try:
        driver.find_element_by_xpath("//*[contains(text(),'Your Cart is currently empty')]")
        # element=driver.find_element_by_partial_link_text("Your Cart is currently empty")
    except NoSuchElementException:
        # print("No element found")
        return 0
    return 1


def cancel_cart():
    display_basket()
    cancel_option = 2
    # driver.get("https://movelearnplay.edmonton.ca/COE/public/Basket")
    message = driver.find_element_by_xpath("// html / body / div[6] / div / div / div[2] / div[2] / p")
    if 'empty' in message.text:
        return 0
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
            print(str(e))
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
            if debug:
                print(error_list)
            for rm in reversed(error_list):
                remove_buttons = driver.find_elements_by_class_name("BasketItemRemoveLink")
                try:
                    ActionChains(driver).move_to_element(remove_buttons[rm - 1]).perform()
                except Exception as e:
                    if debug:
                        print(str(e))
                        print("scroll stuff in cancel cart")
                time.sleep(1)
                remove_buttons[rm - 1].click()
        except Exception as e:
            print(str(e))
            return 0
        return 1


def is_error_present():
    try:
        if debug:
            print("in is_error_present")
        WebDriverWait(driver, 30).until(ex_cond.presence_of_element_located((By.CLASS_NAME, "table")))
        return 1
    except Exception as e:
        print(str(e))
        print("except in is_error_present")
        return 0


def handle_cart_error():
    before_xpath_1 = "//*[@class='table']/tbody/tr["
    before_xpath_2 = "/td["
    after_xpath = "]"
    # search_text = "The class is at or exceeding the maximum number of participants"

    try:
        if debug:
            print("in handle error trying to find session error")
        WebDriverWait(driver, 180).until(ex_cond.presence_of_element_located((By.CLASS_NAME, "table")))
        num_rows = len(driver.find_elements_by_xpath("//*[@class='table']/tbody/tr"))
        # num_columns = len(driver.find_elements_by_xpath("//*[@class = 'table']/tbody/tr[2]/td"))

        # elem_found = False

        error_list = []
        for t_row in range(2, (num_rows + 1), 2):
            final_xpath = before_xpath_1 + str(t_row) + after_xpath + \
                          before_xpath_2 + str(1) + after_xpath
            cell_text = driver.find_element_by_xpath(final_xpath).text
            if "Error" in cell_text:
                error_list.append(int(t_row / 2))

        if debug:
            print(error_list)

        for rm in reversed(error_list):
            remove_buttons = driver.find_elements_by_class_name("BasketItemRemoveLink")
            try:
                ActionChains(driver).move_to_element(remove_buttons[rm - 1]).perform()
            except Exception as e:
                print(str(e))
                print("in removing error session place")
            time.sleep(1)
            remove_buttons[rm - 1].click()
    except Exception as e:
        print(str(e))
        print("handle cart wait exception")
        if debug:
            "error handle time out"
        return 0

    # driver.get("https://movelearnplay.edmonton.ca/COE/public/Basket/CheckoutBasket")
    # time.sleep(1)
    return 1


def display_basket():
    driver.get("https://movelearnplay.edmonton.ca/COE/public/Basket")
    print(datetime.now().strftime("display basket: %m/%d/%Y, %H:%M:%S"))
    try:
        print(driver.find_element_by_class_name("table").text)
    except Exception as e:
        print(str(e))
        print("not able to print basket")


def checkout():
    if debug:
        display_basket()
    confirmation = 0

    # ISSUE: after last session added to cart, not automatically jumping to the checkout page.
    # time.sleep(1)
    print(datetime.now().strftime("submit order: %m/%d/%Y, %H:%M:%S"))
    # experimental get a basket link before checkout link
    driver.get("https://movelearnplay.edmonton.ca/COE/public/Basket")
    time.sleep(1)
    driver.get("https://movelearnplay.edmonton.ca/COE/public/Basket/CheckoutBasket")

    if not pre_login:
        try:
            if debug:
                print("finding email to enter")
                print("check if on the correct checkout page")
            WebDriverWait(driver, 2).until(
                ex_cond.presence_of_element_located((By.ID, "EmailAddress"))
            )
        except Exception as e:
            print(str(e))
            print("cant find email to enter, trying to checkout again")
            driver.get("https://movelearnplay.edmonton.ca/COE/public/Basket/CheckoutBasket")
            time.sleep(1)
        login()

    # ISSUE:
    # check for potential submission error after login, need code to automatically resubmit order.
    # need to check for redirection to the cart and remove correct session

    # ISSUE
    # try to find error message
    try:
        if debug:
            print(datetime.now().strftime("submit order: %m/%d/%Y, %H:%M:%S"))
        assert is_error_present() == 1
        handle_cart_error()
    except Exception as e:
        print(str(e))
        print("no error to handle")

    # may or may not get a request to agree to condition
    try:
        element = driver.find_elements_by_css_selector("input[type='radio'][id='AGREE']")[0]
    except Exception as e:
        print(str(e))
        print("after radio")
        # no agree condition, submit order
        while confirmation == 0:
            try:
                if debug:
                    print("waiting for confirmation")
                element = WebDriverWait(driver, 180).until(
                    ex_cond.presence_of_element_located((By.ID, "BasketConfirmed"))
                )
                print(element.text)
                confirmation = 1
            except Exception as e:
                print(str(e))
                if debug:
                    print("did not find basket confirmation")
                time.sleep(60)
        print("end of confirmation")
        return ()

    try:
        ActionChains(driver).move_to_element(element).perform()
    except Exception as e:
        print(str(e))
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
        print(str(e))
        if debug:
            print("need manual assistance")
        time.sleep(180)


def main():
    # create list of sessions to book, the target date of the booking, the link to the target facility
    session_list, session_list_str, target_day, location_link = pre_process()
    cancel_cart()
    # wait until booking opens online
    standby()
    print(datetime.now().strftime("start reserve time: %m/%d/%Y, %H:%M:%S"))
    # make the reservation
    reserve(session_list_str, target_day, location_link)
    print(datetime.now().strftime("end reserve time: %m/%d/%Y, %H:%M:%S"))
    time.sleep(5)
    driver.get("https://movelearnplay.edmonton.ca/COE/members")
    time.sleep(5)
    webdriver.Chrome.close(driver)
    exit()


if __name__ == '__main__':
    main()
