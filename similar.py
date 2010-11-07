#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# this program display similar thing it use tastekid.com API
# Copyright (C) 2010 Jakub Jankiewicz
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

#from urllib import urlencode
from urllib2 import urlopen, Request, HTTPError, URLError
from urllib import quote_plus
from sys import argv, stderr
from os.path import basename
from getopt import getopt, GetoptError
from StringIO import StringIO
import json
import re

def gets(dict, *keys):
    "function generate values from dictionary which is on the list."  
    for e in keys:
	yield dict[e]

def partial_first(fun, *args):
    "return single argument function which execute function fun with arguments."
    def p(object):
	return fun(object, *args)
    return p

def gets_fun(*args):
    "return function which return values from dictinary which is on the list."
    return partial_first(gets, *args) 

class ServerJsonException(Exception):
    pass
	
class Similar(object):
    def __init__(self, stuff, type=None):
	query = quote_plus(stuff)
	if type:
	    query = '%s:%s' % (type, query)
	url = 'http://www.tastekid.com/ask/ws?&q=%s&format=JSON&verbose=1'
	response_data = urlopen(url % query).read()
	if not re.match('{.*}', response_data):
	    raise ServerJsonException
	#fix malform json
	response_data = response_data.replace('}{', '},{')
	self.data = json.load(StringIO(response_data))
	
    def infos(self):
	for i in self.data['Similar']['Info']:
	    yield Similar.Stuff(*list(gets(i, 'Name', 'Type', 'wTeaser')))

    def similar(self):
	"generate list of Stuff."
	results = self.data['Similar']['Results']
	if len(results) == 0:
	    yield None
	for result in results:
	    elems = list(gets(result, 'Name', 'Type', 'wTeaser', 'yTitle', 'yUrl'))
	    yield Similar.Stuff(*elems)
	    
    class Stuff(object):
	def __init__(self, name, type, description, y_title=None, y_url=None):
	    self.name = name.encode('UTF-8')
	    self.type = type.encode('UTF-8')
	    self.description = description.encode('UTF-8')
	    if y_title:
		self.y_title = y_title.encode('UTF-8')
	    if y_url:
		self.y_url = y_url.encode('UTF-8')

usage = """usage:
%s -d -i -y -l <lang> <search query>
d - display descriptions
i - display only info
y - display youtube links
l - translate descriptions
    lang should be one of:
    af - afrikaans
    sk - albánskej
    ar - عربي
    be - Беларускі
    bg - Български
    zh - 荃湾
    zh - 太阳
    hr - Hrvatski
    cs - Český
    da - Danske
    et - Eesti
    tl - filipiński
    fi - Suomi
    fr - Français
    gl - galijski
    el - Ελληνικά
    iw - עברית
    hi - हिन्दी
    es - Español
    nl - Nederlands
    id - indonezyjski
    ga - Gaeilge
    is - Íslenska
    ja - 日本語
    yi - ייִדיש
    ca - Català
    ko - 한국의
    lt - Lietuvos
    lv - Latvijas
    mk - Македонски
    ms - Melayu
    mt - Malti
    de - Deutsch
    no - Norsk
    fa - فارسی
    pl - polski
    ru - Русский
    ro - Română
    sr - Српски
    sk - Slovenský
    sl - Slovenski
    sw - Swahili
    sv - Svenska
    th - ภาษาไทย
    tr - Türk
    uk - Український
    cy - walijski
    hu - Magyar
    vi - Việt
    it - Italiano

put "band:", "movie:", "show:", "book:" or "author:" before name if you want to specify search
""" % basename(argv[0])

def main():
    try:
        opts, rest = getopt(argv[1:], 'dl:iy')
    except GetoptError:
        print usage
        exit(1)
    opts = dict(opts)
    if opts.has_key('-h'):
        print usage
        exit(0)
    description = opts.has_key('-d')
    info = opts.has_key('-i')
    youtube = opts.has_key('-y')
    lang = opts.get('-l')
    if len(rest) == 0:
	print usage
    else:
	try:
	    stuff = Similar(' '.join(rest))
	    if info:
		for info in stuff.infos():
		    print '%s (%s)' % (info.name, info.type)
		    if lang:
			from xgoogle.translate import Translator
			translate = Translator().translate
			print translate(info.description, lang_to=lang)
		    else:
			print info.description
	    else:
		for stuff in stuff.similar():
		    print stuff.name
		    if youtube:
			print 'Youtube:'
			print '\t%s' % stuff.y_title
			print '\t%s' % stuff.y_url
		    if description:
			if lang:
			    from xgoogle.translate import Translator
			    translate = Translator().translate
			    print translate(stuff.description, lang_to=lang)
			else:
			    print stuff.description
    except URLError:
	    print >> stderr, "Error: you're not connected to the internet" 
	except ServerJsonException:
	    print >> stderr, "Error: can't read recived data from the server"


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        #when user hit Ctrl-C
        exit(1)
