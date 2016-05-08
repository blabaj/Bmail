from google.appengine.ext import ndb
from google.appengine.api import users


class  Bmail(ndb.Model):
    posiljatelj = ndb.StringProperty()
    sporocilo = ndb.TextProperty()
    datum_sporocila = ndb.DateTimeProperty(auto_now_add=True)
    naslovnik = ndb.StringProperty()
    zadeva = ndb.TextProperty()
