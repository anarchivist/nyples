#!/usr/bin/env PYTHONPATH=/home/matienzo/lib/python2.4/site-packages python2.4
"""
nyples.py
"""

import pymarc
import web
from Ft.Xml import InputSource
from Ft.Xml.Xslt.Processor import Processor
from PyZ3950 import zoom
from parsers import ParseError, Parser

urls = (
    '/', 'usage',
    '/search/(.*)', 'search',
    '/marcxml/(.*)', 'marcxml',
    '/mods/(.*)', 'mods',
    '/query', 'search'
)

SERVER = {'host': 'catnyp.nypl.org', 'port': 210, 'db': 'INNOPAC',
            'qsyntax': 'PQF', 'rsyntax': 'USMARC', 'element_set': 'F'}
MODS_XSLT = InputSource.DefaultFactory.fromUri('http://www.loc.gov/standards/mods/v3/MARC21slim2MODS3-2.xsl')
BASE_QUERY = '@attr 1=12 '


render = web.template.render('templates/')
zoom.ResultSet.__bases__ += (Parser,)
pymarc.Record.__bases__ += (Parser,)
p = Parser()

def run_query(server, qs):
    """Creates Z39.50 connection, sends query, parses results"""
    conn = zoom.Connection(SERVER['host'],
                            SERVER['port'],
                            databaseName=SERVER['db'],
                            preferredRecordSyntax=SERVER['rsyntax'],
                            elementSetName=SERVER['element_set'])
    out = []
    query = zoom.Query(SERVER['qsyntax'], '%s%s' % (BASE_QUERY, qs))
    result_set = conn.search(query)
    for result in result_set:
        if result.syntax in ('USMARC', 'MARC21'):
            r = pymarc.Record(data=result.data)     # deserialize
            conv_record = pymarc.record_to_xml(r)
        elif result.syntax in ('SUTRS', 'XML'): # doesn't account for MARC8 text
            conv_record = p.to_html(result.data)
        else:
            raise 
        out.append(conv_record)
    conn.close()
    return ''.join(out)

class search:
    """web.py class for submitting a Z39.50 query and returning results"""
    def GET(self, query_string):
        print render.base(server=SERVER)
        results = run_query(SERVER, query_string)
        print render.search(query_string=query_string,
                                                results=results,
                                                total=len(results))

    def POST(self):
        i = web.input()
        query_string = i.query_string
        print render.base(server=SERVER)
        results = run_query(SERVER, query_string)
        print render.search(query_string=query_string,
                                                results=results,
                                                total=len(results))

class marcxml:
    """web.py class for submitting a Z39.50 query and returning results"""
    def GET(self, query_string):
        xml = run_query(SERVER, query_string)
        if xml != '':
            xml = '<?xml version="1.0" encoding="UTF-8"?><collection xmlns="http://www.loc.gov/MARC21/slim" xsi:schemaLocation="http://www.loc.gov/MARC21/slim http://www.loc.gov/standards/marcxml/schema/MARC21slim.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">%s</collection>' % xml
            web.header('Content-Type', 'application/xml')
            print render.marcxml(xml=xml)
        else:
            web.notfound()

class mods:
    def GET(self, query_string):
        xml = run_query(SERVER, query_string)
        if xml != '':
            xml = '<?xml version="1.0" encoding="UTF-8"?><collection xmlns="http://www.loc.gov/MARC21/slim" xsi:schemaLocation="http://www.loc.gov/MARC21/slim http://www.loc.gov/standards/marcxml/schema/MARC21slim.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">%s</collection>' % xml
            xml = InputSource.DefaultFactory.fromString(xml)
            processor = Processor()
            processor.appendStylesheet(MODS_XSLT)
            web.header('Content-Type', 'application/xml')
            print render.marcxml(processor.run(xml))
        else:
            web.notfound()

class usage:
    """web.py class to display usage information"""
    def GET(self):
        print render.base(server=SERVER)
        print render.usage()
        
web.webapi.internalerror = web.debugerror

def runfcgi_apache(func):
    web.wsgi.runfcgi(func, None)

if __name__ == '__main__':
    #web.wsgi.runwsgi = lambda func, addr=None: web.wsgi.runfcgi(func, addr)
    #web.wsgi.runwsgi = runfcgi_apache
    web.run(urls, globals())

