from datetime import datetime, timezone
from azurecost.date_util import DateUtil


class TestDateUtil:
    def test_get_start_and_end_monthly(self):
        start, end = DateUtil.get_start_and_end("MONTHLY", 1)
        assert isinstance(start, datetime)
        assert isinstance(end, datetime)
        assert start.tzinfo == timezone.utc
        assert end.tzinfo == timezone.utc
        assert start.day == 1
        assert start < end

    def test_get_start_and_end_monthly_multiple_months(self):
        start, end = DateUtil.get_start_and_end("MONTHLY", 3)
        assert isinstance(start, datetime)
        assert isinstance(end, datetime)
        assert start.day == 1
        # Should be approximately 90 days ago
        diff = end - start
        assert 85 <= diff.days <= 95

    def test_get_start_and_end_daily(self):
        start, end = DateUtil.get_start_and_end("DAILY", 1)
        assert isinstance(start, datetime)
        assert isinstance(end, datetime)
        assert start.tzinfo == timezone.utc
        assert end.tzinfo == timezone.utc
        # Should be approximately 1 day ago
        diff = end - start
        assert 0 <= diff.days <= 2

    def test_get_start_and_end_daily_multiple_days(self):
        start, end = DateUtil.get_start_and_end("DAILY", 7)
        assert isinstance(start, datetime)
        assert isinstance(end, datetime)
        # Should be approximately 7 days ago
        diff = end - start
        assert 6 <= diff.days <= 8
