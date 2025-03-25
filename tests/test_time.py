from datetime import datetime, timedelta, timezone

import pytest

from nexosim.time import Duration, MonotonicTime

NANOS_IN_SEC = 1_000_000_000


class TestDuration:
    def test_nanos_too_large_value_error(self):
        with pytest.raises(ValueError):
            Duration(0, NANOS_IN_SEC + 1)

    def test_nanos_negative_value_error(self):
        with pytest.raises(ValueError):
            Duration(0, -1)

    def test_create(self):
        d = Duration.create(
            days=1,
            hours=1,
            minutes=1,
            seconds=1,
            milliseconds=1000,
            microseconds=1_000_000,
            nanoseconds=1_000_000_001,
        )
        assert d == Duration(90064, 1)

    def test_create_nanos(self):
        assert Duration.create(nanoseconds=1_000_000_001) == Duration(1, 1)

    def test_create_micros(self):
        assert Duration.create(microseconds=1_000_001) == Duration(1, 1000)

    def test_create_millis(self):
        assert Duration.create(milliseconds=1001) == Duration(1, 1_000_000)

    def test_from_timedelta(self):
        d = Duration.fromtimedelta(
            timedelta(days=1, hours=1, seconds=1, microseconds=1_000_002)
        )
        assert d == Duration(90002, 2000)

    def test_pos(self):
        assert +Duration(1, 2) == Duration(1, 2)

    def test_neg_only_sec(self):
        assert -Duration(1) == Duration(-1)

    def test_neg_with_nanos(self):
        assert -Duration(1, 10) == Duration(-2, NANOS_IN_SEC - 10)

    def test_iadd(self):
        d = Duration(1, 2)
        d += Duration(3)

        assert d == Duration(4, 2)

    def test_iadd_nanos_more_than_sec(self):
        d = Duration(1, NANOS_IN_SEC - 1)
        d += Duration(3, 3)

        assert d == Duration(5, 2)

    def test_isub(self):
        d = Duration(1, 4)
        d -= Duration(3, 3)

        assert d == Duration(-2, 1)

    def test_isub_neg_nanos(self):
        d = Duration(1, 4)
        d -= Duration(3, 5)

        assert d == Duration(-3, NANOS_IN_SEC - 1)

    def test_imul_int(self):
        d = Duration(1, NANOS_IN_SEC - 1)
        d *= 2

        assert d == Duration(3, NANOS_IN_SEC - 2)

    def test_imul_float(self):
        d = Duration(1, NANOS_IN_SEC - 1)
        d *= 2.0

        assert d == Duration(3, NANOS_IN_SEC - 2)

    def test_itruediv_int(self):
        d = Duration(3, NANOS_IN_SEC - 2)
        d /= 2

        assert d == Duration(1, NANOS_IN_SEC - 1)

    def test_itruediv_float(self):
        d = Duration(3, NANOS_IN_SEC - 2)
        d /= 2.0

        assert d == Duration(1, NANOS_IN_SEC - 1)

    def test_add_duration(self):
        assert Duration(1, 2) + Duration(3) == Duration(4, 2)

    def test_add_monotonic_time(self):
        assert Duration(1, 2) + MonotonicTime(3) == MonotonicTime(4, 2)

    def test_add_int(self):
        with pytest.raises(TypeError):
            _ = Duration(1, 2) + 3

    def test_sub(self):
        assert Duration(1, 4) - Duration(3, 6) == Duration(-3, NANOS_IN_SEC - 2)

    def test_sub_monotonic_time(self):
        with pytest.raises(TypeError):
            _ = Duration(2, 2) - MonotonicTime(1, 1)

    def test_sub_int(self):
        with pytest.raises(TypeError):
            _ = Duration(2, 2) - 1

    def test_mul_int(self):
        assert Duration(1, NANOS_IN_SEC - 1) * 2 == Duration(3, NANOS_IN_SEC - 2)

    def test_mul_float(self):
        assert Duration(1, NANOS_IN_SEC - 1) * 2.0 == Duration(3, NANOS_IN_SEC - 2)

    def test_mul_duration(self):
        with pytest.raises(TypeError):
            _ = Duration(1) * Duration(3, 2)

    def test_truediv_int(self):
        assert Duration(3, NANOS_IN_SEC - 2) / 2 == Duration(1, NANOS_IN_SEC - 1)

    def test_truediv_float(self):
        assert Duration(3, NANOS_IN_SEC - 2) / 2.0 == Duration(1, NANOS_IN_SEC - 1)

    def test_truediv_duration(self):
        with pytest.raises(TypeError):
            _ = Duration(3, NANOS_IN_SEC - 2) / Duration(1)

    def test_format_zero_precision(self):
        assert f"{Duration(1, 2):.0}" == "0:00:01"

    def test_format_non_zero_precision(self):
        assert f"{Duration(1, 2):.3}" == "0:00:01.000"

    def test_format_precision_not_spec_zero_nanos(self):
        assert f"{Duration(1)}" == "0:00:01"

    def test_format_precision_not_spec_non_zero_nanos(self):
        assert f"{Duration(1, NANOS_IN_SEC - 1_000_000)}" == "0:00:01.999"


