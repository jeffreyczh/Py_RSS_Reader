import os
import json

class MyRSS:
	settingPath = ""
	settings = {}
	bookmarksPath = ""
	bookmarks = {}
	# path for the folder to store all cache
	cachePath = ""
	def __init__(self):
		"""constructor"""
		self.__initVals()
		self.__loadSetting()
		self.__loadBookmarks()

	def __initVals(self):
		""" initialize all attributes"""
		currentDir = os.path.dirname(os.path.abspath(__file__))
		metadataDir = os.path.join(currentDir, 'metadata')
		self.settingPath = os.path.join(metadataDir, 'setting')
		self.bookmarksPath = os.path.join(metadataDir, 'bookmarks')
		self.cachePath = os.path.join(metadataDir, 'cache')

	def __loadSetting(self):
		"""load the setting from the setting file"""
		try:
			settingFile = open(self.settingPath)
			self.settings = json.loads(settingFile.read())
			settingFile.close()
			# load the bookmarks path from the setting
			try:
				self.bookmarksPath = self.settings['bookmarks_path']
			except KeyError:
				self.settings['bookmarks_path'] = self.bookmarksPath
				self.__saveSettings()
			# load the cache path from the setting
			try:
				self.cachePath = self.settings['cache_path']
			except KeyError:
				self.settings['cache_path'] = self.cachePath
				self.__saveSettings()
			
		except IOError:
			# the setting file might not exist
			# create this file
			self.__saveSettings()

	def __saveSettings(self):
		"""save settings to a file"""
		self.__ensureDir(self.settingPath)
		settingFile = open(self.settingPath, "w")
		settingFile.write(json.dumps(self.settings))
		settingFile.close()

	def __loadBookmarks(self):
		"""load bookmarks from the file specified by the setting"""
		try:
			bookmarksFile = open(self.bookmarksPath)
			self.bookmarks = json.loads(bookmarksFile.read())
			bookmarksFile.close()
		except IOError:
			# the file which stores book marks does not exist
			pass

	def __saveBookmarks(self):
		"""save bookmarks to the bookmarks file and update the settings"""
		self.__ensureDir(self.bookmarksPath)
		bookmarksFile = open(self.bookmarksPath, "w")
		bookmarksFile.write(json.dumps(self.bookmarks))
		bookmarksFile.close()

	def saveBookmark(self, name, url):
		"""save a url to a book mark"""
		if self.bookmarks.has_key(name):
			response =  str(raw_input("A bookmark with the same name exists. Overwrite? (y/n): ")).lower()
			if response != "y":
				return
		self.bookmarks[name] = url
		self.__saveBookmarks()

	def checkUpdate(self, name):
		"""check update for a specific bookmark
		download the update and save it to the cache
		"""
		dic = self.__loadCache(name)
		try:
			url = self.bookmarks[name]
			# send request to get update
			import urllib2
			request = urllib2.Request(url)
			request.add_header('If-Modified-Since',
				dic['last-modified'])
			opener = urllib2.build_opener()
			stream = opener.open(request)
			print name + " has update!"
			content = stream.read()
			# save into cache
			dic['last-modified'] = stream.headers.get('last-modified')
			dic['content'] = content
			self.__saveCache(name, dic)
			# deal with update ...
			# translate the content with the specified unicode
		except KeyError:
			print 'Error: Undefined bookmark: ' + name
			return
		except urllib2.HTTPError, e:
			if e.getcode() == 304:
				# not modified
				return


	def checkUpdates(self):
		"""check updates for all bookmarks"""
		map(self.checkUpdate, self.bookmarks.keys())

	def __ensureDir(self, path, isFile=True):
		"""ensure directories exist
		if not exist, create them

		isFile: whether the given path is a path of a file. Defaultly true.
		"""
		if isFile:
			d = os.path.dirname(path)
		else:
			d = path
		if not os.path.exists(d):
			try:
				os.makedirs(d)
			except OSError:
				print 'Error: The path: \"' + d + '\" is invalid.'

	def __saveCache(self, cacheFileName, content):
		"""save the cache to the cache file"""
		cacheFilePath = os.path.join(self.cachePath, cacheFileName)
		self.__ensureDir(cacheFilePath)
		cacheFile = open(cacheFilePath, "w")
		cacheFile.write(json.dumps(content))
		cacheFile.close()

	def __loadCache(self, cacheFileName):
		"""load cache from the file"""
		cacheFilePath = os.path.join(self.cachePath, cacheFileName)
		self.__ensureDir(cacheFilePath)
		try:
			cacheFile = open(cacheFilePath)
			content = json.loads(cacheFile.read())
			cacheFile.close()
		except IOError:
			content = self.__createCacheDic()
		return content

	def __createCacheDic(self):
		"""create an empty cache dictionary"""
		dic = {'last-modified': '', 'content': ''}
		return dic






#def run(url):
#	import httplib, urllib2
#	request = urllib2.Request(url)
#	opener = urllib2.build_opener()
#	fs = opener.open(request)
#	from xml.dom import minidom
#	xmldoc = minidom.parse(fs)
#	items = xmldoc.getElementsByTagName("item");
#	for i in range(0, items.length):
#		pubdate = items[i].getElementsByTagName("pubDate")[0].firstChild.nodeValue
#		title = getCDATAValue(items[i].getElementsByTagName("title")[0])
#		des = getCDATAValue(items[i].getElementsByTagName("description")[0])
#		print pubdate + " --- " + title
#		print "\t" + des
#		print "----------------------------------"


#def getCDATAValue(node):
#	"""Get all nodes value inside the given node"""
#	return "".join([t.nodeValue for t in node.childNodes if t.nodeType == t.CDATA_SECTION_NODE])


if __name__ == '__main__':
	myrss = MyRSS()
	print myrss.bookmarks
	myrss.checkUpdates()