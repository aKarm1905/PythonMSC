"""
Provides base class and standard filters to filter the usage records data,
provided by the pyrevit.usagelog module.

    Base filter class is:
        >>> RecordFilter()

    This module provides a function ``get_auto_filters()`` that looks
    into the provided records list and automatically creates useful
    filters for that data.
        >>> record_list = [] # List of records
        >>> get_auto_filters(record_list)

"""

from pyrevit.coreutils import get_all_subclasses
from pyrevit.coreutils.logger import get_logger
from pyrevit.usagelog.record import RESULT_DICT


#pylint: disable=W0703,C0302,C0103
mlogger = get_logger(__name__)


class RecordFilter(object):
    """
    Superclass of all UsageRecord filters. Use the subclasses for each of
    access to standard parameters.

    Class Attributes:
        RecordFilter.filter_param (str): This is the parameter name of
                                         the UsageRecord object,
                                         filtered by this filter
        RecordFilter.name_template (str): This template is used to create
                                          a human-readable name for the filter

    Attributes:
        filter_value (str): Any UsageRecord object that
                            object.filter_param == filter_value,
                            will pass the filter
        filter_name (str): Human-readable name for this filter.
    """

    filter_param = ''
    name_template = ''

    def __init__(self, filter_value):
        self.filter_value = filter_value
        self.filter_name = self.name_template.format(self.filter_value)

    def __eq__(self, other):
        return self.filter_value == other.filter_value

    def __ne__(self, other):
        return self.filter_value != other.filter_value

    def __hash__(self):
        return hash(self.filter_value)

    def __lt__(self, other):
        # less-than operator overload that causes the filter list to be
        # sorted by name and then by value if two filters are the same type,
        # compare based on filter_value
        if isinstance(self, type(other)):
            return self.filter_value < other.filter_value
        else:
            # if not, compare based on filter_name
            return self.filter_name < other.filter_name

    def filter_records(self, record_list, search_term=None):
        """Filters the input list of UsageRecord objects.

        Example:
            >>> all_records = [] # List of all records
            >>> recfilter = RecordCommandFilter('command name to filter')
            >>> recfilter.filter_records(all_records, search_term="some term")

        Args:
            record_list (list): List of UsageRecord object to be filtered
            search_term (str): If provided, filters all objects that
                               pass object.has_term(search_term)

        Returns:
            list: Filtered list of UsageRecord objects.

        """

        filtered_list = []
        for record in record_list:
            # test for paraemter value
            if getattr(record, self.filter_param) == self.filter_value:
                # Passed filter value test:
                if search_term:
                    # check for search_term if provided
                    if record.has_term(search_term.lower()):
                        filtered_list.append(record)
                else:
                    # else add to filtered_list
                    filtered_list.append(record)

        return filtered_list


class RecordNoneFilter(RecordFilter):
    """RecordFilter that has no effect. All records pass this filter."""

    type_id = ''

    def __init__(self):
        super(RecordNoneFilter, self).__init__('None')
        self.filter_name = 'No Filter'

    def __eq__(self, other):
        return isinstance(self, type(other))

    def __ne__(self, other):
        return not isinstance(self, type(other))

    def __hash__(self):
        return hash(0)

    def __lt__(self, other):
        return True

    def filter_records(self, record_list, search_term=None):
        if search_term:
            filtered_list = []
            for record in record_list:
                if record.has_term(search_term.lower()):
                    filtered_list.append(record)

            return filtered_list
        else:
            return record_list


class RecordDateFilter(RecordFilter):
    filter_param = 'date'
    name_template = 'Date: {}'


# class RecordTimeFilter:
#     filter_param = 'time'


class RecordUsernameFilter(RecordFilter):
    filter_param = 'username'
    name_template = 'User: {}'


class RecordRevitVersionFilter(RecordFilter):
    filter_param = 'revit'
    name_template = 'Revit Version: {}'


class RecordRevitBuildFilter(RecordFilter):
    filter_param = 'revitbuild'
    name_template = 'Revit Build: {}'


