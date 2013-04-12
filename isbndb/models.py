
class Model(object):
    
    def __init__(self, xml):
        self.raw_data = xml

    def __str__(self):
        return self.raw_data.toprettyxml( )

    def _get_attribute(self, attr):
        val = self.raw_data.getAttribute(attr)
        if val == '':
            return None
        return val

    def _get_element(self, name):
        nodes = self.raw_data.getElementsByTagName(name)
        if len(nodes) == 0:
            return None
        if len(nodes) > 1:
            raise AttributeError("Too many elements with name %s" % name)

        return nodes[0]

    def _get_childNodes(self, name):
        return self._get_element(name).childNodes if self._get_element(name) else []

    def _get_nodeValue(self, node):
        if isinstance(node, str):
            nodes = self._get_childNodes(node)
        elif hasattr(node, 'childNodes'):
            nodes = node.childNodes
        else:
            return None

        if len(nodes) == 0:
            return None
        if len(nodes) > 1:
            raise AttributeError("Unable to parse value from node with name %s" % name)
        
        return nodes[0].nodeValue

class Book(Model):

    @property
    def book_id(self):
        return self._get_attribute('book_id')

    @property
    def isbn(self):
        return self._get_attribute('isbn')

    @property
    def isbn13(self):
        return self._get_attribute('isbn13')

    @property
    def title(self):
        return self._get_nodeValue('Title')

    @property
    def title_long(self):
        return self._get_nodeValue('TitleLong')

    @property
    def authors_text(self):
        return self._get_nodeValue('AuthorsText')

    @property
    def authors(self):
        for node in self._get_childNodes('Authors'):
            if node.nodeType == node.ELEMENT_NODE:
                aid  = node.getAttribute('person_id')
                name = self._get_nodeValue(node)
                yield {
                    'person_id':   aid,
                    'person_text': name,
                }

    @property
    def publisher_id(self):
        pelem = self._get_element('PublisherText')
        if pelem is not None:
            val = pelem.getAttribute('publisher_id')
            if val != '':
                return val
        return None

    @property
    def publisher_text(self):
        return self._get_nodeValue('PublisherText')

    @property
    def details(self):
        delem = self._get_element('Details')
        if delem is not None:
            return dict(delem.attributes.items())
        return None

    @property
    def summary(self):
        return self._get_nodeValue('Summary')

    @property
    def notes(self):
        return self._get_nodeValue('Notes')

    @property
    def urls_text(self):
        return self._get_nodeValue('UrlsText')

    @property
    def awards_text(self):
        return self._get_nodeValue('AwardsText')

    @property
    def prices(self):
        for node in self._get_childNodes('Prices'):
            if node.nodeType == node.ELEMENT_NODE:
                yield dict(node.attributes.items())

    @property 
    def subjects(self):
        for node in self._get_childNodes('Subjects'):
            if node.nodeType == node.ELEMENT_NODE:
                sid  = node.getAttribute('subject_id')
                text = self._get_nodeValue(node)
                yield {
                    'subject_id':   sid,
                    'subject_text': text,
                }

    @property
    def marc_records(self):
        for node in self._get_childNodes('MARCRecords'):
            if node.nodeType == node.ELEMENT_NODE:
                yield dict(node.attributes.items())

class Subject(Model):

    @property
    def subject_id(self):
        return self._get_attribute('subject_id')

    @property
    def book_count(self):
        return self._get_attribute('book_count')

    @property
    def marc_field(self):
        return self._get_attribute('marc_field')

    @property
    def marc_indicators(self):
        return (self._get_attribute('marc_indicator_1'),
                self._get_attribute('marc_indicator_2'))

    @property
    def name(self):
        return self._get_nodeValue('Name')

    @property 
    def categories(self):
        for node in self._get_childNodes('Categories'):
            if node.nodeType == node.ELEMENT_NODE:
                cid  = node.getAttribute('category_id')
                text = self._get_nodeValue(node)
                yield {
                    'category_id':   cid,
                    'category_text': text,
                }

    @property
    def structure(self):
        for node in self._get_childNodes('SubjectStructure'):
            if node.nodeType == node.ELEMENT_NODE:
                yield dict(node.attributes.items())

class Category(Model):
    
    @property
    def category_id(self):
        return self._get_attribute('category_id')

    @property
    def parent_id(self):
        return self._get_attribute('parent_id')

    @property
    def name(self):
        return self._get_nodeValue('Name')

    @property
    def details(self):
        delem = self._get_element('Details')
        if delem:
            return dict(delem.attributes.items())
        return {}

    @property
    def subcategories(self):
        for node in self._get_childNodes('SubCategories'):
            if node.nodeType == node.ELEMENT_NODE:
                yield dict(node.attributes.items())

class Author(Model):

    @property 
    def author_id(self):
        return self._get_attribute('person_id')
    
    @property
    def name(self):
        return self._get_nodeValue('Name')

    @property 
    def details(self):
        delem = self._get_element('Details')
        if delem:
            return dict(delem.attributes.items())
        return None

    @property 
    def categories(self):
        for node in self._get_childNodes('Categories'):
            if node.nodeType == node.ELEMENT_NODE:
                cid  = node.getAttribute('category_id')
                text = self._get_nodeValue(node)
                yield {
                    'category_id':   cid,
                    'category_text': text,
                }

    @property
    def subjects(self):
        for node in self._get_childNodes('Subjects'):
            if node.nodeType == node.ELEMENT_NODE:
                sid   = node.getAttribute('subject_id')
                count = node.getAttribute('book_count')
                text  = self._get_nodeValue(node)
                yield {
                    'subject_id':   sid,
                    'book_count':   count,
                    'subject_text': text,
                }

class Publisher(Model):

    @property
    def publisher_id(self):
        return self._get_attribute('publisher_id')

    @property
    def name(self):
        return self._get_nodeValue('Name')

    @property
    def details(self):
        delem = self._get_element('Details')
        if delem:
            return dict(delem.attributes.items())
        return None

    @property
    def categories(self):
        for node in self._get_childNodes('Categories'):
            if node.nodeType == node.ELEMENT_NODE:
                cid  = node.getAttribute('category_id')
                text = self._get_nodeValue(node)
                yield {
                    'category_id':   cid,
                    'category_text': text,
                }
