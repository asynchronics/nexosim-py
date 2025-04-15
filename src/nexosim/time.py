"""Time-related types.

This module defines a custom duration type and timestamp. While superficially
similar to the standard Python `timedelta` and `datetime` types, they do differ
from the latter in a number of ways.

Unlike the standard `datetime` type,
[`MonotonicTime`][nexosim.time.MonotonicTime] is a monotonic timestamp that
specifies a [TAI](https://en.wikipedia.org/wiki/International_Atomic_Time) point
in time. It is represented as a signed number of seconds and a positive number
of nanoseconds, relative to 1970-01-01 00:00:00 TAI.

Note that for most simulation models, the absolute time reference is irrelevant.
If no model makes use of absolute time, the difference between UTC and TAI can
be ignored and the simulation bench can be initialized with an arbitrary
timestamp.

[`Duration`][nexosim.time.Duration] and
[`MonotonicTime`][nexosim.time.MonotonicTime] objects can be directly
deserialized/serialized from/to their counterparts from the Rust world. It must
be noted, however, that unlike Rust's `std::time::Duration` type,
[`Duration`][nexosim.time.Duration] also supports negative durations.

Mixed addition and subtraction involving `Duration` and `MonotonicTime` types
are supported. The `Duration` type also supports multiplication and division by
a scalar.


!!! example "Example usage"
    Basic usage:

    ```py
    from nexosim.time import MonotonicTime

    # A timestamp dated 2009-02-13 23:31:30.987654321 TAI.
    t0 = MonotonicTime(1_234_567_890, 987_654_321)

    # The current TAI time.
    t1 = MonotonicTime.now(leap_secs=37)

    print(f"current TAI time: {t1}")
    print(f"t1 - t0 = {t1 - t0}") # t1 - t0 is a `Duration`
    ```

    Construction from time components and formatting:

    ```py
    from nexosim.time import Duration, MonotonicTime

    # Set the time to 2222-11-11 12:34:56.789 TAI.
    t = MonotonicTime.create(2222, 11, 11, 12, 34, 56, 789000000)

    # Shift it back by 10 days and forth by 1ms.
    shift = Duration.create(days=-10, milliseconds=1)
    t += shift

    print(t)         # prints '2222-11-01 12:34:56.79'
    print(f"{t:.0}") # prints '2222-11-01 12:34:56'
    print(f"{t:.6}") # prints '2222-11-01 12:34:56.790000'
    ```

    Construction from Python `datetime` and `timedelta` objects:

    ```py
    from datetime import datetime, timedelta
    from nexosim.time import Duration, MonotonicTime

    # Set a naive date-time to 1987-06-05 04:32:10.123456.
    dt = datetime(1987, 6, 5, 4, 32, 10, 123456)

    # Interpret it as a TAI timestamp.
    t = MonotonicTime.fromdatetime(dt)

    print(t) # prints "1987-06-05 04:32:10.123456".

    # Create a `Duration` from a `timedelta`.
    delta = timedelta(hours=52, milliseconds=11)
    duration = Duration.fromtimedelta(delta)

    print(duration) # prints '2 days, 4:00:00.011'
    ```
"""

from __future__ import annotations

import copy
import datetime
import time
import types
import typing

import attrs
from typing_extensions import Self as _Self

_T = typing.TypeVar("_T")

_NANOS_IN_SEC: int = 1_000_000_000


def _assert_isnanos(
    instance: typing.Any, attribute: attrs.Attribute[int], value: int
) -> typing.Any:
    if value >= _NANOS_IN_SEC or value < 0:
        raise ValueError(
            "the nanosecond field must be within the range [0, 999'999'999]"
        )


def _assert_istime(hour: int, minute: int, second: int, nanosecond: int) -> None:
    if not 0 <= hour < 24:
        raise ValueError(f"hour must be in 0..23, got '{hour}'")
    if not 0 <= minute < 60:
        raise ValueError(f"minute must be in 0..59, got '{minute}'")
    if not 0 <= second < 60:
        raise ValueError(f"second must be in 0..59, got '{second}'")
    if not 0 <= nanosecond < _NANOS_IN_SEC:
        raise ValueError(f"nanosecond must be in 0..999999999, got '{nanosecond}'")


