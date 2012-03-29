#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#  todo: add date selector; cleaner template; csv dl; test
import os
from google.appengine.ext.webapp import template
from google.appengine.api import users, memcache
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
import sys
import cgi
import re
import simplejson
import random
import uuid
import StringIO
from google.appengine.ext import db
import googleplusevaluator as gpe
from gaesessions import get_current_session


class buildExcel(webapp.RequestHandler):
	def get(self):
		session = get_current_session()
		
		profiles = session.get('profiles')
		out = StringIO.StringIO()
		key = "ID,Kind,Image,Display name,URL,Plus ones,Replies,Reshares,Checkins,Posts,Shares,Last Updated\n"
		out.write(key)
		for x in profiles:
			y = str(x)
			y = y.replace('[','')
			y = y.replace(']','')
			y = y.replace("'","")
			y = y.replace("(","")
			y = y.replace(")","")
			y = y.replace("uperson","person")
			y = y.replace("uhttps://","https://")
			y = y.replace(", u",", ")
			y = y.replace("u1","1")
			out.write(y+"\n")
					# HTTP headers to force file download
		self.response.headers['Content-Type'] = 'text/csv'
		self.response.headers['Content-disposition'] = 'attachment; filename="profiles.csv"'
			# output to user
		self.response.out.write(out.getvalue())
#		session.terminate()

class getProfiles(webapp.RequestHandler):
	def post(self):
		session = get_current_session()
		query = self.request.get('query')
		try:
			meh = gpe.eval(query,3)
			session['profiles'] = meh
		
			path = os.path.join(os.path.dirname(__file__), 'getprofiles.html')
			template_values = {
				'data':meh,
				'query':query
			}
			self.response.out.write(template.render(path, template_values))
		except DeadlineExceededError:
			self.response.out.write("Ugh. Google timed out. Someday, when we have time, we'll build a pretty interface that keeps trying until this works. For now, all you can do is hit refresh and try again, sorry.")
class getSingleProfile(webapp.RequestHandler):
	def post(self):
		session = get_current_session()
		profiles = self.request.get('profiles')
		profiles = profiles.split(',')
		meh = gpe.single(profiles)
		session['profiles'] = meh

		path = os.path.join(os.path.dirname(__file__), 'getprofiles.html')
		template_values = {
			'data':meh,
			'query':profiles
		}
		self.response.out.write(template.render(path, template_values))
		
class MainPage(webapp.RequestHandler):
	def get(self):
		session = get_current_session()
		user = users.get_current_user()
		if user:
			path = os.path.join(os.path.dirname(__file__), 'index.html')
			template_values = {

			}
			self.response.out.write(template.render(path, template_values))
		else:
			self.redirect(users.create_login_url(self.request.uri))

class tester(webapp.RequestHandler):
	def get(self):
		query = "seo"
		status = "Starting"
#		meh = gpe.eval(query,1)
		path = os.path.join(os.path.dirname(__file__), 'tester.html')
		template_values = {
			'status': status,
			'query': query
		}
		self.response.out.write(template.render(path, template_values))	

class refresh(webapp.RequestHandler):
	def get(self):
		session = get_current_session()
		
		string = session['status']
		self.response.out.write(string)

class RPCHandler(webapp.RequestHandler):
	def __init__(self):
		webapp.RequestHandler.__init__(self)
		self.methods = RPCMethods()

	def get(self):
		func = None

		action = self.request.get('action')
		if action:
			if action[0] == '_':
				self.error(403) # access denied
				return
			else:
				func = getattr(self.methods, action, None)

		if not func:
			self.error(404) # file not found
			return

		args = ()
		while True:
			key = 'arg%d' % len(args)
			val = self.request.get(key)
			if val:
				args += (simplejson.loads(val),)
			else:
				break
		result = func(*args)
		self.response.out.write(simplejson.dumps(result))		

class RPCMethods:
	""" Defines the methods that can be RPCed.
	NOTE: Do not allow remote callers access to private/protected "_*" methods.
	"""
	def fetchData(self,query):
		# The JSON encoding may have encoded integers as strings.
		# Be sure to convert args to any mandatory type(s).
# 		meh = gpe.eval(query,1)	
		meh = "asdfasdfasdf"
		
		return meh

			
application = webapp.WSGIApplication([
	('/', MainPage),
	('/getprofiles', getProfiles),
	('/getsingleprofile', getSingleProfile),
	('/tester', tester),
	('/rpc', RPCHandler),
	('/refresh', refresh),
	('/buildExcel', buildExcel)],
	debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
    main()
