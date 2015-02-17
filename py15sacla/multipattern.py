#!/usr/bin/env python

"""This module allows matching of multiple patterns to the same string.
The patterns support anchoring at the beginning or the end of string
and a match of a range of integer numbers.

Pattern syntax:

^start  -- match "start" only at the beginning of the string
end$    -- match "end" only at the end of string
<7>     -- match number 7 preceded by any number of leading zeros
<1-34>  -- match an integer range.  The matched number may have
           one or more leading zeros
<7->    -- match an integer greater or equal 7 allowing leading zeros
<->     -- match any integer

All other patterns are matched literally, including a single '^' or '$'.
"""

import re


def match(patterns, s):
    '''True if all patterns match the string.

    patterns -- a list of string patterns.  Can be also a string that gets
                split to sub-patterns according to shell quoting rules.
    s        -- string to be matched

    Return bool.
    See module docstring for pattern syntax.
    '''
    mp = MultiPattern(patterns)
    return mp.match(s)


class MultiPattern(object):
    '''Object with parsed multiple patterns that is ready for matching.

    Data attributes:

    patterns        -- list of unique input patterns
    fixed_patterns  -- patterns to be matched as fixed strings
    re_patterns     -- list of regular expression objects
    re_validators   -- a dictionary mapping RE object to a list of
                       validator functions, that can for example check
                       the integer range.
    '''


    def __init__(self, patterns):
        '''Initialize new MultiPattern object.

        patterns    -- a sequence of string patterns, all of them must match.
                       Can be also a single string that gets split to
                       sub-patterns according to shell quoting rules.

        No return value.
        See module docstring for pattern syntax.
        '''
        import shlex
        # declare object attributes
        self.patterns = []
        self.fixed_patterns = []
        self.re_patterns = []
        self.re_validators = {}
        # process inputs
        plist = patterns
        if isinstance(patterns, basestring):
            plist = shlex.split(patterns)
        duplicates = set()
        for p in plist:
            if not p in duplicates:  self.patterns.append(p)
            duplicates.add(p)
        self._parsePatterns()
        return


    def match(self, s):
        '''Check if all patterns match the string.

        s -- string to be checked

        Return bool.
        '''
        ismatch = True
        for p in self.fixed_patterns:
            if not ismatch: break
            ismatch = p in s
        for rx in self.re_patterns:
            if not ismatch: break
            mxlist = list(rx.finditer(s))
            ismatch = bool(mxlist)
            # apply validators while things are matching
            validators = self.re_validators.get(rx, [])
            for validate in validators:
                anymatchvalid = filter(validate, mxlist)
                ismatch = ismatch and anymatchvalid
        return bool(ismatch)


    def _parsePatterns(self):
        '''Identify internal patterns as fixed or regular expressions.

        Updates the fixed_patterns and re_patterns attributes.
        No return value.
        '''
        for p in self.patterns:
            # build regular expressions for special patterns
            rx = self._parseSpecialPattern(p)
            if rx is None:
                self.fixed_patterns.append(p)
            else:
                self.re_patterns.append(rx)
        return


    def _parseSpecialPattern(self, p):
        '''Process patterns that contain special syntax.

        p   -- string pattern

        Return regular expression object or None when p is not special.
        Update the re_validators dictionary if necessary to check range.
        '''
        wr = re.split(r'(<\d*-\d*>|<\d+>)', p)
        rangespecs = wr[1::2]
        rangecount = len(rangespecs)
        # replace range specifications with an RE group of several digits
        wr1 = wr[:]
        wr1[1::2] = rangecount * [r'(\d+)']
        isfixedpattern = not rangecount
        # check if we need to anchor to the beginning
        p1head = ''
        if p.startswith('^') and len(p) > 1:
            p1head = '^'
            wr1[0] = wr[0][1:]
            isfixedpattern = False
        # check for anchoring to the end of string
        p1tail = ''
        if p.endswith('$') and len(p) > 1:
            p1tail = '$'
            wr1[-1] = wr1[-1][:-1]
            isfixedpattern = False
        # escape non-range parts of the pattern
        wr1[0::2] = map(re.escape, wr1[0::2])
        # create validator for each range specification in the pattern
        rangevalidators = []
        for i, spec in enumerate(rangespecs):
            grpidx = i + 1
            # use None for either limit that has not been specified
            lohi = [(int(w) if w else None)
                    for w in spec.strip('<>').split('-')]
            # lohi has just one element for the '<\d+>' pattern.
            if len(lohi) == 1:  lohi = lohi + lohi
            lo, hi = lohi
            validator = _ValidateMatchGroupRange(grpidx, lo, hi)
            rangevalidators.append(validator)
        # determine return value
        if isfixedpattern:
            rv = None
        else:
            # return compiled regular expression
            p1 = p1head + ''.join(wr1) + p1tail
            rv = re.compile(p1)
            self.re_validators[rv] = rangevalidators
        return rv

# End of class MultiPattern

# Local Helpers --------------------------------------------------------------

class _ValidateMatchGroupRange(object):
    '''Functor for checking if RE group is an integer inside the given range.

    Data:

    grpidx  -- index of RE group that contains the checked number
    lobound -- inclusive lower boundary of the accepted range.
               Do not check lower boundary when None.
    hibound -- inclusive upper boundary of the accepted range
               Do not check upper boundary when None.
    '''

    def __init__(self, grpidx, lobound, hibound):
        '''Initialize _ValidateMatchGroupRange object.

        grpidx  -- index of RE group that contains the checked number
        lobound -- inclusive lower boundary of the accepted range.
                   Do not check lower boundary when None.
        hibound -- inclusive upper boundary of the accepted range
                   Do not check upper boundary when None.

        No return value.
        '''
        self.grpidx = grpidx
        self.lobound = lobound
        self.hibound = hibound
        return


    def __call__(self, mxobj):
        '''Validate a regular expression Match object.

        mxobj   -- an instance of regular expression Match object

        Return bool.
        '''
        n = int(mxobj.group(self.grpidx))
        rv = ((self.lobound is None or self.lobound <= n) and
              (self.hibound is None or n <= self.hibound))
        return rv

# End of class _ValidateMatchGroupRange

# End of file
