from google.appengine.ext import ndb
import webapp2
import json

class HelloWebapp2(webapp2.RequestHandler):
    def get(self):
        self.response.write('Hello, webapp2!')

class Book(ndb.Model):
    title = ndb.StringProperty(required=True)
    isbn = ndb.IntegerProperty()
    genre = ndb.StringProperty(repeated=True)
    author = ndb.StringProperty()
    checkedIn = ndb.BooleanProperty()

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
            # self.response.write(keyParam)

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

allowed_methods = webapp2.WSGIApplication.allowed_methods
new_allowed_methods = allowed_methods.union(('PATCH',))
webapp2.WSGIApplication.allowed_methods = new_allowed_methods

app = webapp2.WSGIApplication([
    ('/', HelloWebapp2),
    ('/book', BookHandler),
    ('/books/(.*)', BookHandler),
], debug=True)
