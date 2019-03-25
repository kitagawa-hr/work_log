import unittest
from datetime import datetime

import work_log


class TestWorklog(unittest.TestCase):
    def test_last_day_of_month(self):
        test_cases = [(2019, 1, 31), (2019, 3, 31), (2019, 2, 28), (2020, 2, 29)]
        for year, month, day in test_cases:
            with self.subTest(year=year, month=month, day=day):
                self.assertEqual(work_log.last_day_of_month(year, month), day)

    def test_take_if_exists(self):
        test_cases = [
            ([1, 2, 3], 0, 1),
            ([1, 2, 3], 1, 2),
            ([1, 2, 3], -1, 3),
            ([], 1, None),
            ([1, 2, 3], 10, None),
            ([], 0, None),
            ([1, 3, 5], 4, None),
        ]
        for lis, index, element in test_cases:
            with self.subTest(lis=lis, index=index, element=element):
                self.assertEqual(work_log.take_if_exists(lis, index), element)

    def test_minmax_datetime(self):
        test_cases = [
            (min, [datetime(2019, 1, 1), datetime(2019, 1, 1)], datetime(2019, 1, 1)),
            (max, [datetime(2019, 1, 1), datetime(2019, 1, 1)], datetime(2019, 1, 1)),
            (min, [datetime(2019, 1, 1), datetime(2019, 1, 31)], datetime(2019, 1, 1)),
            (max, [datetime(2019, 1, 1), datetime(2019, 1, 31)], datetime(2019, 1, 31)),
            (
                min,
                [datetime(2019, 1, 1), datetime(2019, 1, 1), datetime(2018, 12, 12)],
                datetime(2018, 12, 12),
            ),
            (max, [datetime(2019, 1, 1), None], datetime(2019, 1, 1)),
            (max, [None, None], None),
            (max, [], None),
        ]
        for min_or_max, dates, date in test_cases:
            with self.subTest(min_or_max=min_or_max, dates=dates, date=date):
                self.assertEqual(work_log.minmax_datetime(min_or_max, *dates), date)

    def test_format_datetime(self):
        test_cases = [
            (datetime(2019, 10, 10, 12, 24), "12:20"),
            (datetime(2019, 10, 10, 1, 22), "1:20"),
            (datetime(2019, 10, 10, 3, 27), "3:30"),
            (datetime(2019, 10, 10, 0, 29), "0:30"),
            (None, None),
        ]
        for dt, formatted_dt in test_cases:
            with self.subTest(dt=dt, formatted_dt=formatted_dt):
                self.assertEqual(work_log.format_datetime(dt), formatted_dt)
