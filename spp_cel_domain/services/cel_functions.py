from datetime import date, datetime, timedelta


def today():
    return date.today()


def now():
    return datetime.now()


def days_ago(n: int):
    return date.today() - timedelta(days=int(n))


def years_ago(n: int):
    try:
        n = int(n)
    except Exception:
        n = 0
    today_d = date.today()
    # naive year delta
    try:
        return today_d.replace(year=today_d.year - n)
    except ValueError:
        # Feb 29th case
        return today_d.replace(month=2, day=28, year=today_d.year - n)


def months_ago(n: int):
    n = int(n)
    today_d = date.today()
    y = today_d.year
    m = today_d.month - n
    while m <= 0:
        m += 12
        y -= 1
    d = min(today_d.day, 28)
    return date(y, m, d)


def age_years(d):
    if not d:
        return None
    if isinstance(d, datetime):
        d = d.date()
    if not isinstance(d, date):
        return None
    t = date.today()
    return t.year - d.year - ((t.month, t.day) < (d.month, d.day))


def between(x, a, b):
    return a <= x <= b
