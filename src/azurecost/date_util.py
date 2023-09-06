from datetime import timedelta
from datetime import datetime
from datetime import timezone


class DateUtil:
    @staticmethod
    def get_start_and_end(granularity, point):
        """
        datapointのscaleをmonth, week, dayで自動調節する
        """
        if granularity == "MONTHLY":
            days = 30 * point
        elif granularity == "DAILY":
            days = point

        start_datetime = datetime.now(timezone.utc) - timedelta(days=days)
        if granularity == "MONTHLY":
            start_datetime = start_datetime.replace(day=1)
        return start_datetime, datetime.now(timezone.utc)
