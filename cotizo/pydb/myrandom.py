"""Some random functions

This module will provide a set of functions that will return random datatypes.
For now, there only the following datatypes are supported:

* INTEGER => myrandom.Integer(low, high)
* REAL => myrandom.Real(low, high)
* TEXT => myrandom.Text(length)
"""

import random

def Integer(low, high):
    """Will return a random integer between low and high.
    Wrapper for random.randint()"""
    random.seed()
    return random.randint(low, high)

def Real(low, high):
    """Will return a random real number between low and high.
    Based on random.random()"""
    random.seed()
    return random.random() * (high-low) + low

def Text(length = None):
    """Will return a random generated string composed only from letters (lowercase and uppercase).
    If the length of the string is not supplied, it is randomly chosen between 1 and 100."""
    random.seed()
    if length == None:
        length = Integer(1, 100)
    # Integer(0,25) will choose one random letter, 65 is the offset for
    # uppercase, and Integer(0,1)*32 will make the letter lowercase
    chars = [chr(Integer(0,25)+65+Integer(0,1)*32) for i in xrange(length)]
    return "".join(chars)
