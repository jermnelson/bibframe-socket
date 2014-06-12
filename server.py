#-------------------------------------------------------------------------------
# Name:        server
# Purpose:     This module creates a socket server using jython for transforming
#              MARC xml to BIBFRAME RDF using the Saxon jquery engine and the
#              XQuery script from https://github.com/lcnetdev/marc2bibframe/
#
# Author:      Jeremy Nelson
#
# Created:     2014/05/22
# Copyright:   (c) Jeremy Nelson, Colorado College 2014
# Licence:     MIT
#-------------------------------------------------------------------------------
import argparse
import datetime
import json
import os
import SocketServer
import sys
import tempfile
import urllib



for filename in os.listdir("./lib"):
    if os.path.splitext(filename)[-1].endswith(".jar"):
        sys.path.append(os.path.join("lib",filename))

from java.io import File, ByteArrayInputStream, ByteArrayOutputStream
from java.io import FileInputStream, FileOutputStream, PrintStream, StringReader
from java.lang import System
from java.net import URI
from java.util import Properties
from javax.xml.parsers import DocumentBuilderFactory
from javax.xml.transform.stream import StreamResult, StreamSource
from javax.xml.transform.sax import SAXSource
from net.sf import saxon
from org.xml.sax import InputSource
from StringIO import StringIO
from tempfile import NamedTemporaryFile

INFO = json.load(open('server.json'))
COMPLIED_XQUERY, CONFIG = None, None

def setup():
    global COMPLIED_XQUERY, CONFIG
    CONFIG = saxon.Configuration()
    context = CONFIG.newStaticQueryContext()
##    props = Properties()
##    props.setProperty()
    saxon_xqy_file = FileInputStream(INFO.get('saxon_xqy'))
    context.setBaseURI(
        File(INFO.get('saxon_xqy')).toURI().toString())
    COMPLIED_XQUERY = context.compileQuery(saxon_xqy_file, None)


class Marc2BibframeTCPHandler(SocketServer.StreamRequestHandler):
    """Socket server accepts raw xml, runs Library of Congress MARC XML to
    BIBFRAME xquery and returns the resulting RDF/XML graph

    >> server = SocketServer.TCPServer(('localhost', 8089))
    >> server.serve_forever()
    """

    def alt_handle(self):
        try:
            raw_xml = self.rfile.readline().strip()
            marc_xmlfile = NamedTemporaryFile(delete=False)
            marc_xmlfile.write(raw_xml)
            marc_xmlfile.close()
            base_uri =  INFO.get('base_uri','http://catalog/')
            args = [INFO.get('saxon_xqy'),
                    'marcxmluri={}'.format(
                    os.path.normpath(marc_xmlfile.name).replace("\\", "/")),
                    'baseuri={}'.format(INFO.get('base_uri',
                                        'http://catalog/')),
                    'serialization=rdfxml']
            query = saxon.Query()
            output_stream = ByteArrayOutputStream()
            System.setOut(PrintStream(output_stream))
            query.main(args)
            self.wfile.write(output_stream.toString().encode('ascii',
                                                         errors='ignore'))
            os.remove(marc_xmlfile.name)
        except:
            self.wfile.write("Error processing MARC XML:\n\t{}".format(sys.exc_info()[0]))

    def handle(self):
        try:
            raw_xml = self.rfile.readline().strip()
            marc_xmlfile = NamedTemporaryFile(delete=False)
            marc_xmlfile.write(raw_xml)
            marc_xmlfile.close()
            dynamic_context = saxon.query.DynamicQueryContext(CONFIG)
##            xml_doc = CONFIG.buildDocument(
##                StreamSource(ByteArrayInputStream(raw_xml)))
##            dynamic_context.setContextItem(xml_doc)
            dynamic_context.setParameter(
                "baseuri",
                INFO.get('base_uri', 'http://catalog/'))

            dynamic_context.setParameter(
                "marcxmluri",
                os.path.normpath(marc_xmlfile.name).replace("\\", "/"))
            dynamic_context.setParameter("serialization", "rdfxml")
            output_stream = ByteArrayOutputStream()
            result = StreamResult(output_stream)
            COMPLIED_XQUERY.run(dynamic_context, result, None)
            self.wfile.write(output_stream.toString().encode('ascii',
                                                         errors='ignore'))
            os.remove(marc_xmlfile.name)
        except:
             self.wfile.write("Error processing MARC XML:\n\t{}".format(sys.exc_info()[0]))


def main(args):
    # Run as a socket server
    try:
        server = SocketServer.TCPServer(
            (args.host, args.port),
            Marc2BibframeTCPHandler)
        print("Running xquery server at {}:{}\nkill java process to stop".format(
            args.host,
            args.port))
        server.serve_forever()
    except:
        print("Exception {} ".format(sys.exc_info()))
        main(args)
##

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('host',
                         help='Host for xquery server',
                         default='localhost')
    parser.add_argument('port',
                        type=int,
                        help='Port for xquery server',
                        default=8089)
    args = parser.parse_args()
    setup()
    # setup query processor
    main(args)