class TestMonotonicTime:
    def test_nanos_too_large_value_error(self):
        with pytest.raises(ValueError):
            MonotonicTime(0, NANOS_IN_SEC + 1)

    def test_create_hour_too_large_value_error(self):
        with pytest.raises(ValueError):
            MonotonicTime.create(hour=24)

    def test_create_hour_negative_value_error(self):
        with pytest.raises(ValueError):
            MonotonicTime.create(hour=-1)

    def test_create_minute_too_large_value_error(self):
        with pytest.raises(ValueError):
            MonotonicTime.create(minute=60)

    def test_create_minute_negative_value_error(self):
        with pytest.raises(ValueError):
            MonotonicTime.create(minute=-1)

    def test_create_second_too_large_value_error(self):
        with pytest.raises(ValueError):
            MonotonicTime.create(second=60)

    def test_create_second_negative_value_error(self):
        with pytest.raises(ValueError):
            MonotonicTime.create(second=-1)

    def test_create_nanosecond_too_large_value_error(self):
        with pytest.raises(ValueError):
            MonotonicTime.create(nanosecond=NANOS_IN_SEC)

    def test_create_nanosecond_negative_value_error(self):
        with pytest.raises(ValueError):
            MonotonicTime.create(nanosecond=-1)

    def test_create(self):
        t = MonotonicTime.create(hour=1, minute=1, second=1, nanosecond=1)
        assert t == MonotonicTime(3661, 1)

    def test_from_datetime(self):
        t = MonotonicTime.fromdatetime(
            datetime(
                year=1970, month=1, day=2, hour=1, minute=1, second=1, microsecond=1
            )
        )
        assert t == MonotonicTime(90061, 1000)

    def test_from_datetime_with_timezone(self):
        dt = datetime(
            year=1970,
            month=1,
            day=2,
            hour=1,
            minute=1,
            second=1,
            microsecond=1,
            tzinfo=timezone(-timedelta(hours=1)),
        )

        assert MonotonicTime.fromdatetime(dt) == MonotonicTime(93661, 1000)

    def test_iadd(self):
        t = MonotonicTime(1, 1)
        t += Duration(1, 1)

        assert t == MonotonicTime(2, 2)

    def test_iadd_carry_over(self):
        t = MonotonicTime(1, NANOS_IN_SEC - 1)
        t += Duration(1, 1)

        assert t == MonotonicTime(3)

    def test_isub(self):
        t = MonotonicTime(2, 2)
        t -= Duration(1, 1)

        assert t == MonotonicTime(1, 1)

    def test_isub_carry_over(self):
        t = MonotonicTime(3)
        t -= Duration(1, 1)

        assert t == MonotonicTime(1, NANOS_IN_SEC - 1)

    def test_add(self):
        assert MonotonicTime(1, 1) + Duration(1, 1) == MonotonicTime(2, 2)

    def test_add_not_implemented(self):
        with pytest.raises(TypeError):
            _ = MonotonicTime(1, 0) + 1

    def test_sub_duration(self):
        assert MonotonicTime(2, 2) - Duration(1, 1) == MonotonicTime(1, 1)

    def test_sub_monotonic_time(self):
        assert MonotonicTime(2, 2) - MonotonicTime(1, 1) == Duration(1, 1)

    def test_sub_monotonic_time_carry_over(self):
        assert MonotonicTime(2, 2) - MonotonicTime(0, 3) == Duration(
            1, NANOS_IN_SEC - 1
        )

    def test_sub_not_implemented(self):
        with pytest.raises(TypeError):
            _ = MonotonicTime(1, 0) - 1

    def test_format_zero_precision(self):
        assert f"{MonotonicTime(1, 2):.0}" == "1970-01-01 00:00:01"

    def test_format_non_zero_precision(self):
        assert f"{MonotonicTime(1, 2):.3}" == "1970-01-01 00:00:01.000"

    def test_format_precision_not_spec_zero_nanos(self):
        assert f"{MonotonicTime(1)}" == "1970-01-01 00:00:01"

    def test_format_precision_not_spec_non_zero_nanos(self):
        assert (
            f"{MonotonicTime(1, NANOS_IN_SEC - 1_000_000)}" == "1970-01-01 00:00:01.999"
        )
