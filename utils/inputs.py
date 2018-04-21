from calendar import timegm
from datetime import datetime, time, timedelta
from email.utils import parsedate_tz, mktime_tz
import re

import aniso8601
import pytz

# for ip validate
import socket
from netaddr import IPNetwork, IPAddress

# Constants for upgrading date-based intervals to full datetimes.
START_OF_DAY = time(0, 0, 0, tzinfo=pytz.UTC)
END_OF_DAY = time(23, 59, 59, 999999, tzinfo=pytz.UTC)

# https://code.djangoproject.com/browser/django/trunk/django/core/validators.py
# basic auth added by frank

url_regex = re.compile(
    r'^(?:http|ftp)s?://'  # http:// or https://
    r'(?:[^:@]+?:[^:@]*?@|)'  # basic auth
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+'
    r'(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
    r'localhost|'  # localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'  # ...or ipv4
    r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'  # ...or ipv6
    r'(?::\d+)?'  # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)

#http://stackoverflow.com/questions/8022530/python-check-for-valid-email-address
email_regex = re.compile(
    r'[^@]+@[^@]+\.[^@]+'
    , re.IGNORECASE)


def url(value):
    """Validate a URL.

    :param string value: The URL to validate
    :returns: The URL if valid.
    :raises: ValueError
    """
    if not url_regex.search(value):
        message = u"{0} is not a valid URL".format(value)
        if url_regex.search('http://' + value):
            message += u". Did you mean: http://{0}".format(value)
        raise ValueError(message)
    return value


class regex(object):
    """Validate a string based on a regular expression.

    Example::

        parser = reqparse.RequestParser()
        parser.add_argument('example', type=inputs.regex('^[0-9]+$'))

    Input to the ``example`` argument will be rejected if it contains anything
    but numbers.

    :param pattern: The regular expression the input must match
    :type pattern: str
    """

    def __init__(self, pattern):
        self.pattern = pattern
        self.re = re.compile(pattern)

    def __call__(self, value):
        if not self.re.search(value):
            message = 'Value does not match pattern: "{}"'.format(self.pattern)
            raise ValueError(message)
        return value


def _normalize_interval(start, end, value):
    """Normalize datetime intervals.

    Given a pair of datetime.date or datetime.datetime objects,
    returns a 2-tuple of tz-aware UTC datetimes spanning the same interval.

    For datetime.date objects, the returned interval starts at 00:00:00.0
    on the first date and ends at 00:00:00.0 on the second.

    Naive datetimes are upgraded to UTC.

    Timezone-aware datetimes are normalized to the UTC tzdata.

    Params:
        - start: A date or datetime
        - end: A date or datetime
    """
    if not isinstance(start, datetime):
        start = datetime.combine(start, START_OF_DAY)
        end = datetime.combine(end, START_OF_DAY)

    if start.tzinfo is None:
        start = pytz.UTC.localize(start)
        end = pytz.UTC.localize(end)
    else:
        start = start.astimezone(pytz.UTC)
        end = end.astimezone(pytz.UTC)

    return start, end


def _expand_datetime(start, value):
    if not isinstance(start, datetime):
        # Expand a single date object to be the interval spanning
        # that entire day.
        end = start + timedelta(days=1)
    else:
        # Expand a datetime based on the finest resolution provided
        # in the original input string.
        time = value.split('T')[1]
        time_without_offset = re.sub('[+-].+', '', time)
        num_separators = time_without_offset.count(':')
        if num_separators == 0:
            # Hour resolution
            end = start + timedelta(hours=1)
        elif num_separators == 1:
            # Minute resolution:
            end = start + timedelta(minutes=1)
        else:
            # Second resolution
            end = start + timedelta(seconds=1)

    return end


def _parse_interval(value):
    """Do some nasty try/except voodoo to get some sort of datetime
    object(s) out of the string.
    """
    try:
        return sorted(aniso8601.parse_interval(value))
    except ValueError:
        try:
            return aniso8601.parse_datetime(value), None
        except ValueError:
            return aniso8601.parse_date(value), None


def iso8601interval(value, argument='argument'):
    """Parses ISO 8601-formatted datetime intervals into tuples of datetimes.

    Accepts both a single date(time) or a full interval using either start/end
    or start/duration notation, with the following behavior:

    - Intervals are defined as inclusive start, exclusive end
    - Single datetimes are translated into the interval spanning the
      largest resolution not specified in the input value, up to the day.
    - The smallest accepted resolution is 1 second.
    - All timezones are accepted as values; returned datetimes are
      localized to UTC. Naive inputs and date inputs will are assumed UTC.

    Examples::

        "2013-01-01" -> datetime(2013, 1, 1), datetime(2013, 1, 2)
        "2013-01-01T12" -> datetime(2013, 1, 1, 12), datetime(2013, 1, 1, 13)
        "2013-01-01/2013-02-28" -> datetime(2013, 1, 1), datetime(2013, 2, 28)
        "2013-01-01/P3D" -> datetime(2013, 1, 1), datetime(2013, 1, 4)
        "2013-01-01T12:00/PT30M" -> datetime(2013, 1, 1, 12), datetime(2013, 1, 1, 12, 30)
        "2013-01-01T06:00/2013-01-01T12:00" -> datetime(2013, 1, 1, 6), datetime(2013, 1, 1, 12)

    :param str value: The ISO8601 date time as a string
    :return: Two UTC datetimes, the start and the end of the specified interval
    :rtype: A tuple (datetime, datetime)
    :raises: ValueError, if the interval is invalid.
    """

    try:
        start, end = _parse_interval(value)

        if end is None:
            end = _expand_datetime(start, value)

        start, end = _normalize_interval(start, end, value)

    except ValueError:
        raise ValueError(
            "Invalid {arg}: {value}. {arg} must be a valid ISO8601 "
            "date/time interval.".format(arg=argument, value=value),
        )

    return start, end


def date(value):
    """Parse a valid looking date in the format YYYY-mm-dd"""
    date = datetime.strptime(value, "%Y-%m-%d")
    if date.year < 1900:
        raise ValueError(u"Year must be >= 1900")
    return date


def _get_integer(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        raise ValueError('{} is not a valid integer'.format(value))


def natural(value, argument='argument'):
    """ Restrict input type to the natural numbers (0, 1, 2, 3...) """
    value = _get_integer(value)
    if value < 0:
        error = ('Invalid {arg}: {value}. {arg} must be a non-negative '
                 'integer'.format(arg=argument, value=value))
        raise ValueError(error)
    return value

def Float(value, argument='argument'):
    if isinstance(value, int) or isinstance(value, float):
        pass
    else:
        error = ('Invalid {arg}: {value}. {arg} must be a '
                'integer or float'.format(arg=argument, value=value))
        raise ValueError(error)
    return value


def positive(value, argument='argument'):
    """ Restrict input type to the positive integers (1, 2, 3...) """
    value = _get_integer(value)
    if value < 1:
        error = ('Invalid {arg}: {value}. {arg} must be a positive '
                 'integer'.format(arg=argument, value=value))
        raise ValueError(error)
    return value


def int_range(low, high, value, argument='argument'):
    """ Restrict input to an integer in a range (inclusive) """
    value = _get_integer(value)
    if value < low or value > high:
        error = ('Invalid {arg}: {val}. {arg} must be within the range {lo} - {hi}'
                 .format(arg=argument, val=value, lo=low, hi=high))
        raise ValueError(error)

    return value


def boolean(value):
    """Parse the string "true" or "false" as a boolean (case insensitive).
    Also accepts "1" and "0" as True/False (respectively). If
    the input is from the request JSON body, the type is already a native
    python boolean, and will be passed through without further parsing."""
    if type(value) == bool:
        return value

    if not value:
        raise ValueError("boolean type must be non-null")
    value = value.lower()
    if value in ('true', '1',):
        return True
    if value in ('false', '0',):
        return False
    raise ValueError("Invalid literal for boolean(): {}".format(value))


def datetime_from_rfc822(datetime_str):
    """Turns an RFC822 formatted date into a datetime object.

    Example::

        inputs.datetime_from_rfc822("Wed, 02 Oct 2002 08:00:00 EST")

    :param datetime_str: The RFC822-complying string to transform
    :type datetime_str: str
    :return: A datetime
    """
    return datetime.fromtimestamp(mktime_tz(parsedate_tz(datetime_str)), pytz.utc)


def datetime_from_iso8601(datetime_str):
    """Turns an ISO8601 formatted date into a datetime object.

    Example::

        inputs.datetime_from_iso8601("2012-01-01T23:30:00+02:00")

    :param datetime_str: The ISO8601-complying string to transform
    :type datetime_str: str
    :return: A datetime
    """
    return aniso8601.parse_datetime(datetime_str)

def email(value):
    """Validate a EMAIL.

    :param string value: The EMAIL to validate
    :returns: The EMAIL if valid.
    :raises: ValueError
    """
    if not email_regex.search(value):
        message = u"{0} is not a valid EMAIL".format(value)
        raise ValueError(message)
    return value

def str_range(low, high, value, argument='argument'):
    """ Restrict input to an str in a range (inclusive) """
    try:
        value = str(value)
    except (TypeError, ValueError):
        raise ValueError('{} is not a valid str'.format(value))

    strlen = value.__len__()
    low = _get_integer(low)
    high = _get_integer(high)
    if strlen < low or high < strlen :
        error = ('Invalid {arg}: {val}. {arg} length must be within the range {lo} - {hi}'
                 .format(arg=argument, val=value, lo=low, hi=high))
        raise ValueError(error)

    return value

def wrap_str_range(value, name, op, argument):
    low, high = argument.split(',')
    return str_range(low, high, value)

def str_in_list(value, name, op, argument):
    if value not in argument:
        message = u"{0} is not in {1} List".format(value, argument)
        raise ValueError(message)
    return value

def int_in_list(value, name, op, argument):
    value = _get_integer(value)
    if value not in argument:
        message = u"{0} is not in {1} List".format(value, argument)
        raise ValueError(message)
    return value

def is_ipv4_ipv6(value, name=None, op=None, argument='IPv4'):
    # now we only support IPv4/IPv6
    if 'IPv4' == argument:
        socket.inet_aton(value)
    else:
        socket.inet_pton(socket.AF_INET6, value)

    #except socket.error as error: if Not legal
    return value

def is_cidr(value, name=None, op=None, argument=None):
    #http://stackoverflow.com/questions/819355/how-can-i-check-if-an-ip-is-in-a-network-in-python
    #IPAddress("192.168.0.1") in IPNetwork("192.168.0.0/24")
    ip = [value, argument]
    if not (IPAddress(value) in IPNetwork('/'.join(ip))):
        message = u"{0} is not valid ".format('/'.join(ip))
        raise ValueError(message)

    return value

def is_netmask(value, name=None, op=None, argument=None):
    if not IPAddress(value).is_netmask():
        message = u"{0} is not valid ".format(value)
        raise ValueError(message)

    return value

def is_ipv6_prefix(value, name=None, op=None, argument=None):
    #IPNetwork('fe80::dead:beef/64')
    ip = [value, argument]
    if not IPNetwork('/'.join(ip)):
        message = u"{0} is not valid ".format('/'.join(ip))
        raise ValueError(message)

    return value
