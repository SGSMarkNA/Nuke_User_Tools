import datetime

date = datetime.date.today()

date.year
date.month
date.day

"%s:%s:%s" % (str(date.year),str(date.month).zfill(2),str(date.day).zfill(2))