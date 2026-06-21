from __future__ import annotations

import importlib.util
from datetime import date, timedelta


if importlib.util.find_spec("workalendar") is not None and importlib.util.find_spec("workalendar.europe") is not None:
    from workalendar.europe import Hungary as HungaryCalendar
else:

    class HungaryCalendar:
        """Small development fallback used only when workalendar is unavailable."""

        def is_working_day(self, day: date) -> bool:
            return day.weekday() < 5 and day not in self._fixed_holidays(day.year)

        def _fixed_holidays(self, year: int) -> set[date]:
            easter = self._easter_sunday(year)
            return {
                date(year, 1, 1),
                date(year, 3, 15),
                easter - timedelta(days=2),
                easter + timedelta(days=1),
                date(year, 5, 1),
                date(year, 8, 20),
                date(year, 10, 23),
                date(year, 11, 1),
                date(year, 12, 25),
                date(year, 12, 26),
            }

        def _easter_sunday(self, year: int) -> date:
            a = year % 19
            b = year // 100
            c = year % 100
            d = b // 4
            e = b % 4
            f = (b + 8) // 25
            g = (b - f + 1) // 3
            h = (19 * a + b - d - g + 15) % 30
            i = c // 4
            k = c % 4
            l = (32 + 2 * e + 2 * i - h - k) % 7
            m = (a + 11 * h + 22 * l) // 451
            month = (h + l - 7 * m + 114) // 31
            day = ((h + l - 7 * m + 114) % 31) + 1
            return date(year, month, day)
