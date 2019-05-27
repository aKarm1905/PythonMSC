"""Ladybug analysis period class."""
from .dt import LBDateTime
from datetime import datetime, timedelta


class AnalysisPeriod(object):
    """Ladybug Analysis Period.

    A continuous analysis period between two days of the year between certain hours

    Attributes:
        stMonth: An integer between 1-12 for starting month (default = 1)
        stDay: An integer between 1-31 for starting day (default = 1).
                Note that some months are shorter than 31 days.
        stHour: An integer between 0-23 for starting hour (default = 0)
        endMonth: An integer between 1-12 for ending month (default = 12)
        endDay: An integer between 1-31 for ending day (default = 31)
                Note that some months are shorter than 31 days.
        endHour: An integer between 0-23 for ending hour (default = 23)
        timestep: An integer number from 1, 2, 3, 4, 5, 6, 10, 12, 15, 20, 30, 60
    """

    __validTimesteps = {1: 60, 2: 30, 3: 20, 4: 15, 5: 12,
                        6: 10, 10: 6, 12: 5, 15: 4, 20: 3, 30: 2, 60: 1}
    __numOfDaysEachMonth = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)

    # TODO: handle timestep between 1-60
    def __init__(self, stMonth=1, stDay=1, stHour=0, endMonth=12,
                 endDay=31, endHour=23, timestep=1):
        """Init an analysis period."""
        # calculate start time and end time
        self.stTime = LBDateTime(int(stMonth), int(stDay), int(stHour))

        if int(endDay) > self.__numOfDaysEachMonth[int(endMonth) - 1]:
            end = self.__numOfDaysEachMonth[endMonth - 1]
            print "Updated endDay from {} to {}".format(endDay, end)
            endDay = end

        self.endTime = LBDateTime(int(endMonth), int(endDay), int(endHour))

        if self.stTime.hour <= self.endTime.hour:
            self.overnight = False  # each segments of hours will be in a single day
        else:
            self.overnight = True

        # A reversed analysis period defines a period that starting month is after ending month
        # (e.g DEC to JUN)
        if self.stTime.HOY > self.endTime.HOY:
            self.reversed = True
        else:
            self.reversed = False

        # check time step
        if timestep not in self.__validTimesteps:
            raise ValueError("Invalid timestep. Valid values are %s" % str(self.__validTimesteps))

        # calculate time stamp
        self.timestep = timestep
        self.minuteIntervals = timedelta(1 / (24.0 * self.timestep))

        # calculate timestamps and hoursOfYear
        # A dictionary for datetimes. Key values will be minute of year
        self.__timestampsData = list()
        self.__calculateTimestamps()

    @classmethod
    def fromAnalysisPeriod(cls, analysisPeriod=None):
        """Create and AnalysisPeriod from an analysis period.

        This method is useful to be called from inside Grasshopper or Dynamo
        """
        if not analysisPeriod:
            return cls()
        elif hasattr(analysisPeriod, 'isAnalysisPeriod'):
            return analysisPeriod
        elif isinstance(analysisPeriod, str):
            try:
                return cls.__fromAnalysisPeriodString(analysisPeriod)
            except Exception as e:
                raise ValueError(
                    "{} is not convertable to an AnalysisPeriod: {}".format(
                        analysisPeriod, e)
                )

    @classmethod
    def __fromAnalysisPeriodString(cls, analysisPeriodString):
        """Create an Analysis Period object from an analysis period string."""
        # %s/%s to %s/%s between %s to %s @%s
        ap = analysisPeriodString.lower().replace(' ', '') \
            .replace('to', ' ') \
            .replace('/', ' ') \
            .replace('between', ' ') \
            .replace('@', ' ')
        try:
            stMonth, stDay, endMonth, endDay, stHour, endHour, timestep = ap.split(' ')
            return cls(stMonth, stDay, stHour, endMonth, endDay, endHour, int(timestep))
        except Exception as e:
            raise ValueError(str(e))

    @property
    def isAnalysisPeriod(self):
        """Return True."""
        return True

    def __isPossibleHour(self, hour):
        """Check if a float hour is a possible hour for this analysis period."""
        if hour > 23 and self.__isPossibleHour(0):
            hour = int(hour)
        if not self.overnight:
            return self.stTime.hour <= hour <= self.endTime.hour
        else:
            return self.stTime.hour <= hour <= 23 or \
                0 <= hour <= self.endTime.hour

    def __calcTimestamps(self, stTime, endTime):
        """Calculate timesteps between start time and end time.

        Use this method only when start time month is before end time month.
        """
        # calculate based on minutes
        # I have to convert the object to LBDateTime because of how Dynamo
        # works: https://github.com/DynamoDS/Dynamo/issues/6683
        # Do not modify this line to datetime
        curr = datetime(stTime.year, stTime.month, stTime.day, stTime.hour,
                        stTime.minute)
        endTime = datetime(endTime.year, endTime.month, endTime.day,
                           endTime.hour, endTime.minute)

        while curr <= endTime:
            if self.__isPossibleHour(curr.hour + (curr.minute / 60.0)):
                time = LBDateTime(curr.month, curr.day, curr.hour, curr.minute)
                self.__timestampsData.append(time.MOY)
            curr += self.minuteIntervals

        if self.timestep != 1 and curr.hour == 23 and self.__isPossibleHour(0):
            # This is for cases that timestep is more than one
            # and last hour of the day is part of the calculation
            curr = endTime
            for i in range(self.timestep)[1:]:
                curr += self.minuteIntervals
                time = LBDateTime(curr.month, curr.day, curr.hour, curr.minute)
                self.__timestampsData.append(time.MOY)

    def __calculateTimestamps(self):
        """Return a list of Ladybug DateTime in this analysis period."""
        if not self.reversed:
            self.__calcTimestamps(self.stTime, self.endTime)
        else:
            self.__calcTimestamps(self.stTime, LBDateTime.fromHOY(8759))
            self.__calcTimestamps(LBDateTime.fromHOY(0), self.endTime)

    @property
    def datetimes(self):
        """A sorted list of datetimes in this analysis period."""
        # sort dictionary based on key values (minute of the year)
        return tuple(LBDateTime.fromMOY(MOY) for MOY in self.__timestampsData)

    @property
    def HOYs(self):
        """A sorted list of hours of year in this analysis period."""
        return tuple(MOY / 60.0 for MOY in self.__timestampsData)

    @property
    def intHOYs(self):
        """A sorted list of hours of year as float values in this analysis period."""
        return tuple(int(MOY / 60) for MOY in self.__timestampsData)

    @property
    def isAnnual(self):
        """Check if an analysis period is annual."""
        return True if len(self.__timestampsData) / self.timestep == 8760 \
            else False

    def isTimeIncluded(self, time):
        """Check if time is included in analysis period.

        Return True if time is inside this analysis period,
        otherwise return False

        Args:
            time: A LBDateTime to be tested

        Returns:
            A boolean. True if time is included in analysis period
        """
        # time filtering in Ladybug and honeybee is slightly different since
        # start hour and end hour will be applied for every day.
        # For instance 2/20 9am to 2/22 5pm means hour between 9-17
        # during 20, 21 and 22 of Feb.
        return time.MOY in self.__timestampsData

    def ToString(self):
        """Overwrite .NET representation."""
        return self.__repr__()

    def __str__(self):
        """Return analysis period as a string."""
        return self.__repr__()

    def __repr__(self):
        """Return analysis period as a string."""
        return "%s/%s to %s/%s between %s to %s @%d" % \
            (self.stTime.month, self.stTime.day,
             self.endTime.month, self.endTime.day,
             self.stTime.hour, self.endTime.hour,
             self.timestep)
