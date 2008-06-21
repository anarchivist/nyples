"""
settings.py - for zgw.py

IGNORE_UNICODE_ERRORS does what it says; see parsers.py for the related
implementation. I specifically added this as the EACC records from the Library
of Congress can make pymarc.marc8_to_unicode fail. See
http://www.loc.gov/z3950/lcserver.html#limt for more information.
"""
IGNORE_UNICODE_ERRORS = True 

"""
SERVER specifies the Z39.50 server for queries. All elements of this
dictionary are required.

SERVER['qsyntax']: query syntax. As of PyZ3950 2.04, the following query
syntaxes are supported: CCL, S-CCL, CQL, S-CQL, PQF, C2, SQL, CQL-TREE. See
PyZ3950 docs for more information.

SERVER['rsyntax']: result syntax; zgw parses SUTRS, USMARC, XML only for now.

SERVER['element_set']: Element set names vary from host to host; e.g. for
result syntax XML at LC, the following element sets are available: 'dc',
'mods', 'marcxml', 'opacxml'. Treat 'F' as the default unless you know you
need something else.

Sample server entries:

SERVER = {'host': 'library.usc.edu', 'port': 2200, 'db': 'unicorn',
          'qsyntax': 'CCL', 'rsyntax': 'USMARC', 'element_set': 'F'}
SERVER = {'host': 'z3950cat.bl.uk, 'port': 9909, 'db': 'BLAC',
          'qsyntax': 'CCL', 'rsyntax': 'SUTRS', 'element_set': 'F'} 
"""
SERVER = {'host': 'z3950.loc.gov', 'port': 7090, 'db': 'VOYAGER',
          'qsyntax': 'CCL', 'rsyntax': 'USMARC', 'element_set': 'F'}

