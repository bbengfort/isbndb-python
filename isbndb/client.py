#!/usr/bin/env python

import os
from urllib import urlencode
from httplib import HTTPConnection
from xml.dom.minidom import parse
from isbndb import ISBNdbException
from isbndb import ISBNdbHttpException
from isbndb.catalog import *

def find_credentials( ):
    """
    Look in the current environment for the ISBNdb Access credentials

    @todo: add additional credentials as necessary
    """
    try:
        access_key = os.environ["ISBNDB_ACCESS_KEY"]
        return access_key
    except KeyError:
        return None

class ISBNdbClient(object):
    """
    A client for accessing the ISBNdb API
    """

    def __init__(self, access_key=None, host="isbndb.com", 
                 base="/api/", client=None):
        """
        Create an ISBNdb API client
        """

        # Get account credentials (for now, just the access key)
        if not access_key:
            access_key = find_credentials( )
            if not access_key:
                raise ISBNdbException("""
 ISBNdb could not find your access key (account credentials). Pass them
 into the ISBNdbClient constructor like this:
 
    client = ISBNdbClient(access_key="ABCDEFGH")

 Or, add your credentials to your shell environment. From the terminal, run

    echo "export ISBNDB_ACCESS_KEY=ABCDEFGH" >> ~/.bashrc

 and be sure to replace the values for the access_key with the values from 
 your isbndb.com account. 
 """)

        self.host = host
        self.base = base
        self.auth = access_key

        # Add collections
        self.books      = BookCollection(self)
        self.subjects   = SubjectCollection(self)
        self.categories = CategoryCollection(self)
        self.authors    = AuthorCollection(self)
        self.publishers = PublisherCollection(self)

    def request(self, path, method=None, params=None, debug=False, stats=False):
        """
        Sends a request and gets a response from isbndb.com

        @param: method should be in (GET, POST, DELETE, or PUT)
        @param: params should be a dictionary of options to send to server
        @param: debug if true, reports the arguments that you sent to the server
        @param: stats if true, reports the statistics of the key in use.
        """
        
        params = params or { }
        params['access_key'] = self.auth
        if debug:
            params['results'] = 'args'
        if stats:
            params['results'] = 'keystats'
        params = urlencode(params)
        query  = None
        data   = None

        if not path or len(path) < 1:
            raise ValueError('Invalid path parameter')
        if method and method not in ['GET', 'POST', 'DELETE', 'PUT']:
            raise NotImplementedError('HTTP %s method not implemented' % method)

        if path[0] == '/':
            uri = self.base
        else:
            uri = self.base + path

        if method == "GET":
            query = params
        elif method == "POST" or method == "PUT":
            data = params

        headers = {
            "User-Agent":"ISBNdb-Python",
        }

        conn = HTTPConnection(self.host)

        if query:
            conn.request(method, '?'.join([uri, query]), '', headers)
        elif data:
            conn.request(method, uri, data, headers)

        response = conn.getresponse( )

        if response.status != 200:
            raise ISBNdbHttpException(response.status, uri, response.reason)
        else:
            return parse(response)

    def keystats(self):
        """
        Returns the statistics of the key you're using
        """
        return self.request('books.xml', method="GET", stats=True)

if __name__=="__main__":

    client = ISBNdbClient( access_key="UQ8OR4XB" )
    params = {
        'results':'detail',
        'index1': 'keywords',
        'value1': 'lord of the flies'
    }
#    print client.request('books.xml', method="GET", params=params).toprettyxml( )
    print client.keystats( ).toprettyxml( )
