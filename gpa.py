# import os
import simplejson
import httplib
import re
import urllib
import datetime
from datetime import *
from gaesessions import get_current_session

def eval(queryterm, pages):
	apiurl = "www.googleapis.com"
	urlstart = "/plus/v1/people/"
	theterm = "seo"
	apikey = "AIzaSyB821z11J56ZrmbH9F7mzQybuZqUSBSS2M"
	#	print "Display Name", "\t", "URL", "\t", "Image", "\t", "Type", "\t", "Reshares", "\t", "Replies", "\t", "Plus Ones"
	theterm = urllib.quote_plus(theterm)
	theRequest =  "&maxResults=20&fields=items(displayName%2Cid%2Cimage%2Ckind%2Cnickname%2CobjectType%2Curl)%2Ckind%2CnextPageToken&pp=1&key="
	pages = pages
	pagelimit = pages
	recordCount = 0
	# first, do a search on this term
	requesturl = urlstart + "?query=" + str(theterm) + theRequest + apikey
	rList = []

	while pages > 0:
	#		print "Processing batch ", pages
		# pagination via the API
		counter = 60 - recordCount
		if pages < pagelimit:
			nextPage = data["nextPageToken"]
			nextPage = "&pageToken=" + nextPage
			requesturl = urlstart + "?query=" + str(theterm) + nextPage + theRequest + apikey
		requesturl = str(requesturl)
		conn = httplib.HTTPSConnection(apiurl)
		conn.request("GET",requesturl)
		res = conn.getresponse()
		foo = res.read()
		conn.close()
		data = simplejson.loads(foo)
		items = data["items"]
		pages = pages - 1
		for d in items:
			recordCount = recordCount + 1
			thisOne = []
			theid = d["id"]
			kind = d["kind"]
			img = d["image"]["url"]
			dname = d["displayName"]
			url = d["url"]
			# now, grab activity data for each person
			requesturl = "/plus/v1/people/" + str(theid) + "/activities/public?fields=items(actor(displayName,id),id,kind,object(actor/id,attachments(displayName,image/url,objectType),objectType,plusoners,replies,resharers),published,updated,verb),kind&key=AIzaSyB821z11J56ZrmbH9F7mzQybuZqUSBSS2M"
			requesturl = str(requesturl)
			conn = httplib.HTTPSConnection(apiurl)
			conn.request("GET",requesturl)
			res = conn.getresponse()
			foo = res.read()
			conn.close()
			data2 = simplejson.loads(foo)
			acts = data2["items"]
			tplusones = 0
			treplies = 0
			treshares = 0
			checkins = 0
			posts = 0
			shares = 0
			counter = 0
			for a in acts:
				if counter == 0:
					thedate = a["updated"]
					thedate = thedate.replace("Z","")
					thedate = thedate.split('.')[0]
					lastUpdated = datetime.strptime(thedate, '%Y-%m-%dT%H:%M:%S')
					lastUpdated = datetime.strftime(lastUpdated, '%m/%d/%y %M:%S')
				verb = a["verb"]
				verb = verb.strip()
				verb = verb.replace("\r\n","")
				reshares = a["object"]["resharers"]["totalItems"]
				pdate = a["published"]
				replies = a["object"]["replies"]["totalItems"]
				plusones = a["object"]["plusoners"]["totalItems"]
				tplusones = tplusones + plusones
				treshares = treshares + reshares
				treplies = treplies + replies
				counter = counter + 1
				if verb == "post":
					posts = posts + 1
				if verb == "checkin":
					checkins = checkins + 1
				if verb == "shares":
					shares = shares + 1
	#			return "Storing activity data for " + dname
			thisOne = theid, kind, img, dname, url, tplusones, treplies, treshares, checkins, posts, shares, lastUpdated, counter
			rList.append(thisOne)
	#			return "Done working with " + dname

