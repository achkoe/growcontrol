from datetime import datetime
from oncalendar import BaseIterator

expression = "05:50"
expression = "*:*:01"
it = BaseIterator(expression, datetime.now())
for index in range(5):
    print(next(it))