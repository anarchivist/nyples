"""
parsers.py: contains Parser class for zgw.py
"""

from web.net import htmlquote
from pymarc import MARCReader, marc8_to_unicode
from settings import IGNORE_UNICODE_ERRORS

class ParseError(Exception):
  """Base class for exceptions from this module"""
  pass

class Parser:
  """Base class for parsers used by zgw"""

  def to_html(self, result):
    """
    Takes a result, converts it to Unicode (assumes result is MARC8), escapes
    characters for HTML, and adds linebreak tags where newlines occur.
    """
    result = result.replace('\n', '<br/>\n')
    sanitized = htmlquote(result)
    return sanitized.replace('&lt;br/&gt;', '<br/>\n')

  def to_unicode(self):
    """Converts MARC8 encoded data to Unicode."""
    result = self.__str__()
    result_html = Parser().to_html(result)
    try:
      result_out = marc8_to_unicode(result_html)
    except:
      if IGNORE_UNICODE_ERRORS == True:
        result_out = "<strong>NOTE: MARC8 to Unicode conversion failed on this \
                 record.</strong><br/>\n%s" % result
      else:
        raise
    return result_out

