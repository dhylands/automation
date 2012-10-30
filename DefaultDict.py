# DefaultDict is a dictionary that returns an empty string for non-existing keys.
#
# You can also provide a dictionary containing initial values.
# 
import collections

def DefaultDict(init = {}):
    """A dictionary that returns an empty string for non-existing keys."""
    d = collections.defaultdict(lambda: '')
    for item in init:
        d[item] = init[item]
    return d

def ErrorFound(d):
    """Returns True if any non-empty values are found (useful for dictionaries of error messages)"""
    for item in d:
        if d[item]:
            return True
    return False

def PrintErrors(d):
    """Prints any errors detected."""
    for item in d:
        if d[item]:
            print 'Error:', item, '-', d[item]


