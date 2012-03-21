import calendar
import re
from datetime import date


def get_view_day(request):
    """get day we are currently from session or if no day in session
    give current day
    """

    day = None
    if request is None:
        # There is no request. This may be a test. Return today:
        return date.today()

    if 'date' in request.form:
        # A new date was passed in. Switch date:
        date_str = request.form['date']
        if not date_str or not re.match(r"^\d{4}-\d{2}-\d{2}$", date_str):
            # The string as empty: Return today.
            return date.today()
        year, month, day = date_str.split('-')
        year = int(year)
        month = int(month)
        day = int(day)
        _, days_in_month = calendar.monthrange(year, month)
        if days_in_month < day:
            day = days_in_month
        day = date(year, month, day)
        set_view_day(request, day)
        return day

    if 'chronos_day' in request.SESSION.keys():
        # No new date was passed, in , but a date is set in the session:
        return request.SESSION.get('chronos_day')
    else:
        day = date.today()
        request.SESSION.set('chronos_day', day)
        return day

def set_view_day(request, day):
    """set current day to session"""

    request.SESSION.set('chronos_day', day)

def localTimeFormatFromLocalDateTimeFormat(format):
    """Derive a time-only format from a format string possibly including both time and date tokens.

    Needed because there's no apparent definition of a localized time format string (apart from format strings that mix in date as well) in Plone < 3.2. Algorithm: find each strftime substitution token (like %S) and decide whether it conveys any time information (seconds, minutes, etc.). Keep the time-like tokens, and discard the date-like ones. Also keep any characters between successive time-like tokens. Discard leading and trailing characters.
    """
    # TODO: If we end up butting two tokens up against each other, insert a space between them.

    chunks = format.split('%')[1:]  # Always throw away the first chunk. Whether we keep or discard prefixes and suffixes, we have to do the same for both to support right-to-left and left-to-right languages.
    kill = 'aAbBdjmUwWxyY'  # date-like tokens
    limbo = ''  # chars between tokens
    previousKept = False
    output = []
    for c in chunks:
        try:
            subst = c[0]  # the char following the %
        except IndexError:
            subst = ''
        if subst not in kill:
            if previousKept:
                output.append(limbo)
            output.append('%' + subst)
            try:
                limbo = c[1:]
            except IndexError:
                limbo = ''
            previousKept = True
        else:
            previousKept = False
    return ''.join(output)
