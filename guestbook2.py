from google.appengine.api import users
from google.appengine.api import ndb
import webapp2
import urllib
import jinja2
import os

DEFAULT_GUESTBOOK_NAME = 'default_guestbook'

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__),'templates')),
    extensions=['jinja2.ext.autoescape'])

def guestbook_key(guestbook_name=DEFAULT_GUESTBOOK_NAME):
    return ndb.Key('Guestbook', guestbook_name)

class Greeting(ndb.Model):
    author = ndb.UserProperty()
    content = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)

class MainPage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        logout_url = users.create_logout_url(self.request.path)
        guestbook_name = self.request.get('guestbook_name',
                                          DEFAULT_GUESTBOOK_NAME)
        greetings_query = Greeting.query(ancestor=guestbook_key(guestbook_name)).order(-Greeting.date)
        greetings = greetings_query.fetch(10)
        if user:
        	template = JINJA_ENVIRONMENT.get_template('welcome.html')
        	template_values = {
                'greetings': greetings
                'guestbook_name': urllib.quote_plus(guestbook_name)
            	'user': user.nickname(),
            	'url_logout': logout_url,
            	'url_logout_text': 'Log out',
        	}
        	self.response.write(template.render(template_values))
        else:
            self.redirect(users.create_login_url(self.request.uri))
            
    def post(self):
        user = users.get_current_user()
        logout_url = users.create_logout_url(self.request.path)
        greeting = Greeting(parent=guestbook_key(guestbook_name))
        
        if users.get_current_user():
            greeting.author = users.get_current_user
        
        greeting.content = self.request.get('content')
        greeting.put()
        
        query_params = {'guestbook_name': guestbook_name}
        self.redirect('/?' + urllib.urlencode(query_params))
        
        if user:
        	template = JINJA_ENVIRONMENT.get_template('guest.html')
        	template_values = {
            	'user': user.nickname(),
            	'url_logout': logout_url,
            	'url_logout_text': 'Log out',
            	'greetings': self.request.get('content'),
        	}
        	self.response.write(template.render(template_values))
        else:
            self.redirect(users.create_login_url(self.request.uri))


application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/sign',MainPage),
], debug=True)
