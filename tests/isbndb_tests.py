#!/usr/bin/env python

from isbndb import ISBNdbException
from isbndb.models  import *
from isbndb.client  import ISBNdbClient
from isbndb.catalog import *
from unittest import TestCase

ACCESS_KEY = "UQ8OR4XB"

class ISBNdbTest(TestCase):
    
    def setup(self):
        self.client = ISBNdbClient( access_key=ACCESS_KEY )

    def teardown(self):
        pass

    def test_connection(self):
        catalog = BookCollection(self.client)
        result  = catalog.isbn('0210406240', results='authors')


if __name__ == "__main__":

    from unittest import main
    main( )