class RecordSessionFilter(RecordFilter):
    filter_param = 'sessionid'
    name_template = 'Session Id: {}'


class RecordPyRevitVersionFilter(RecordFilter):
    filter_param = 'pyrevit'
    name_template = 'pyRevit Version: {}'


class RecordDebugModeFilter(RecordFilter):
    filter_param = 'debug'
    name_template = 'Debug Mode: {}'


class RecordAltScriptFilter(RecordFilter):
    filter_param = 'alternate'
    name_template = 'Alternate Mode: {}'


class RecordCommandFilter(RecordFilter):
    filter_param = 'commandname'
    name_template = 'Command Name: {}'


# class RecordBundleFilter(RecordFilter):
#     filter_param = 'commandbundle'
#     name_template = 'Bundle: {}'


class RecordBundleTypeFilter(RecordFilter):
    """Filters records based on bundle type (e.g. pushbutton)."""

    filter_param = 'commandbundle'
    name_template = 'Bundle Type: {}'

    def __init__(self, filter_value):
        super(RecordBundleTypeFilter, self).__init__(filter_value)
        self.filter_value = filter_value.split('.')[1]
        self.filter_name = self.name_template.format(self.filter_value)

    def filter_records(self, record_list, search_term=None):
        filtered_list = []
        for record in record_list:
            if getattr(record, self.filter_param).endswith(self.filter_value):
                if search_term:
                    if record.has_term(search_term.lower()):
                        filtered_list.append(record)
                else:
                    filtered_list.append(record)
        return filtered_list


class RecordExtensionFilter(RecordFilter):
    filter_param = 'commandextension'
    name_template = 'Extension: {}'


class RecordResultFilter(RecordFilter):
    """
    Filters records based on result code (e.g. 0, 1, 2).
    Also overrides filter_name to convert the integer result code to
    human-readable code name.
    """

    filter_param = 'resultcode'
    name_template = 'Result Code: {}'

    def __init__(self, filter_value):
        RecordFilter.__init__(self, filter_value)
        # overrides filter_name to convert the integer result code
        # to human-readable codename
        self.filter_name = self.name_template\
            .format(RESULT_DICT[self.filter_value])


def get_auto_filters(record_list):
    """
    Returns a list of RecordFilter objects. This function works on the input
    list of usage records. This function traverses the usage records list,
    finds the parameters on each record object and creates a filter object for
    each (if a subclass of RecordFilter is available to that parameter)

    Any of the filter objects returned from this function, can be passed to
    the db.get_records() method to filter the usage record data.

        Example of typical use:
        >>> from pyrevit.usagelog import db, filters
        >>> all_unfiltered_records = db.get_records()
        >>> filter_list = filters.get_auto_filters(all_unfiltered_records)
        >>> chosen_filter = filter_list[0] # type: RecordFilter
        >>> filtered_records = db.get_records(record_filter=chosen_filter)

    Args:
        record_list (list): list of UsageRecord objects

    Returns:
        list: returns a list of RecordFilter objects, sorted; Empty list if
              no filters could be created.
    """
    # lets find all subclasses of the RecordFilter class (all custom filters)
    filter_types = get_all_subclasses([RecordFilter])
    # and make a filter dictionary based on the filter parameter names
    # so filters_dict['commandname'] returns a filter that filters the
    # records based on their 'commandname' property
    filters_dict = {f.filter_param: f for f in filter_types}

    # make a filter list and add the `None` filter to it.
    auto_filters = set()
    auto_filters.add(RecordNoneFilter())
    for record in record_list:
        # find parameters in the record object
        for param, value in record.__dict__.items():
            if param in filters_dict:
                # and if a filter is provided for that parameter,
                # setup the filter and add to the list.
                mlogger.debug('Adding filter: param=%s value=%s', param, value)
                auto_filters.add(filters_dict[param](value))

    # return a sorted list of filters for ease of use
    return sorted(auto_filters)
