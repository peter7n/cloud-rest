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
        # newBook = Book(title=bookData['title'], isbn=bookData['isbn'], genre=bookData['genre'], author=bookData['author'], checkedIn=bookData['checkedIn'])
        newBook = Book(title=bookData['title'])
        # newBook.populate(isbn=bookData['isbn'], genre=bookData['genre'], author=bookData['author'], checkedIn=bookData['checkedIn'])
        for bKey, bValue in bookData.iteritems():
            setattr(newBook, bKey, bValue)
        newBook.put()
        bookDict = newBook.to_dict()
        bookDict['self'] = '/book/' + newBook.key.urlsafe()
        self.response.write(json.dumps(bookDict))

    def get(self, id=None):
        if id:
            bookGet = ndb.Key(urlsafe=id).get()
            bookGetDict = bookGet.to_dict()
            bookGetDict['self'] = "/book/" + id
            self.response.write(json.dumps(bookGetDict))

app = webapp2.WSGIApplication([
    ('/', HelloWebapp2),
    ('/book', BookHandler),
    ('/book/(.*)', BookHandler),
], debug=True)
