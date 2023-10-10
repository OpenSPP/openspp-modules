from datetime import date, datetime


def datetime_format(inp):
    if not isinstance(inp, datetime) or not isinstance(inp, date):
        return inp
    return inp.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
