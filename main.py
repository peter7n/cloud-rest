from google.appengine.ext import ndb
import webapp2
import json
import re

class HelloWebapp2(webapp2.RequestHandler):
    def get(self):
        self.response.write('Hello, webapp2!')

class Book(ndb.Model):
    title = ndb.StringProperty(required=True)
    isbn = ndb.IntegerProperty()
    genre = ndb.StringProperty(repeated=True)
    author = ndb.StringProperty()
    checkedIn = ndb.BooleanProperty()

class Customer(ndb.Model):
    name = ndb.StringProperty(required=True)
    balance = ndb.FloatProperty()
    checked_out = ndb.StringProperty(repeated=True)

class BookHandler(webapp2.RequestHandler):
    def post(self):
        bookData = json.loads(self.request.body)
        newBook = Book(title=bookData['title'])
        # propagate values for newBook
        for bKey, bValue in bookData.iteritems():
            setattr(newBook, bKey, bValue)
        newBook.put()
        bookDict = newBook.to_dict()
        bookDict['self'] = '/books/' + newBook.key.urlsafe()
        self.response.write(json.dumps(bookDict))

    def get(self, keyParam=None):
        if keyParam:
            bookRetrieve = ndb.Key(urlsafe=keyParam).get()
            bookRetrieveDict = bookRetrieve.to_dict()
            bookRetrieveDict['id'] = bookRetrieve.key.id()
            bookRetrieveDict['self'] = "/books/" + keyParam
            self.response.write(json.dumps(bookRetrieveDict))

    def delete(self, idParam=None):
        if idParam:
            bookObj = Book.get_by_id(int(idParam))
            bookObj.key.delete()
            self.response.write("entity deleted")

    def patch(self, idParam=None):
        if idParam:
            bookObj = Book.get_by_id(int(idParam))
            bookData = json.loads(self.request.body)
            # patch attribute values for bookObj
            for bKey, bValue in bookData.iteritems():
                setattr(bookObj, bKey, bValue)
            bookObj.put()
            bookDict = bookObj.to_dict()
            bookDict['self'] = '/books/' + bookObj.key.urlsafe()
            self.response.write(json.dumps(bookDict))

class CustomerHandler(webapp2.RequestHandler):
    def post(self):
        customerData = json.loads(self.request.body)
        newCustomer = Customer(name=customerData['name'])
        # propagate values for newCustomer
        for cKey, cValue in customerData.iteritems():
            setattr(newCustomer, cKey, cValue)
        newCustomer.put()
        customerDict = newCustomer.to_dict()
        customerDict['self'] = '/customers/' + newCustomer.key.urlsafe()
        self.response.write(json.dumps(customerDict))

    def get(self, keyParam=None):
        if keyParam:
            customerRetrieve = ndb.Key(urlsafe=keyParam).get()
            customerRetrieveDict = customerRetrieve.to_dict()
            customerRetrieveDict['id'] = customerRetrieve.key.id()
            customerRetrieveDict['self'] = "/customers/" + keyParam
            self.response.write(json.dumps(customerRetrieveDict))

    def delete(self, idParam=None):
        if idParam:
            customerObj = Customer.get_by_id(int(idParam))
            customerObj.key.delete()
            self.response.write("entity deleted")

    def patch(self, idParam=None):
        if idParam:
            customerObj = Customer.get_by_id(int(idParam))
            customerData = json.loads(self.request.body)
            # patch attribute values for customerObj
            for cKey, cValue in customerData.iteritems():
                setattr(customerObj, cKey, cValue)
            customerObj.put()
            customerDict = customerObj.to_dict()
            customerDict['self'] = '/customers/' + customerObj.key.urlsafe()
            self.response.write(json.dumps(customerDict))

class CustomerBooksHandler(webapp2.RequestHandler):
    def get(self, customerId=None):
        if customerId:
            self.response.write("success! ")
            self.response.write(customerId)

# Allow patch operations
allowed_methods = webapp2.WSGIApplication.allowed_methods
new_allowed_methods = allowed_methods.union(('PATCH',))
webapp2.WSGIApplication.allowed_methods = new_allowed_methods

app = webapp2.WSGIApplication([
    ('/', HelloWebapp2),
    ('/book', BookHandler),
    ('/books/(.*)', BookHandler),
    ('/customer', CustomerHandler),
    (r'/customers/(\d+)', CustomerHandler),
    webapp2.Route(r'/customers/<customerId:\d+>/books', handler=CustomerBooksHandler, name='customer-books'),
], debug=True)