@attrs.define(order=True)
class Duration:
    """A nanosecond-precision signed duration.

    Attributes:
        secs: The largest second boundary that isn't greater than the
            duration. Always strictly negative for strictly negative durations.

        nanos: The positive sub-second number of nanoseconds to be added to the
            number of seconds specified by `secs` to obtain the duration.
    """

    secs: int = attrs.field(validator=attrs.validators.instance_of(int), default=0)
    nanos: int = attrs.field(
        validator=[attrs.validators.instance_of(int), _assert_isnanos],
        default=0,
    )

    @classmethod
    def create(
        cls,
        days: int = 0,
        hours: int = 0,
        minutes: int = 0,
        seconds: int = 0,
        milliseconds: int = 0,
        microseconds: int = 0,
        nanoseconds: int = 0,
    ) -> _Self:
        """Creates a duration using one or several time units.

        This is a convenience constructor which sums all parameters and
        normalizes the duration to a signed number of seconds and a positive
        number of nanoseconds.

        All parameters are allowed to be negative and may have arbitrary
        magnitudes.

        Args:
            days: A number of days.

            hours: A number of hours.

            minutes: A number of minutes.

            seconds: A number of seconds.

            milliseconds: A number of milliseconds.

            microseconds: A number of microseconds.

            nanoseconds: A number of nanoseconds.
        """
        nanos = nanoseconds + 1_000 * microseconds + 1_000_000 * milliseconds

        carry_secs = nanos // _NANOS_IN_SEC
        secs = seconds + minutes * 60 + hours * 3_600 + days * 86_400

        return cls(secs=secs + carry_secs, nanos=nanos - carry_secs * _NANOS_IN_SEC)

    @classmethod
    def fromtimedelta(cls, dt: datetime.timedelta) -> _Self:
        """Creates a duration from a `datetime.timedelta` object

        Args:
            dt: A time interval.
        """
        nanos = dt.microseconds * 1000

        return cls.create(days=dt.days, seconds=dt.seconds, nanoseconds=nanos)

    def __pos__(self) -> _Self:
        return self

    def __neg__(self) -> _Self:
        if self.nanos == 0:
            self.secs = -self.secs
        else:
            self.secs = -1 - self.secs
            self.nanos = _NANOS_IN_SEC - self.nanos

        return self

    @typing.overload
    def __iadd__(self, other: Duration) -> _Self: ...

    @typing.overload
    def __iadd__(self, other: typing.Any) -> types.NotImplementedType | _Self: ...

    def __iadd__(self, other: typing.Any) -> types.NotImplementedType | _Self:
        if not isinstance(other, Duration):
            return NotImplemented

        nanos = self.nanos + other.nanos

        if nanos < _NANOS_IN_SEC:
            self.secs += other.secs
            self.nanos = nanos
        else:
            self.secs += other.secs + 1
            self.nanos = nanos - _NANOS_IN_SEC

        return self

    @typing.overload
    def __isub__(self, other: Duration) -> _Self: ...

    @typing.overload
    def __isub__(self, other: typing.Any) -> types.NotImplementedType | _Self: ...

    def __isub__(self, other: typing.Any) -> types.NotImplementedType | _Self:
        if not isinstance(other, Duration):
            return NotImplemented

        nanos = self.nanos - other.nanos

        if nanos >= 0:
            self.secs -= other.secs
            self.nanos = nanos
        else:
            self.secs -= other.secs + 1
            self.nanos = nanos + _NANOS_IN_SEC

        return self

    @typing.overload
    def __imul__(self, other: int | float) -> _Self: ...

    @typing.overload
    def __imul__(self, other: typing.Any) -> types.NotImplementedType | _Self: ...

    def __imul__(self, other: typing.Any) -> types.NotImplementedType | _Self:
        if not isinstance(other, (int, float)):
            return NotImplemented

        ns = int((self.secs * _NANOS_IN_SEC + self.nanos) * other)
        self.secs = ns // _NANOS_IN_SEC
        self.nanos = ns - self.secs * _NANOS_IN_SEC

        return self

    @typing.overload
    def __itruediv__(self, other: int | float) -> _Self: ...

    @typing.overload
    def __itruediv__(self, other: typing.Any) -> types.NotImplementedType | _Self: ...

    def __itruediv__(self, other: typing.Any) -> types.NotImplementedType | _Self:
        if not isinstance(other, (int, float)):
            return NotImplemented

        ns = int((self.secs * _NANOS_IN_SEC + self.nanos) / other)
        self.secs = ns // _NANOS_IN_SEC
        self.nanos = ns - self.secs * _NANOS_IN_SEC

        return self

    @typing.overload
    def __add__(self, other: Duration) -> _Self: ...

    @typing.overload
    def __add__(self, other: MonotonicTime) -> MonotonicTime: ...

    @typing.overload
    def __add__(
        self, other: typing.Any
    ) -> types.NotImplementedType | MonotonicTime | _Self: ...

    def __add__(
        self, other: typing.Any
    ) -> types.NotImplementedType | MonotonicTime | _Self:
        if isinstance(other, MonotonicTime):
            return other + self

        if not isinstance(other, Duration):
            return NotImplemented

        tmp = copy.deepcopy(self)
        tmp += other

        return tmp

    @typing.overload
    def __sub__(self, other: Duration) -> _Self: ...

    @typing.overload
    def __sub__(self, other: typing.Any) -> types.NotImplementedType | _Self: ...

    def __sub__(self, other: typing.Any) -> types.NotImplementedType | _Self:
        if not isinstance(other, Duration):
            return NotImplemented

        tmp = copy.deepcopy(self)
        tmp -= other

        return tmp

    @typing.overload
    def __mul__(self, other: int | float) -> _Self: ...

    @typing.overload
    def __mul__(self, other: typing.Any) -> types.NotImplementedType | _Self: ...

    def __mul__(self, other: typing.Any) -> types.NotImplementedType | _Self:
        if not isinstance(other, (int, float)):
            return NotImplemented

        tmp = copy.deepcopy(self)
        tmp *= other

        return tmp

    @typing.overload
    def __rmul__(self, other: int) -> _Self: ...

    @typing.overload
    def __rmul__(self, other: typing.Any) -> types.NotImplementedType | _Self: ...

    def __rmul__(self, other: typing.Any) -> types.NotImplementedType | _Self:
        return self * other

    @typing.overload
    def __truediv__(self, other: int | float) -> _Self: ...

    @typing.overload
    def __truediv__(self, other: typing.Any) -> types.NotImplementedType | _Self: ...

    def __truediv__(self, other: typing.Any) -> types.NotImplementedType | _Self:
        if not isinstance(other, (int, float)):
            return NotImplemented

        tmp = copy.deepcopy(self)
        tmp /= other

        return tmp

    def __format__(self, format_spec: str) -> str:
        if format_spec.startswith("."):
            precision = int(format_spec[1:])

            if precision == 0:
                frac = ""
            else:
                nanos = "{:0>9}".format(self.nanos)
                frac = "." + nanos[0:precision]
        else:
            if self.nanos == 0:
                frac = ""
            else:
                nanos = "{:0>9}".format(self.nanos)
                frac = "." + nanos.rstrip("0")

        delta_secs = datetime.timedelta(seconds=self.secs)

        return str(delta_secs) + frac

    def __str__(self) -> str:
        return "{}".format(self)


