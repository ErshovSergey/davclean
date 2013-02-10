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

for options in options_list:
	try:
		remotedir=urllib.quote(options["remotedir"].encode("utf-8"))
		returncode = 0
	
		conn = httplib.HTTPSConnection(options["host"])
		headers = {"Depth": "1", "Authorization": 'Basic ' + base64.encodestring(options["user"] + ':' + options["password"]).strip()}
		conn.request("PROPFIND", remotedir, "", headers)
		response = conn.getresponse()
		data = response.read()
	
		dom = xml.dom.minidom.parseString(data)
		responses = dom.getElementsByTagName("d:response")
	
		targeturls = []
		now = datetime.datetime.now(rfc3339_parse.UTC_TZ)
	
		for r in responses:
			href=r.getElementsByTagName("d:href")[0].childNodes[0].nodeValue
			cdatestr=r.getElementsByTagName("d:creationdate")[0].childNodes[0].nodeValue
			cdatetime=rfc3339_parse.parse_datetime(cdatestr)
#			print "found " +  href
			for t in options["targets"]:
				if href.startswith(t[0]) and ( ( now - datetime.timedelta(days=t[1])) >  cdatetime ):
					targeturls.append(href);
					break
	except Exception as inst:
		print type(inst)     # the exception instance
		print inst.args      # arguments stored in .args
		print inst           # __str__ allows args to printed directly
		returncode = 1
		continue

	headers = {"Authorization": 'Basic ' + base64.encodestring(options["user"] + ':' + options["password"]).strip()}
	for url in targeturls:
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
		if response.status != httplib.OK :
			print "Failed DELETE on " + url
			returncode = 1

sys.exit(returncode)
