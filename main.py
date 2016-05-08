#!/usr/bin/env python
import os
import jinja2
import webapp2
from models import Bmail
import time
from google.appengine.api import users

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=False)

def najdiUporabnika():
    user = users.get_current_user()

    if user:
        logiran = True
        logout_url = users.create_logout_url('/')
        params = {"logiran": logiran, "logout_url": logout_url, "user": user}
        return params
    else:
        logiran = False
        login_url = users.create_login_url('/')
        params = {"logiran": logiran, "login_url": login_url, "user": user}
        return params


class BaseHandler(webapp2.RequestHandler):

    def write(self, *a, **kw):
        return self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        return self.write(self.render_str(template, **kw))

    def render_template(self, view_filename, params=None):
        if not params:
            params = {}
        template = jinja_env.get_template(view_filename)
        return self.response.out.write(template.render(params))


class MainHandler(BaseHandler):
    def get(self):
        params = najdiUporabnika()
        vnosi = Bmail.query().fetch()
        params.update({"vnosi":vnosi})
        return self.render_template("panel.html", params)
    def post(self):

        user = users.get_current_user()
        if user:
            logiran = True
            logout_url = users.create_logout_url('/')

            params = {"logiran": logiran, "logout_url": logout_url, "user": user}
        else:
            logiran = False
            login_url = users.create_login_url('/')

            params = {"logiran": logiran, "login_url": login_url, "user": user}

        return self.render_template("panel.html", params)

class SporociloHandler(BaseHandler):
    def get(self, sporocilo_id):
        params = najdiUporabnika()
        sporociloPridobitev = Bmail.get_by_id(int(sporocilo_id))
        sporocilo = {"sporocilo":sporociloPridobitev}
        params.update(sporocilo)
        return self.render_template("sporocilo.html", params)

class UrediHandler(BaseHandler):
    def get(self, vnos_id):
        vnos = Bmail.get_by_id(int(vnos_id))
        params = {"vnos":vnos}
        return self.render_template("uredi.html", params)
    def post(self, vnos_id):
        vnos = Bmail.get_by_id(int(vnos_id))
        vrednost_vnosa = self.request.get("sporocilo")
        vnos.sporocilo = vrednost_vnosa
        vnos.put()
        time.sleep(0.1)
        return self.redirect_to("seznam-vnosov")

class BrisiHandler(BaseHandler):
    def get(self, sporocilo_id):

        sporocilo = Bmail.get_by_id(int(sporocilo_id))
        params = {"sporocilo":sporocilo}
        return self.render_template("brisi.html", params)
    def post(self, sporocilo_id):
        sporocilo = Bmail.get_by_id(int(sporocilo_id))
        sporocilo.key.delete()
        time.sleep(0.1)
        return self.redirect_to("seznam-vnosov")

class PrijetoHandler(BaseHandler):
    def get(self):
        uporabnik = najdiUporabnika()
        seznam = Bmail.query(Bmail.naslovnik==uporabnik["user"].email()).fetch()
        params = {"seznam":seznam}
        uporabnik.update(params)
        return self.render_template("prijeto.html", uporabnik)



class PoslanoHandler(BaseHandler):
    def get(self):
        uporabnik = najdiUporabnika()
        seznam = Bmail.query(Bmail.posiljatelj==uporabnik["user"].email()).fetch()
        params = {"seznam":seznam}
        uporabnik.update(params)
        return self.render_template("poslano.html", uporabnik)

class PosljiHandler(BaseHandler):
    def get(self):
        params = najdiUporabnika()
        return self.render_template("poslji.html", params)
    def post(self):
        uporabnik = najdiUporabnika()
        posiljatelj = uporabnik["user"].email()
        naslovnik = self.request.get("naslovnik")
        zadeva = self.request.get("zadeva")
        sporocilo = self.request.get("sporocilo")
        if (len(sporocilo) == 0 or len(sporocilo.strip(' ')) == 0):
            napaka = {"napaka":"Vsebina sporocila je potrebna!"}
            uporabnik.update(napaka)
            return self.render_template("poslji.html", uporabnik)
        vnos = Bmail(posiljatelj=posiljatelj, naslovnik=naslovnik, zadeva=zadeva, sporocilo=sporocilo)
        vnos.put()
        rezultat = {"rezultat":"Sporocilo je uspesno poslano!"}
        uporabnik.update(rezultat)
        return self.render_template("poslji.html", uporabnik)

app = webapp2.WSGIApplication([
    webapp2.Route('/', MainHandler, name = "seznam-vnosov"),
    webapp2.Route('/sporocilo/<sporocilo_id:\d+>', SporociloHandler),
    webapp2.Route('/sporocilo/uredi/<sporocilo_id:\d+>', UrediHandler),
    webapp2.Route('/sporocilo/brisi/<sporocilo_id:\d+>', BrisiHandler),
    webapp2.Route('/prijeto', PrijetoHandler),
    webapp2.Route('/poslano', PoslanoHandler),
    webapp2.Route('/poslji', PosljiHandler),
], debug=True)