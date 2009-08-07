import calendar
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
        if not date_str:
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
