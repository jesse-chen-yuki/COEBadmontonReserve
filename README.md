# COEBadmintonReserve
badminton reservation program for city of edmonton website during COVID restriction period
Not required to use as of July 2021

# Assumptions
only book available courts, booking list only targeting book now items in the table
booking consecutive available sessions.

# Requirement 
Selenium
Chrome

# TODO:
 change to async wait after cart checkout
 add logging feature 
 add unit testing stuff
 log the output for analysis
 branch, adding other rec centers
 change in strategy: book 2 only, wait for 20 min for second round manual

add choice of facilities (TCRC, Commonwealth, Meadows) to make reservations

Edit and TODO History

2021-06-19
complete new booking procedure with row by row examination
need testing

2021-06-08
change booking link after covid
add try/except block for getting start date etc. raise exception when nothing to see

2020-10-19
branch, adding other rec centers -- Done 
standby using timer and only click on submit button instead of reloading webpage -- DONE


2020-10-17
print cart items before submit -- DONE
branch, pre log in before, add sessions -- DONE

2020-10-12

examine booking issue conditions each time to check for resubmission. -- Done need testing
need to resolve incomplete order after submission -- Done need testing
look for error as the cart becomes unavailable and cancel the unavailable item -- Done need testing


2020-10-06
examine booking issue conditions each time to check for resubmission.-- done. need test
waited too long, too many attempts after list not able to complete -- done, need more test
set up if statement when available session less than minimum of session requested -- done, need more test


2020-09-28
early login before start time -- REJECT due to slower process
find book element into wait for element to exist. -- REJECT due to logical order
change book_one_session to have precise session booking instead of iteration. -- DONE
implement list of session to be booked in priority order or reverse order -- DONE by list pop

