from datetime import datetime, timezone, timedelta

from src.cloudevents.events import EventAttributes


class TestEventAttributes:
    def test_init_time(self):
        # Default timestamp
        attrs = EventAttributes()
        assert attrs.time is not None
        assert type(attrs.time) is datetime
        assert attrs.time.tzinfo == timezone.utc
        assert attrs.time < datetime.now(timezone.utc)

        attrs2 = EventAttributes(time="wrong")
        assert attrs2.time is None

        # Timezone-aware
        attrs3 = EventAttributes(time="2025-08-19 13:05:11.892067+02:00")
        assert attrs3.time == datetime(
            2025, 8, 19, 13, 5, 11, 892067, tzinfo=timezone(timedelta(seconds=7200))
        )

        # Timezone-naive
        attrs4 = EventAttributes(time="2025-08-19 13:05:11.892067")
        assert attrs4.time == datetime(2025, 8, 19, 13, 5, 11, 892067)

    def test_get_event_time_as_int(self):
        # Timezone-aware
        attrs = EventAttributes(time="2025-08-19 13:05:11.892067+02:00")
        assert attrs.get_event_time_as_int() == 1755601511892

        # Timezone-naive
        attrs_2 = EventAttributes(time="2025-08-19 13:05:11.892067")
        assert attrs_2.get_event_time_as_int() == 1755605111892

        # Default timestamp
        attrs_3 = EventAttributes()
        assert attrs_3.get_event_time_as_int() > 1755601511892
