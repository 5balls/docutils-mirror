#!/usr/bin/env python
# -*- coding: utf8 -*-
# :Copyright: © 2011 Günter Milde.
# :License: Released under the terms of the `2-Clause BSD license`_, in short:
#
#    Copying and distribution of this file, with or without modification,
#    are permitted in any medium without royalty provided the copyright
#    notice and this notice are preserved.
#    This file is offered as-is, without any warranty.
#
# .. _2-Clause BSD license: http://www.spdx.org/licenses/BSD-2-Clause

# :Id: $Id$

import sys, re
import unicodedata

# punctuation characters around inline markup
# ===========================================
#
# This module provides the lists of characters for the implementation of
# the `inline markup recognition rules`_ in the reStructuredText parser
# (states.py)
#
# .. _inline markup recognition rules:
#     ../../docs/ref/rst/restructuredtext.html#inline-markup

# Docutils punctuation category sample strings
# --------------------------------------------
#
# The sample strings are generated by punctuation_samples() and put here
# literal to avoid the time-consuming generation with every Docutils run.
# As the samples are used inside ``[ ]`` in regular expressions, hyphen and
# square brackets are escaped. ::

openers = (u'"\'(<\\[{\u0f3a\u0f3c\u169b\u2045\u207d\u208d\u2329\u2768'
           u'\u276a\u276c\u276e\u2770\u2772\u2774\u27c5\u27e6\u27e8\u27ea'
           u'\u27ec\u27ee\u2983\u2985\u2987\u2989\u298b\u298d\u298f\u2991'
           u'\u2993\u2995\u2997\u29d8\u29da\u29fc\u2e22\u2e24\u2e26\u2e28'
           u'\u3008\u300a\u300c\u300e\u3010\u3014\u3016\u3018\u301a\u301d'
           u'\u301d\ufd3e\ufe17\ufe35\ufe37\ufe39\ufe3b\ufe3d\ufe3f\ufe41'
           u'\ufe43\ufe47\ufe59\ufe5b\ufe5d\uff08\uff3b\uff5b\uff5f\uff62'
           u'\xab\u2018\u201c\u2039\u2e02\u2e04\u2e09\u2e0c\u2e1c\u2e20'
           u'\u201a\u201e\xbb\u2019\u201d\u203a\u2e03\u2e05\u2e0a\u2e0d'
           u'\u2e1d\u2e21\u201b\u201f')
closers = (u'"\')>\\]}\u0f3b\u0f3d\u169c\u2046\u207e\u208e\u232a\u2769'
           u'\u276b\u276d\u276f\u2771\u2773\u2775\u27c6\u27e7\u27e9\u27eb'
           u'\u27ed\u27ef\u2984\u2986\u2988\u298a\u298c\u298e\u2990\u2992'
           u'\u2994\u2996\u2998\u29d9\u29db\u29fd\u2e23\u2e25\u2e27\u2e29'
           u'\u3009\u300b\u300d\u300f\u3011\u3015\u3017\u3019\u301b\u301e'
           u'\u301f\ufd3f\ufe18\ufe36\ufe38\ufe3a\ufe3c\ufe3e\ufe40\ufe42'
           u'\ufe44\ufe48\ufe5a\ufe5c\ufe5e\uff09\uff3d\uff5d\uff60\uff63'
           u'\xbb\u2019\u201d\u203a\u2e03\u2e05\u2e0a\u2e0d\u2e1d\u2e21'
           u'\u201b\u201f\xab\u2018\u201c\u2039\u2e02\u2e04\u2e09\u2e0c'
           u'\u2e1c\u2e20\u201a\u201e')
delimiters = (u'\\-/:\u058a\xa1\xb7\xbf\u037e\u0387\u055a-\u055f\u0589'
              u'\u05be\u05c0\u05c3\u05c6\u05f3\u05f4\u0609\u060a\u060c'
              u'\u060d\u061b\u061e\u061f\u066a-\u066d\u06d4\u0700-\u070d'
              u'\u07f7-\u07f9\u0830-\u083e\u0964\u0965\u0970\u0df4\u0e4f'
              u'\u0e5a\u0e5b\u0f04-\u0f12\u0f85\u0fd0-\u0fd4\u104a-\u104f'
              u'\u10fb\u1361-\u1368\u1400\u166d\u166e\u16eb-\u16ed\u1735'
              u'\u1736\u17d4-\u17d6\u17d8-\u17da\u1800-\u180a\u1944\u1945'
              u'\u19de\u19df\u1a1e\u1a1f\u1aa0-\u1aa6\u1aa8-\u1aad\u1b5a-'
              u'\u1b60\u1c3b-\u1c3f\u1c7e\u1c7f\u1cd3\u2010-\u2017\u2020-'
              u'\u2027\u2030-\u2038\u203b-\u203e\u2041-\u2043\u2047-'
              u'\u2051\u2053\u2055-\u205e\u2cf9-\u2cfc\u2cfe\u2cff\u2e00'
              u'\u2e01\u2e06-\u2e08\u2e0b\u2e0e-\u2e1b\u2e1e\u2e1f\u2e2a-'
              u'\u2e2e\u2e30\u2e31\u3001-\u3003\u301c\u3030\u303d\u30a0'
              u'\u30fb\ua4fe\ua4ff\ua60d-\ua60f\ua673\ua67e\ua6f2-\ua6f7'
              u'\ua874-\ua877\ua8ce\ua8cf\ua8f8-\ua8fa\ua92e\ua92f\ua95f'
              u'\ua9c1-\ua9cd\ua9de\ua9df\uaa5c-\uaa5f\uaade\uaadf\uabeb'
              u'\ufe10-\ufe16\ufe19\ufe30-\ufe32\ufe45\ufe46\ufe49-\ufe4c'
              u'\ufe50-\ufe52\ufe54-\ufe58\ufe5f-\ufe61\ufe63\ufe68\ufe6a'
              u'\ufe6b\uff01-\uff03\uff05-\uff07\uff0a\uff0c-\uff0f\uff1a'
              u'\uff1b\uff1f\uff20\uff3c\uff61\uff64\uff65\U00010100'
              u'\U00010101\U0001039f\U000103d0\U00010857\U0001091f\U0001093f'
              u'\U00010a50-\U00010a58\U00010a7f\U00010b39-\U00010b3f'
              u'\U000110bb\U000110bc\U000110be-\U000110c1\U00012470-'
              u'\U00012473')
