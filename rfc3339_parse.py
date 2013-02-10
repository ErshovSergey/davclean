import datetime, time, calendar
import re

ZERO = datetime.timedelta(0)

class tzinfo(datetime.tzinfo):
    """
    Implementation of a fixed-offset tzinfo.
    """
    def __init__(self, minutesEast = 0, name = 'Z'):
        """
        minutesEast -> number of minutes east of UTC that this tzinfo represents.
        name -> symbolic (but uninterpreted) name of this tzinfo.
        """
        self.minutesEast = minutesEast
        self.offset = datetime.timedelta(minutes = minutesEast)
        self.name = name

    def utcoffset(self, dt):
        """Returns minutesEast from the constructor, as a datetime.timedelta."""
        return self.offset

    def dst(self, dt):
        """This is a fixed offset tzinfo, so always returns a zero timedelta."""
        return ZERO

    def tzname(self, dt):
        """Returns the name from the constructor."""
        return self.name

    def __repr__(self):
        """If minutesEast==0, prints specially as rfc3339.UTC_TZ."""
        if self.minutesEast == 0:
            return "rfc3339.UTC_TZ"
        else:
            return "rfc3339.tzinfo(%s,%s)" % (self.minutesEast, repr(self.name))

UTC_TZ = tzinfo(0, 'Z')

date_re_str = r'(\d\d\d\d)-(\d\d)-(\d\d)'
time_re_str = r'(\d\d):(\d\d):(\d\d)(\.(\d+))?([zZ]|(([-+])(\d\d):?(\d\d)))'

def make_re(*parts):
    return re.compile(r'^\s*' + ''.join(parts) + r'\s*$')

datetime_re = make_re(date_re_str, r'[ tT]', time_re_str)

def parse_datetime(s):
    m = datetime_re.match(s)
    if m:
        (y, m, d, hour, min, sec, ignore1, frac_sec, wholetz, ignore2, tzsign, tzhour, tzmin) = \
            m.groups()

        if frac_sec:
            frac_sec = float("0." + frac_sec)
        else:
            frac_sec = 0
        microsec = int((frac_sec * 1000000) + 0.5)

        if wholetz == 'z' or wholetz == 'Z':
            tz = UTC_TZ
        else:
            tzhour = int(tzhour)
            tzmin = int(tzmin)
            offset = tzhour * 60 + tzmin
            if offset == 0:
                tz = UTC_TZ
            else:
                if tzhour > 24 or tzmin > 60 or offset > 1439: ## see tzinfo docs for the 1439 part
                    raise ValueError('Invalid timezone offset', s, wholetz)

                if tzsign == '-':
                    offset = -offset
                tz = tzinfo(offset, _offset_to_tzname(offset))

        return datetime.datetime(int(y), int(m), int(d),
                                 int(hour), int(min), int(sec), microsec,
                                 tz)
    else:
        raise ValueError('Invalid RFC 3339 datetime string', s)