@attrs.define(order=True)
class MonotonicTime:
    """A nanosecond-precision monotonic clock timestamp.

    A timestamp specifies a
    [TAI](https://en.wikipedia.org/wiki/International_Atomic_Time) point in
    time. It is represented as a signed number of seconds and a positive number
    of nanoseconds, counted with reference to 1970-01-01 00:00:00 TAI.

    Attributes:
        secs: The number of whole seconds in the future (if positive) or in the past
            (if negative) of 1970-01-01 00:00:00 TAI.
        nanos: The sub-second number of nanoseconds in the future of the point
            in time defined by `secs`.
    """

    secs: int = attrs.field(validator=attrs.validators.instance_of(int), default=0)
    nanos: int = attrs.field(
        validator=[attrs.validators.instance_of(int), _assert_isnanos],
        default=0,
    )

    @classmethod
    def create(
        cls,
        year: int = 1970,
        month: int = 1,
        day: int = 1,
        hour: int = 0,
        minute: int = 0,
        second: int = 0,
        nanosecond: int = 0,
        leap_secs: int = 0,
    ) -> _Self:
        """Creates a timestamp from a date-time representation.

        The first argument is the proleptic Gregorian year, which must be at
        least equal to 1. The month and day follow the usual calendar convention
        and start at 1.

        If the date is provided as UTC rather than TAI, the number of leap
        seconds can be specified to allow conversion to TAI. For reference, this
        offset has been +37s since 2017-01-01, a value which is to remain valid
        until at least 2024-12-28. See the [official IERS bulletin
        C](http://hpiers.obspm.fr/iers/bul/bulc/bulletinc.dat) for leap second
        announcements or the [IERS
        table](https://hpiers.obspm.fr/iers/bul/bulc/Leap_Second.dat) for
        current and historical values.

        Args:
            year: The year (1 ≤ `year` ≤ 9999).

            month: The month (1 ≤ `month` ≤ 12).

            day: The day of the month (1 ≤ `day` ≤ 28/29/30/31).

            hour: The hour (0 ≤ `hour` < 24).

            minute: The minute (0 ≤ `minute` < 60).

            second: The second (0 ≤ `second` < 60).

            nanosecond: The nanosecond (0 ≤ `nanosecond` < 1'000'000'000).

            leap_secs: Difference between TAI and UTC time in seconds applicable
                at the date represented by the timestamp.

        Raises:
            ValueError: An exception is thrown if one or several parameters are
                invalid or not supported.
        """

        date = datetime.date(year, month, day)
        # number of days since 1970-01-01 00:00:00 TAI
        days = date.toordinal() - 719163
        _assert_istime(hour, minute, second, nanosecond)
        secs = second + leap_secs + minute * 60 + hour * 3600 + days * 86400

        return cls(secs=secs, nanos=nanosecond)

    @classmethod
    def fromdatetime(cls, dt: datetime.datetime, leap_secs: int = 0) -> _Self:
        """Creates a timestamp from a Python `datetime` object.

        If the date-time is provided as UTC-based, timezone-aware object rather
        than a naive TAI date-time, the number of leap seconds can be specified
        to allow conversion to TAI. For reference, this offset has been +37s
        since 2017-01-01, a value which is to remain valid until at least
        2024-12-28. See the [official IERS bulletin
        C](http://hpiers.obspm.fr/iers/bul/bulc/bulletinc.dat) for leap second
        announcements or the [IERS
        table](https://hpiers.obspm.fr/iers/bul/bulc/Leap_Second.dat) for
        current and historical values.

        Args:
            dt: A date-time object, which may be specified as a TAI naive
                date-time (`tzinfo=None`) or as a timezone-aware date-time.

            leap_secs: Difference between TAI and UTC time in seconds applicable
                at the date represented by the timestamp.
        """

        if dt.tzinfo is not None:
            dt = dt.astimezone(datetime.timezone.utc)

        timestamp = cls.create(
            year=dt.year,
            month=dt.month,
            day=dt.day,
            hour=dt.hour,
            minute=dt.minute,
            second=dt.second,
            nanosecond=dt.microsecond * 1000,
        )
        timestamp.secs += leap_secs

        return timestamp

    @classmethod
    def now(cls, leap_secs: int = 0) -> _Self:
        """Creates a timestamp corresponding to the current time.

        Note that this method uses the system clock, which is based on UTC. The
        number of leap seconds can be specified to allow conversion to TAI. For
        reference, this offset has been +37s since 2017-01-01, a value which is
        to remain valid until at least 2024-12-28. See the [official IERS
        bulletin C](http://hpiers.obspm.fr/iers/bul/bulc/bulletinc.dat) for leap
        second announcements or the [IERS
        table](https://hpiers.obspm.fr/iers/bul/bulc/Leap_Second.dat) for
        current and historical values.

        Args:
            leap_secs: Difference between TAI and UTC time in seconds applicable
                at the date represented by the timestamp.
        """

        utc_ns = time.time_ns()
        utc_secs = utc_ns // _NANOS_IN_SEC
        utc_nanos = utc_ns - utc_secs * _NANOS_IN_SEC

        return cls(secs=utc_secs + leap_secs, nanos=utc_nanos)

    @typing.overload
    def __iadd__(self, other: Duration) -> _Self: ...

    @typing.overload
    def __iadd__(self, other: typing.Any) -> types.NotImplementedType | _Self: ...

    def __iadd__(self, other: typing.Any) -> types.NotImplementedType | _Self:
        if not isinstance(other, Duration):
            return NotImplemented

        nanos = self.nanos + other.nanos

        if nanos < _NANOS_IN_SEC:
            self.secs += other.secs
            self.nanos = nanos
        else:
            self.secs += other.secs + 1
            self.nanos = nanos - _NANOS_IN_SEC

        return self

    @typing.overload
    def __isub__(self, other: Duration) -> _Self: ...

    @typing.overload
    def __isub__(self, other: typing.Any) -> types.NotImplementedType | _Self: ...

    def __isub__(self, other: typing.Any) -> types.NotImplementedType | _Self:
        if not isinstance(other, Duration):
            return NotImplemented

        nanos = self.nanos - other.nanos

        if nanos >= 0:
            self.secs -= other.secs
            self.nanos = nanos
        else:
            self.secs -= other.secs + 1
            self.nanos = nanos + _NANOS_IN_SEC

        return self

    @typing.overload
    def __add__(self, other: Duration) -> _Self: ...

    @typing.overload
    def __add__(self, other: typing.Any) -> types.NotImplementedType | _Self: ...

    def __add__(self, other: typing.Any) -> types.NotImplementedType | _Self:
        if not isinstance(other, Duration):
            return NotImplemented

        tmp = copy.deepcopy(self)
        tmp += other

        return tmp

    @typing.overload
    def __sub__(self, other: Duration) -> _Self: ...

    @typing.overload
    def __sub__(self, other: MonotonicTime) -> Duration: ...

    @typing.overload
    def __sub__(
        self, other: typing.Any
    ) -> types.NotImplementedType | Duration | _Self: ...

    def __sub__(self, other: typing.Any) -> types.NotImplementedType | Duration | _Self:
        if isinstance(other, MonotonicTime):
            secs = self.secs - other.secs
            nanos = self.nanos - other.nanos

            if nanos < 0:
                nanos = nanos + _NANOS_IN_SEC
                secs -= 1

            return Duration(secs, nanos)

        if not isinstance(other, Duration):
            return NotImplemented

        tmp = copy.deepcopy(self)
        tmp -= other

        return tmp

    def __format__(self, format_spec: str) -> str:
        if format_spec.startswith("."):
            precision = int(format_spec[1:])

            if precision == 0:
                frac = ""
            else:
                nanos = "{:0>9}".format(self.nanos)
                frac = "." + nanos[0:precision]
        else:
            if self.nanos == 0:
                frac = ""
            else:
                nanos = "{:0>9}".format(self.nanos)
                frac = "." + nanos.rstrip("0")

        dt = (
            datetime.datetime.fromtimestamp(float(self.secs))
            .astimezone(datetime.UTC)
            .replace(tzinfo=None)
        )

        return str(dt) + frac

    def __str__(self) -> str:
        return "{}".format(self)