closing_delimiters = u'\\\\.,;!?'

# Matching open/close quotes
# --------------------------

# Rule (5) requires determination of matching open/close pairs. However,
# the pairing of open/close quotes is ambigue due to  different typographic
# conventions in different languages.

quote_pairs = {u'\xbb': u'\xbb', # Swedish
            u'\u2018': u'\u201a', # Greek
            u'\u2019': u'\u2019', # Swedish
            u'\u201a': u'\u2018\u2019', # German, Polish
            u'\u201c': u'\u201e', # German
            u'\u201e': u'\u201c\u201d',
            u'\u201d': u'\u201d', # Swedish
            u'\u203a': u'\u203a', # Swedish
            }

def match_chars(c1, c2):
    try:
        i = openers.index(c1)
    except ValueError:  # c1 not in openers
        return False
    return c2 == closers[i] or c2 in quote_pairs.get(c1, '')


# Running this file as a standalone module checks the definitions against a
# re-calculation::

if __name__ == '__main__':


# Unicode punctuation character categories
# ----------------------------------------

    unicode_punctuation_categories = {
        # 'Pc': 'Connector', # not used in Docutils inline markup recognition
        'Pd': 'Dash',
        'Ps': 'Open',
        'Pe': 'Close',
        'Pi': 'Initial quote', # may behave like Ps or Pe depending on usage
        'Pf': 'Final quote', # may behave like Ps or Pe depending on usage
        'Po': 'Other'
        }
    """Unicode character categories for punctuation"""


# generate character pattern strings
# ==================================

    def unicode_charlists(categories, cp_min=0, cp_max=None):
        """Return dictionary of Unicode character lists.

        For each of the `catagories`, an item contains a list with all Unicode
        characters with `cp_min` <= code-point <= `cp_max` that belong to the
        category. (The default values check every code-point supported by Python.)
        """
        # Determine highest code point with one of the given categories
        # (may shorten the search time considerably if there are many
        # categories with not too high characters):
        if cp_max is None:
            cp_max = max(x for x in xrange(sys.maxunicode + 1)
                        if unicodedata.category(unichr(x)) in categories)
            # print cp_max # => 74867 for unicode_punctuation_categories
        charlists = {}
        for cat in categories:
            charlists[cat] = [unichr(x) for x in xrange(cp_min, cp_max+1)
                            if unicodedata.category(unichr(x)) == cat]
        return charlists


