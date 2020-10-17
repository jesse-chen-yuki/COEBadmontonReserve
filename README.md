# COEBadmintonReserve
badminton reservation program for city of edmonton website

# Assumptions
only book available courts, booking list only targeting book now items in the table
booking consecutive available sessions.


# TODO
 add logging feature
 add unit testing stuff
 log the output for analysis
 branch, adding other rec centers
 change in strategy: book 2 only, wait for 20 min for second round manual

add choice of facilities (TCRC, Commonwealth, Meadows) to make reservations
add logging feature

Edit and TODO History

2020-10-12

# examine booking issue conditions each time to check for resubmission. -- Done need testing
# need to resolve incomplete order after submission -- Done need testing
# look for error as the cart becomes unavailable and cancel the unavailable item -- Done need testing


2020-10-06
examine booking issue conditions each time to check for resubmission.-- done. need test
waited too long, too many attempts after list not able to complete -- done, need more test
set up if statement when available session less than minimum of session requested -- done, need more test


2020-09-28
early login before start time -- REJECT due to slower process
find book element into wait for element to exist. -- REJECT due to logical order
change book_one_session to have precise session booking instead of iteration. -- DONE
implement list of session to be booked in priority order or reverse order -- DONE by list pop

