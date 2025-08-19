from datetime import datetime, timezone, timedelta

from cloudevents.events import EventAttributes


class TestEventAttributes:
    def test_init_time(self):
        attrs = EventAttributes()
        assert attrs.time is not None
        assert type(attrs.time) is datetime
        assert attrs.time < datetime.now(timezone.utc)

        attrs2 = EventAttributes(time="wrong")
        assert attrs2.time is None

        attrs3 = EventAttributes(time="2025-08-19 13:05:11.892067+02:00")
        assert attrs3.time == datetime(
            2025, 8, 19, 13, 5, 11, 892067, tzinfo=timezone(timedelta(seconds=7200))
        )
