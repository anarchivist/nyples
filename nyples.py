#!/usr/bin/env PYTHONPATH=/home/matienzo/lib/python2.4/site-packages python2.4
"""
nyples.py
"""

import pymarc
import web
from Ft.Xml import InputSource
from Ft.Xml.Xslt.Processor import Processor
from Ft.Lib import UriException
from PyZ3950 import zoom
import urllib2

urls = ('/', 'usage',
        '/opac/(.*)', 'opac',
        '/marc/(.*)', 'marc',
        '/marcxml/(.*)', 'marcxml',
        '/mods/(.*)', 'mods',
        '/oai_dc/(.*)', 'oai_dc',
        '/rdf_dc/(.*)', 'rdf_dc')

CATNYP_SERVER = {'host': 'catnyp.nypl.org',
                'port': 210,
                'db': 'INNOPAC',
                'qsyntax': 'PQF',
                'rsyntax': 'USMARC',
                'element_set': 'F'}
LEO_SERVER   =  {'host': 'leo.nypl.org',
                'port': 210,
                'db': 'dynix',
                'qsyntax': 'PQF',
                'rsyntax': 'USMARC',
                'element_set': 'F'}
BASE_QUERY = '@attr 1=12 '
XSLT_URIS = {'mods': 'http://www.loc.gov/standards/mods/v3/MARC21slim2MODS3-2.xsl',
             'oai_dc': 'http://www.loc.gov/standards/marcxml/xslt/MARC21slim2OAIDC.xsl',
             'rdf_dc': 'http://www.loc.gov/standards/marcxml/xslt/MARC21slim2RDFDC.xsl'}
render = web.template.render('templates/')

def run_query(server, qs):
    """Creates Z39.50 connection, sends query, parses results"""
    conn = zoom.Connection(server['host'],
                            server['port'],
                            databaseName=server['db'],
                            preferredRecordSyntax=server['rsyntax'],
                            elementSetName=server['element_set'])
    out = []
    query = zoom.Query(server['qsyntax'], '%s%s' % (BASE_QUERY, qs))
    result_set = conn.search(query)
    for r in result_set:
        out.append(r)
    conn.close()
    return out

class marc:
    """ base class necessary for all other URI calls """
    def GET(self, query_string):
        if query_string[0] == 'b':
            server = CATNYP_SERVER
        elif query_string[0] == 'l':
            server = LEO_SERVER
        query_string = query_string[1:]
        try:
            r = run_query(server, query_string)
            if len(r) == 0:
                web.notfound()
            else:
                marc = pymarc.Record(data=r[0].data).as_marc21()
                if marc != '':
                    web.header('Content-Type', 'application/marc')
                    print marc
                else:
                    web.notfound()
        except:
            raise

class marcxml:
    """ necessary for mods class """
    def GET(self, query_string):
        try:
            marc = urllib2.urlopen('http://localhost:8080/marc/%s' % query_string).read()
            xml = pymarc.record_to_xml(pymarc.Record(data=marc))    
            if xml != '':
                xml = '<?xml version="1.0" encoding="UTF-8"?><collection xmlns="http://www.loc.gov/MARC21/slim" xsi:schemaLocation="http://www.loc.gov/MARC21/slim http://www.loc.gov/standards/marcxml/schema/MARC21slim.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">%s</collection>' % xml
                web.header('Content-Type', 'application/xml')
                print xml
            else:
                web.notfound()
        except urllib2.HTTPError, e:
            if e.code == 404:
                web.notfound()
            else:
                raise
        except:
            raise
    
class mods:
    def GET(self, query_string):
        try: 
            xml = urllib2.urlopen('http://localhost:8080/marcxml/%s' % query_string).read()
            xml = InputSource.DefaultFactory.fromString(xml)
            xslt = InputSource.DefaultFactory.fromUri(XSLT_URIS['mods'])
            processor = Processor()
            processor.appendStylesheet(xslt)
            web.header('Content-Type', 'application/xml')
            print processor.run(xml)
        except urllib2.HTTPError, e:
            if e.code == 404:
                web.notfound()
            else:
                raise
                
class oai_dc:
    def GET(self, query_string):
        try: 
            xml = urllib2.urlopen('http://localhost:8080/marcxml/%s' % query_string).read()
            xml = InputSource.DefaultFactory.fromString(xml)
            xslt = InputSource.DefaultFactory.fromUri(XSLT_URIS['oai_dc'])
            processor = Processor()
            processor.appendStylesheet(xslt)
            web.header('Content-Type', 'application/xml')
            print processor.run(xml)
        except urllib2.HTTPError, e:
            if e.code == 404:
                web.notfound()
            else:
                raise

class opac:
    def GET(self, query_string):
        if query_string[0] == 'b':
            opac_url = 'http://catnyp.nypl.org/record=%s' % query_string
        elif query_string[0] == 'l':
            opac_url = 'http://leopac.nypl.org/ipac20/ipac.jsp?uri=full=1100001~!%s~!1' % query_string[1:]
        else:
            raise web.badrequest()
        web.seeother(opac_url)
        
class rdf_dc:
    def GET(self, query_string):
        try: 
            xml = urllib2.urlopen('http://localhost:8080/marcxml/%s' % query_string).read()
            xml = InputSource.DefaultFactory.fromString(xml)
            xslt = InputSource.DefaultFactory.fromUri(XSLT_URIS['rdf_dc'])
            processor = Processor()
            processor.appendStylesheet(xslt)
            web.header('Content-Type', 'application/xml')
            print processor.run(xml)
        except urllib2.HTTPError, e:
            if e.code == 404:
                web.notfound()
            else:
                raise

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
    web.run(urls, globals(), web.reloader)

