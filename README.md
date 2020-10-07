# COEBadmontonReserve
badminton reservation program for city of edmonton website

# Assumptions
only book available courts, booking list only targeting book now items in the table
booking consecutive available sessions.


# TODO

add unit testing stuff
need to resolve uncomplete order after submission
look for error as the cart becomes unavailable and cancel the unavailable item
resolve access to checkout too soon before complete session

add choice of facilities (TCRC, Commonwealth, Meadows) to make reservations
add logging feature

Edit and TODO History

2020-10-06
examine booking issue conditions each time to check for resubmission.-- done. need test
waited too long, too many attempts after list not fulfillables -- done, need more test
set up if statement when available session less than minimum of session requested -- done, need more test


2020-09-28
early login before start time -- REJECT due to slower process
find book element into wait for element to exist. -- REJECT due to logical order
change bookonesession to have precise session booking instead of iteration. -- DONE
implement list of session to be booked in priority order or reverse order -- DONE by list pop

