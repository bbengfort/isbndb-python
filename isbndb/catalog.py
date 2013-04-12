from models import *
from isbndb import ISBNdbException
from dateutil.parser import parse as isodateparse

class ResultSet(object):
    
    def __init__(self, xml, lroot, model):
        self.xml   = xml
        self.lroot = lroot
        self.model = model

    def __len__(self):
        if not hasattr(self, '_cached_length'):
            self._cached_length = int(self.result_list.getAttribute('total_results'))
        return self._cached_length

    def __iter__(self):
        for elem in self.result_list.childNodes:
            if elem.nodeType == elem.ELEMENT_NODE:
                yield self.model(elem)

    def __getitem__(self, index):
        if index < 0:
            raise IndexError("negative indexing not supported on ResultSet")

        i = 0
        for elem in self.result_list.childNodes:
            if elem.nodeType == elem.ELEMENT_NODE:
                if i == index:
                    return self.model(elem)
                else:
                    i += 1
        raise IndexError("list index is out of range (use next to fetch more results)")

    @property
    def last_access(self):
         tstr = self.xml.documentElement.getAttribute('server_time')
         return isodateparse(tstr)

    @property
    def result_list(self):
        if not hasattr(self, '_cached_result_list'):
            rlist = self.xml.getElementsByTagName(self.lroot)
            if len(rlist) > 1:
                raise ISBNdbException('Unexpected XML data returned')
            self._cached_result_list = rlist[0]
        return self._cached_result_list

    @property
    def current_page(self):
        return int(self.result_list.getAttribute('page_number'))

    @property
    def page_size(self):
        return int(self.result_list.getAttribute('page_size'))

    @property
    def shown_results(self):
        return int(self.result_list.getAttribute('shown_results'))

class Collection(object):
    
    path         = None
    model_class  = None
    list_element = None
    result_types = None

    def __init__(self, client=None, results=None):
        if self.path is None:
            raise NotImplementedError("Must specify a path in collection subclasses.")
        if self.result_types is None:
            raise NotImplementedError("Must specify a list of result types for the subclass.")

        self.client  = client
        self.results = results or self.result_types[0]

    def set_results(self, results):
        if results in self.result_types:
            self.results = results
        else:
            raise ISBNdbException("%s is not a recognized results set." % results)

    def lookup(self, index, value, **kwargs):
        
        results  = kwargs.pop('results', self.results)
        params   = self.get_request_params(results, [(index, value)])
        response = self.request(params=params, **kwargs)
        if self.model_class is not None:
            return ResultSet(response, self.list_element, self.model_class)
        else:
            return response

    def request(self, **kwargs):
        """
        Crafts a request from defaults for a collection by the client property 
        on the collection, or else the passed in client to the request.
        """
        
        client = kwargs.get('client', None) or self.client
        if not client:
            raise ISBNdbException("Cannot make a request without a client")

        method = kwargs.get('method', 'GET')
        params = kwargs.get('params', None) 
        debug  = kwargs.get('debug', False)
        stats  = kwargs.get('stats', False)

        return client.request(self.path, method, params, debug, stats)

    def get_request_params(self, results="details",
                           options=[('index', 'value')]):
        """
        Creates an request paramater dictionary from a list of
        tuples that contain index, value tuples or 3-tuples,
        along with the results format requested.

        E.g. ('isbn', '0061041321') is to lookup that isbn. 

        It returns an ordered dictionary of indicies and parameters
        """
        params = {'results':results}
        for i, option in enumerate(options):
            i += 1
            index, value = 'index'+str(i), 'value'+str(i)
            params[index] = option[0]
            params[value] = option[1]
        return params

