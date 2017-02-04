from google.appengine.ext import ndb
from google.appengine.api import urlfetch
import webapp2
import json
import re

class Home(webapp2.RequestHandler):
    def get(self):
        self.response.write('CS496 - REST Implementation - Author: Peter Nguyen')

    def delete(self):
        # Delete all Datastore entries
        listOfBookKeys = Book.query().fetch(keys_only=True)
        listOfCustomerKeys = Customer.query().fetch(keys_only=True)
        ndb.delete_multi(listOfBookKeys)
        ndb.delete_multi(listOfCustomerKeys)
        self.response.write("All entries successfully delted.")

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
        bookDict['self'] = '/books/' + str(newBook.key.id())
        self.response.write(json.dumps(bookDict))

    def get(self, bookId=None, queryString=None):
        if bookId:
            bookObj = Book.get_by_id(int(bookId))
            bookObjDict = bookObj.to_dict()
            bookObjDict['id'] = bookObj.key.id()
            bookObjDict['self'] = "/books/" + bookId
            self.response.write(json.dumps(bookObjDict))
        # Check for a query string value
        qStrVal = self.request.get('checkedIn')
        checkedOutList = []
        if qStrVal:
            if qStrVal == "true":
                query = Book.query(Book.checkedIn == True)
                for result in query.fetch():
                    checkedOutList.append(result.to_dict())
            elif qStrVal == "false":
                query = Book.query(Book.checkedIn == False)
                for result in query.fetch():
                    checkedOutList.append(result.to_dict())
            self.response.write(checkedOutList)

    def delete(self, bookId=None):
        if bookId:
            bookObj = Book.get_by_id(int(bookId))
            bookObj.key.delete()
            self.response.write(bookObj.title + " has been deleted.")

    def patch(self, bookId=None):
        if bookId:
            bookObj = Book.get_by_id(int(bookId))
            bookData = json.loads(self.request.body)
            # patch attribute values for bookObj
            for bKey, bValue in bookData.iteritems():
                setattr(bookObj, bKey, bValue)
            bookObj.put()
            bookDict = bookObj.to_dict()
            bookDict['self'] = '/books/' + str(bookObj.key.id())
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
        customerDict['self'] = '/customers/' + str(newCustomer.key.id())
        self.response.write(json.dumps(customerDict))

    def get(self, customerId=None):
        if customerId:
            customerObj = Customer.get_by_id(int(customerId))
            customerObjDict = customerObj.to_dict()
            customerObjDict['id'] = customerObj.key.id()
            customerObjDict['self'] = "/customers/" + customerId
            self.response.write(json.dumps(customerObjDict))

    def delete(self, customerId=None):
        if customerId:
            customerObj = Customer.get_by_id(int(customerId))
            customerObj.key.delete()
            self.response.write(customerObj.name + " has been deleted.")

    def patch(self, customerId=None):
        if customerId:
            customerObj = Customer.get_by_id(int(customerId))
            customerData = json.loads(self.request.body)
            # patch attribute values for customerObj
            for cKey, cValue in customerData.iteritems():
                setattr(customerObj, cKey, cValue)
            customerObj.put()
            customerDict = customerObj.to_dict()
            customerDict['self'] = '/customers/' + str(customerObj.key.id())
            self.response.write(json.dumps(customerDict))

class CustomerBooksHandler(webapp2.RequestHandler):
    def get(self, customerId=None):
        if customerId:
            customerObj = Customer.get_by_id(int(customerId))
            bookList = []
            booksCheckedOut = customerObj.checked_out
            # Fetch book links from checked_out list
            for book in booksCheckedOut:
                url = "http://localhost:8080" + book
                result = urlfetch.fetch(url)
                if result.status_code == 200:
                    bookList.append(result.content)
                else:
                    self.response.status_code = result.status_code
            self.response.write(bookList)

class CheckoutHandler(webapp2.RequestHandler):
    def put(self, customerId=None, bookId=None):
        if customerId and bookId:
            customerObj = Customer.get_by_id(int(customerId))
            bookObj = Book.get_by_id(int(bookId))
            # Add checked out book to customer's list
            customerObj.checked_out.append("/books/" + str(bookId))
            customerObj.put()
            #Set book status to checked out
            bookObj.checkedIn = False
            bookObj.put()
            self.response.write(json.dumps(customerObj.to_dict()))
            self.response.write(bookObj.to_dict())

    def delete(self, customerId=None, bookId=None):
        if customerId and bookId:
            customerObj = Customer.get_by_id(int(customerId))
            bookObj = Book.get_by_id(int(bookId))
            # Remove checked out book from customer's list
            customerObj.checked_out.remove("/books/" + str(bookId))
            customerObj.put()
            #Set book status to checked in
            bookObj.checkedIn = True
            bookObj.put()
            self.response.write(customerObj.to_dict())
            self.response.write(bookObj.to_dict())

# Allow patch operations
allowed_methods = webapp2.WSGIApplication.allowed_methods
new_allowed_methods = allowed_methods.union(('PATCH',))
webapp2.WSGIApplication.allowed_methods = new_allowed_methods

app = webapp2.WSGIApplication([
    ('/', Home),

    ('/books', BookHandler),

    webapp2.Route(r'/books/<bookId:\d+>', handler=BookHandler),

    webapp2.Route(r'/books<queryString:\s+>', handler=BookHandler),

    ('/customers', CustomerHandler),

    webapp2.Route(r'/customers/<customerId:\d+>', handler=CustomerHandler),

    webapp2.Route(r'/customers/<customerId:\d+>/books', handler=CustomerBooksHandler),

    webapp2.Route(r'/customers/<customerId:\d+>/books/<bookId:\d+>', handler=CheckoutHandler),
], debug=True)
