"""
File contains the gitmarks object clas.
"""

import hashlib
import httplib
import json
import logging
import os
import re
import sys
import time
import urllib

# -- Our own gitmarks settings
import settings
import git

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
handler = logging.FileHandler('hello.log')
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(formatter)
logger.addHandler(consoleHandler)

GITMARK_VER_STRING = 'gitmark.0.3'

# Arguments are passed directly to git, not through the shell, to avoid the
# need for shell escaping. On Windows, however, commands need to go through the
# shell for git to be found on the PATH, but escaping is automatic there. So
# send git commands through the shell on Windows, and directly everywhere else.
USE_SHELL = os.name == 'nt'


class gitMark(object):
	# -- GitMarks members
	# If you add member variables you don't want in a gitmark, delete them in JSONBlock below
	# Otherwise self.__dict__ works rong.
	uri = None #string
	hash = None #hash value 
	summary = None #string
	description = None #string 
	tags = [] #list of strings of tags
	time = None #ISO8601 absolute date time
	creator = None
	rights = None #creative commons rights string
	tri = [] #transitionary resource locator. IRL bit.ly, goo.gl, etc
	content = None  #content of the site. Lazyloads and should do smart local/away fetch
	title = None
	extended = None
	meta = None
	private = None
	ver = GITMARK_VER_STRING

	def __init__(self,uri, creator=None, dictValues=None):
		# -- temp. Force build deafults before overriding
		self.uri = uri
		self.hash = self.generateHash(uri)
		self.time = time.strftime("%Y-%m-%dT%H:%M:%SZ")
		self.creator  = creator
		self.rights = 'CC BY'
		self.private = True	 #default to private for safety
		
		if dictValues:
			#DANGER: this is a security danger
			self.__dict__
		#TODO: Do I want to return self?
		
		
	def addTags(self, stringList):
		logging.debug('adding tags='+stringList)
		#if we have more than 1 quote, split by quotes
		if stringList.count('"') > 1:
			logging.error('has qouted string! We fail')
		else :
			list = stringList.split(',')
			list = [ l.lstrip().rstrip() for l in list]
			#TODO: do some smart string hacking, for different strings
			# of data formatting
			self.tags.extend(list)
					
	def noContentSet(self):
		"""
		returns true of this gitmark is set to 'get no content'
		"""
		#TODO menoize this result, and kill the menoize if we get
		# a change to the tag. Maybe menoize to a hash of the list,
		# and if the hash changes, re-calculate?
		if 'no content' in self.tags:
			return True
		elif 'no_content' in self.tags:
			return True
		return False
	
	def __str__(self):
		return '<gitmark obj for "%s" by "%s"\n>' %(self.uri, self.creator)
	
	def setPrivacy(self, privacy):
		""" Set this gitmark to be private """
		self.private = privacy
		
	def generateHash(self, uri = None):
		"""generates a hash for our URI (or the passed
		URI if it is not null"""
		if(uri == None): 
			uri = self.uri
		m = hashlib.md5()
		m.update(uri)
		return m.hexdigest()

	def parseTitle(self, content=None):
		""" parses the tile from html content, sets it to 
		our local title value, and returns the title to the caller"""
		if content == None:
			content = self.content
		self.title = self.cls_parseTitle(content)
		return self.title
		
	def getContent(self, uri=None):
		"""
		Get content from the web, and store it to our local 
		content structure. IF we have a uri, gets contents from 
		there instead of our local uri.
		"""
		if uri == None:
			uri = self.uri
		#FUTURE: do we want to allow a different URI to get passed in?			
		self.content = self.cls_getContent(uri)
		 
	def uncacheContent(self, target_file):
		"""
		Reads content from our local cache	if we have it, 
		otherwise it will fetch that content from the web (not 
		store it) and save it to the local gitmark.
		"""		
		if os.path.isfile(target_file) :	
			fh = open(target_file,"r")
			self.content = fh.read()
			del fh
		else:
			print >>sys.stderr, ("Warning: no local content for this gitmark."
				"tryig to read from web")					
			self.getContent() 

	def setTimeIfEmpty(self):
		if self.time is None:
			self.time = time.strftime("%Y-%m-%dT%H:%M:%SZ")

	def cacheContent(self, target_file, content=None):
		""" 
		Write this gitmarks content to the target file. If this
		content is specified, then that content is written instead
		of the content in this gitmark
		"""
		if content is None:
			if self.content is None:
				self.getContent()
			content = self.content
		# -- lazily git store any existing file if necessary
		if os.path.isfile(target_file) :
			#check the md5 sum of the contet of this file, 
			#if it does NOT match our new content, then 
			logging.error("do magic here to md5 sum, and cache file if needed")
		if content == None:
			content = self.content 
		self.cls_saveContent(target_file, content)
			
	def addMyselfLocally(self, localGitmarkDir, localTagsDir):
		"""
		This method causes a gitmark to
		add itself to the local repository.
		""" 
		logging.error("not used. old code. Use for reference only")
		exit(-5)
		
		logging.info("adding myself to the local repository")
		if self.private:
			logging.info("this is a private mark. Encrypting not yet enabled. Do not store")
		else :
			# -- write gitmark
			fname = os.path.join(localGitmarkDir,self.hash)
			#fp = open(fname,"w")
			logging.info('debug fwrite of file "%s"' % fp)
			logging.info('---')
			logging.info( self.JSONBlock() )
			logging.info('---')
			#fwrite(self.JSONBlock())
			#fclose(fp)
			# add git add here
			
			# -- write tags
			fname = os.path.join(localGitmarkDir,self.hash)
			fp = open(fname,"w")
			prettyTags = self.prettyTags() 
			uglyTags = self.uglyTags()
			tags = set(uglyTags.append(prettyTags))			
			for tag in tags:
				fname = os.path.join(localGitmarkDir,self.hash)
				logging.info( 'tag filename "%s" ' %fname )
				# add git add here
			settings.TAG_SUB_PATH
						

			
	def JSONBlock(self):	
		"""creates and retuns a JSON text block of 
		current members of this gitMark. """
		d = self.__dict__
		if 'content' in d.keys() :
			del d['content'] #remove content, we don't want that
		return json.dumps(d,indent=4)
	
	def miniJSONBlock(self):
		""" creates and returns a minimun json block, used for tag files """
		d = {'hash':self.hash, 'title':self.title, 'uri':self.uri,
			'creator':self.creator,	 'ver':self.ver }
		return json.dumps(d,indent=4)
			
		
	def prettyTags(self):
		""" tags, cleaned from delicious and make nicer looking"""
		g = []
		for t in self.tags:
			logging.info ( t )
			if '_' in t:
				g.append(t.replace('_',' '))
			else:
				g.append(t)
			logging.info( g )
		return g
			
	def uglyTags(self):
		""" tags as gotten raw, un-prettied for search and use"""
		return self.tags
		
		
	def everyPossibleTagList(self):
		allTags = self.prettyTags()
		allTags.extend(self.uglyTags())
		allTags = set(allTags)
		return allTags

	@classmethod	
	def cls_hydrate(cls, filename):
		"""  
		Create and returns a gitmark object from files on the local filesystem. 
		"""
		f = open(filename,'r')
		if f:
			jsonObj = f.read()
			f.close()
			del f
			obj = json.loads(jsonObj)
			logging.info( obj ) 
			mark = gitMark(settings.USER_NAME)
			mark.__dict__.update(obj) #force update dict from file
			return mark 
	
		logging.error( "failed to read/load %s" %filename)
		return None
	
	@classmethod
	def cls_saveContent(cls, filename, content):
		f = open(filename, 'w')
		f.write(content)
		f.close()
		return filename
		
	@classmethod
	def cls_generateHash(cls, text):
		m = hashlib.md5()
		m.update(text)
		return m.hexdigest()
		
	@classmethod
	def cls_getContent(cls, url):
		""" Attempts to download content from the specified url, 
		@return data from the specified URL 
		"""
		try:
			h = urllib.urlopen(url)
			content = h.read()
			h.close()
			h = urllib.urlopen(url)

		except IOError, e:
			print >>sys.stderr, ("Error: could not retrieve the content of a"
			" URL. The bookmark will be saved, but its content won't be"
			" searchable. URL: <%s>. Error: %s" % (url, e))
			content = ''
		except httplib.InvalidURL, e: #case: a redirect is giving me www.idealist.org:, which causes a fail during port-number search due to trailing :
			print >>sys.stderr, ("Error: url or url redirect contained an"
			"invalid  URL. The bookmark will be saved, but its content"
			"won't be searchable. URL: <%s>. Error: %s" % (url, e))
			content=''
		return content
	
	@classmethod
	def cls_parseTitle(cls, content):
		if content is None: return '[No Title]'
		re_htmltitle = re.compile(".*<title>(.*)</title>.*")
		try:
			t = re_htmltitle.search(content)
			title = t.group(1)
		except AttributeError:
			title = '[No Title]'
		return title
		
	@classmethod
	def gitAdd(cls, files, forceDateTime=None, gitBaseDir=None):
		logger.debug('git add')
		cls.git_add(os.path.abspath(gitBaseDir), files)

	@classmethod
	def git_add(cls, repo_path, files):
		repo = git.Repo(repo_path)
		for file in files:
			repo.git.add(file)

	@classmethod
	def git_commit(cls, repo_path, commit_message):
		repo = git.Repo(repo_path)
		repo.git.commit(m=commit_message)

	@classmethod
	def gitCommit(cls, msg, repo_path = None):
		logger.debug('git commit')
		cls.git_commit(os.path.abspath(repo_path), msg)

	@classmethod
	def gitPush(cls, gitBaseDir = None):
		logger.debug('gitpush')
		cls.git_push(os.path.abspath(gitBaseDir))

	@classmethod
	def git_push(cls, repo_path):
		repo = git.Repo(repo_path)
		try:
			repo.git.push()
		except:
			logger.error('failed to push to remote')

class gitmarkRepoManager(object):

	def __init__(self):
		logging.info( "initalizing a repo manager")
		
	