class BookCollection(Collection):
    """
    Enumerates the lookup methods for the Book Collection.
    """

    path         = "books.xml"
    model_class  = Book
    list_element = "BookList"
    result_types = ('details', 'texts', 'prices', 'pricehistory', 'subjects', 'authors', 'marc')

    def __init__(self, client=None, results='authors'):
        super(BookCollection, self).__init__(client, results)

    def isbn(self, isbn, **kwargs):
        """
        Search on ISBN

        The returned results subset consists of zero or at most one member,
        ISBN records are unique in the database.
        """
        return self.lookup('isbn', isbn, **kwargs)

    def title(self, title, **kwargs):
        """
        Keywords search on book title, long title, and latinized title for unicode.

        The search follows the same rules and syntax as the search on the website
        itself. You can group words together using double quotes, all non-ignored
        words must be present in the results.
        """
        return self.lookup('title', title, **kwargs)

    def combined(self, term, **kwargs):
        """
        Search index that combines titles, authors, and publisher name

        This helps to answer queries "Title by John Doe" that many people seem to 
        type when search for a book. Another possibility is a generic title with 
        a publisher to look for series. 
        """
        return self.lookup('combined', term, **kwargs)

    def full(self, term, **kwargs):
        """
        Search index that includes titles, authors, publisher name, summary, notes
        awards information, etc. 
        """
        return self.lookup('full', term, **kwargs)

    def book_id(self, book_id, **kwargs):
        """
        Retreive a book by ISBNdb.com's book ID. 

        Returns at most one match.
        """
        return self.lookup('book_id', book_id, **kwargs)

    def person_id(self, person_id, **kwargs):
        """
        Retreives a list of books by the given author, editor, etc. The ID is the
        ID of a person in the 'Persons' collection
        """
        return self.lookup('person_id', person_id, **kwargs)

    def subject_id(self, subject_id, **kwargs):
        """
        Retrieves a list of books on the given subject from the 'Subjects' collection
        """
        return self.lookup('subject_id', subject_id, **kwargs)

    def dewey_decimal(self, dewey, **kwargs):
        """
        Retrieves a list of books by the given Dewey Decimal Classifcation number.
        """
        return self.lookup('dewey_decimal', dewey, **kwargs)

    def llc_number(self, llc, **kwargs):
        """
        Returns a list of books by the Library of Congress Classification number.
        """
        return self.lookup('llc_number', llc, **kwargs)


class SubjectCollection(Collection):

    path         = "subjects.xml"
    model_class  = Subject
    list_element = "SubjectList"
    result_types = ('categories', 'structure')

    def name(self, name, **kwargs):
        """
        Performs a search on subject name.
        """
        return self.lookup('name', name, **kwargs)

    def category_id(self, category_id, **kwargs):
        """
        Retrieves subjects listed by the given category by that category id.
        """
        return self.lookup('category_id', category_id, **kwargs)
        
    def subject_id(self, subject_id, **kwargs):
        """
        Retrieves subject data by ISBNdb.com's subject id. Returns at most one match.
        """
        return self.lookup('subject_id', subject_id, **kwargs)

class CategoryCollection(Collection):
    
    path         = "categories.xml"
    model_class  = Category
    list_element = "CategoryList"
    result_types = ('details', 'subcategories')

    def name(self, name, **kwargs):
        """
        Performs a search on category name.
        """
        return self.lookup('name', name, **kwargs)

    def category_id(self, category_id, **kwargs):
        """
        Retrieves category data by ISBNdb.com's category id. Returns at most one match.
        """
        return self.lookup('category_id', category_id, **kwargs)
        
    def parent_id(self, parent_id, **kwargs):
        """
        Retrieves a list of categories that are contained within the given category. 

        Supplying an empty category id gives you a list of top-level categories.
        """
        return self.lookup('parent_id', parent_id, **kwargs)

class AuthorCollection(Collection):
    
    path         = "authors.xml"
    model_class  = Author
    list_element = "AuthorList"
    result_types = ('details', 'categories', 'subjects')

    def name(self, name, **kwargs):
        """
        Performs a search on the author name
        """
        return self.lookup('name', name, **kwargs)

    def person_id(self, person_id, **kwargs):
        """
        Returns at most one author by ISBNdb.com's person ID
        """
        return self.lookup('person_id', person_id, **kwargs)

class PublisherCollection(Collection):
    
    path         = "publishers.xml"
    model_class  = Publisher
    list_element = "PublisherList"
    result_types = ('details', 'categories')

    def name(self, name, **kwargs):
        """
        Performs a search on the publisher name
        """
        return self.lookup('name', name, **kwargs)

    def publisher_id(self, publisher_id, **kwargs):
        """
        Returns at most one publisher by ISBNdb.com's publisher ID
        """
        return self.lookup('publisher_id', publisher_id, **kwargs)
