#!/usr/bin/python
# coding=utf-8
import httplib
import urllib
import base64
import string
import xml.dom.minidom
import rfc3339_parse
import datetime
import sys
import json

f = open('/usr/local/etc/davclean.json', 'r')
options_list = json.load(f,"utf-8")
f.close()
returncode = 0

for options in options_list:
	try:
		remotedir=urllib.quote(options["remotedir"].encode("utf-8"))
	
		conn = httplib.HTTPSConnection(options["host"])
		headers = {"Depth": "1", "Authorization": 'Basic ' + base64.encodestring(options["user"] + ':' + options["password"]).strip()}
		conn.request("PROPFIND", remotedir, "", headers)
		response = conn.getresponse()
		data = response.read()
	
		dom = xml.dom.minidom.parseString(data)
		responses = dom.getElementsByTagNameNS("DAV:","response")
	
		targeturls = []
		now = datetime.datetime.now(rfc3339_parse.UTC_TZ)
	
		for r in responses:
			href=r.getElementsByTagNameNS("DAV:","href")[0].childNodes[0].nodeValue
			cdatestr=r.getElementsByTagNameNS("DAV:","creationdate")[0].childNodes[0].nodeValue
			cdatetime=rfc3339_parse.parse_datetime(cdatestr)
#			print "found " +  href
			for t in options["targets"]:
				if href.startswith(t[0]) and ( ( now - datetime.timedelta(days=t[1])) >  cdatetime ):
					targeturls.append(href)
					break
	except Exception as inst:
		print type(inst)     # the exception instance
		print inst.args      # arguments stored in .args
		print inst           # __str__ allows args to printed directly
		returncode = 1
		continue

	headers = {"Authorization": 'Basic ' + base64.encodestring(options["user"] + ':' + options["password"]).strip()}
	for url in targeturls:
		data = ""
		try:
#			print "removing " + href
			conn.request("DELETE", url, "", headers)
			response = conn.getresponse()
			data = response.read()
		except Exception as inst:
			print type(inst)     # the exception instance
			print inst.args      # arguments stored in .args
			print inst           # __str__ allows args to printed directly
			returncode = 1
			continue
		if response.status not in {httplib.OK, httplib.NO_CONTENT} :
			print "Failed DELETE on %s: status=%d, response=\"%s\"" % (url, response.status, data)
			returncode = 1

sys.exit(returncode)