# Character categories in Docutils
# --------------------------------

    def punctuation_samples():

        """Docutils punctuation category sample strings.

        Return list of sample strings for the categories "Open", "Close",
        "Delimiters" and "Closing-Delimiters" used in the `inline markup
        recognition rules`_.
        """

        # Lists with characters in Unicode punctuation character categories
        cp_min = 160 # ASCII chars have special rules for backwards compatibility
        ucharlists = unicode_charlists(unicode_punctuation_categories, cp_min)

        # match opening/closing characters
        # --------------------------------
        # Rearange the lists to ensure matching characters at the same
        # index position.

        # low quotation marks are also used as closers (e.g. in Greek)
        # move them to category Pi:
        ucharlists['Ps'].remove(u'‚') # 201A  SINGLE LOW-9 QUOTATION MARK
        ucharlists['Ps'].remove(u'„') # 201E  DOUBLE LOW-9 QUOTATION MARK
        ucharlists['Pi'] += [u'‚', u'„']

        ucharlists['Pi'].remove(u'‛') # 201B  SINGLE HIGH-REVERSED-9 QUOTATION MARK
        ucharlists['Pi'].remove(u'‟') # 201F  DOUBLE HIGH-REVERSED-9 QUOTATION MARK
        ucharlists['Pf'] += [u'‛', u'‟']

        # 301F  LOW DOUBLE PRIME QUOTATION MARK misses the opening pendant:
        ucharlists['Ps'].insert(ucharlists['Pe'].index(u'\u301f'), u'\u301d')

        # print u''.join(ucharlists['Ps']).encode('utf8')
        # print u''.join(ucharlists['Pe']).encode('utf8')
        # print u''.join(ucharlists['Pi']).encode('utf8')
        # print u''.join(ucharlists['Pf']).encode('utf8')

        # The Docutils character categories
        # ---------------------------------
        #
        # The categorization of ASCII chars is non-standard to reduce
        # both false positives and need for escaping. (see `inline markup
        # recognition rules`_)

        # allowed before markup if there is a matching closer
        openers = [u'"\'(<\\[{']
        for cat in ('Ps', 'Pi', 'Pf'):
            openers.extend(ucharlists[cat])

        # allowed after markup if there is a matching opener
        closers = [u'"\')>\\]}']
        for cat in ('Pe', 'Pf', 'Pi'):
            closers.extend(ucharlists[cat])

        # non-matching, allowed on both sides
        delimiters = [u'\\-/:']
        for cat in ('Pd', 'Po'):
            delimiters.extend(ucharlists[cat])

        # non-matching, after markup
        closing_delimiters = [r'\\.,;!?']

        # # Test open/close matching:
        # for i in range(min(len(openers),len(closers))):
        #     print '%4d    %s    %s' % (i, openers[i].encode('utf8'),
        #                                closers[i].encode('utf8'))

        return [u''.join(chars) for chars in (openers, closers, delimiters,
                                              closing_delimiters)]


    def mark_intervals(s):
        """Return s with shortcut notation for runs of consecutive characters

        Sort string and replace 'cdef' by 'c-f' and similar.
        """
        l =[]
        s = [ord(ch) for ch in s]
        s.sort()
        for n in s:
            try:
                if l[-1][-1]+1 == n:
                    l[-1].append(n)
                else:
                    l.append([n])
            except IndexError:
                l.append([n])

        l2 = []
        for i in l:
            i = [unichr(n) for n in i]
            if len(i) > 2:
                i = i[0], u'-', i[-1]
            l2.extend(i)

        return ''.join(l2)

    def wrap_string(s, startstring= "(",
                       endstring = ")", wrap=65):
        """Line-wrap a unicode string literal definition."""
        c = len(startstring)
        contstring = "'\n" + ' ' * len(startstring) + "u'"
        l = [startstring]
        for ch in s:
            c += 1
            if ch == '\\' and c > wrap:
                c = len(startstring)
                ch = contstring + ch
            l.append(ch)
        l.append(endstring)
        return ''.join(l)


# print results
# =============

# (re) create and compare the samples:

    (o, c, d, cd) = punctuation_samples()
    d_sorted = d[:5] + mark_intervals(d[5:])
    if o != openers:
        print '- openers = ur"""%s"""' % openers.encode('utf8')
        print '+ openers = ur"""%s"""' % o.encode('utf8')
    if c != closers:
        print '- closers = ur"""%s"""' % closers.encode('utf8')
        print '+ closers = ur"""%s"""' % c.encode('utf8')
    if d_sorted != delimiters:
        print '- delimiters = ur"%s"' % delimiters.encode('utf8')
        print '+ delimiters = ur"%s"' % d.encode('utf8')
    if cd != closing_delimiters:
        print '- closing_delimiters = ur"%s"' % closing_delimiters.encode('utf8')
        print '+ closing_delimiters = ur"%s"' % cd.encode('utf8')


# Print literal code to define the character sets:

    # `openers` and `closers` must be verbose and keep order because they are
    # also used in `match_chars()`.
    print wrap_string(repr(o), startstring= "openers = (")
    print wrap_string(repr(c), startstring= "closers = (")
    # delimiters: sort and use shortcut for intervals (saves ~150 characters):
    print wrap_string(repr(d_sorted), startstring= "delimiters = (")
    print 'closing_delimiters =', repr(cd)

# test prints

    # print 'openers = ', repr(openers)
    # print 'closers = ', repr(closers)
    # print 'delimiters = ', repr(delimiters)
    # print 'closing_delimiters = ', repr(closing_delimiters)

    # ucharlists = unicode_charlists(unicode_punctuation_categories)
    # for cat, chars in ucharlists.items():
    #     # print cat, chars
    #     # compact output (visible with a comprehensive font):
    #     print (u":%s: %s" % (cat, u''.join(chars))).encode('utf8')

# verbose print

    # print 'openers:'
    # for ch in openers:
    #     print ch.encode('utf8'), unicodedata.name(ch)
    # print 'closers:'
    # for ch in closers:
    #     print ch.encode('utf8'), unicodedata.name(ch)
    # print 'delimiters:'
    # for ch in delimiters:
    #     print ch.encode('utf8'), unicodedata.name(ch)
    # print 'closing_delimiters:'
    # for ch in closing_delimiters:
    #     print ch.encode('utf8'), unicodedata.name(ch)
