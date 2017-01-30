from google.appengine.ext import ndb
import webapp2
import json

class HelloWebapp2(webapp2.RequestHandler):
    def get(self):
        self.response.write('Hello, webapp2!')

class Fish(ndb.Model):
    name = ndb.StringProperty(required=True)
    ph_min = ndb.IntegerProperty()
    ph_max = ndb.IntegerProperty()

class FishHandler(webapp2.RequestHandler):
    def post(self):
        # Define parent or ancestor group
        parent_key = ndb.Key(Fish, "parent_fish")
        fish_data = json.loads(self.request.body)
        new_fish = Fish(name=fish_data['name'], parent=parent_key)
        new_fish.put()
        fish_dict = new_fish.to_dict()
        fish_dict['self'] = '/fish/' + new_fish.key.urlsafe()
        self.response.write(json.dumps(fish_dict))

    def get(self, id=None):
        if id:
            f = ndb.Key(urlsafe=id).get()
            # How to modify attributes
            # f.ph_max = 100
            # f.put()
            f_d = f.to_dict()
            f_d['self'] = "/fish/" + id
            self.response.write(json.dumps(f_d))

app = webapp2.WSGIApplication([
    ('/', HelloWebapp2),
    ('/fish', FishHandler),
    ('/fish/(.*)', FishHandler),
], debug=True)
