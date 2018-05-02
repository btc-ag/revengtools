#! /usr/bin/env python
# -*- coding: UTF-8 -*-

'''
TODO add a short description here

Created on 16.08.2012

@author: FAFRANZE
'''

import pysvn
import time
import datetime
from collections import defaultdict
import os.path
import unittest
import tempfile
import shutil
import logging

class NoCommonPathError(Exception):
	pass

class FileNotFoundError(Exception):
	def __init__(self, fileName):
		self.filename = fileName
	def __str__(self):
		return "File not found: " + self.filename
	

#TODO SGi was ist mit Dateien, die gelöscht wurden? (Das ist eventuell hier nicht so wirklich wichtig, da der Fall eher selten vorkommt)
#TODO SGi Wichtiger sind aber Dateien, die umbenannt wurden. Funktioniert das? Hierfür sollte es einen Testfall geben!
#TODO SGi Der Fall ist schon wichtig... dafür sollte es auch einen Testfall geben!
#TODO: It's possible that the initial commit of file is not considered...
class SVNFreqAnalyser:
	# TODO SGi Die Bestandteile der Methodennamen sollten immer mit _ getrennt werden.   
	
	def __init__(self):
		self.svnClient = pysvn.Client()
	def __remove_prefix(self, path, prefix):
		inspath = os.path.relpath(path,prefix)
		if inspath == ".":
			inspath = ""
		if inspath[:2] == "..":
			raise NoCommonPathError
		return inspath
	def __print_log_entry(self, logEntry):
		print "Revision: %s Author: %s Message: %s" % (logEntry.revision, logEntry.author, logEntry.message)
		import pprint
		pprint.pprint([p.path for p in logEntry.changed_paths]) 
	def getChangeCountOfPath(self, path, start, end=None):
		"""Gibt die �nderungen von Dateien unterhalb von path zur�ck, seit start
		TODO erklären was end==None bedeutet 
		"""
		rootUrl = self.svnClient.root_url_from_path(path)
		baseUrl = self.svnClient.info(path).url.replace(rootUrl,"") + "/"
		if end == None:
			end = time.time()
			
		#Receive logs relevant for this path, stopping on svn copys...
		#Take care: For each log entry the changed_paths variable contains all changes made in the whole repository!
		log = self.svnClient.log(path,
									discover_changed_paths=True, 
									strict_node_history=True,
									revision_start=pysvn.Revision(pysvn.opt_revision_kind.date, end),
									revision_end=pysvn.Revision(pysvn.opt_revision_kind.date, start))
		#Debug: Print all log entries in log
		#for i in log:
		#	self.__print_log_entry(i)
		#Initialize pathChanges with all files
		pathChanges = dict()
		for (dirname, dirs, files) in os.walk(path):
			#Skip .svn dirs
			if ".svn" in dirs:
				dirs.remove(".svn")
			inspath = self.__remove_prefix(dirname, path)
			
			for file in files:
				pathChanges[os.path.normpath(os.path.join(inspath,file))] = 0
		
		#Count commits per file and summarize
		for logEntry in log:
			for pathEntry in logEntry.changed_paths:
				inspath = os.path.normpath(pathEntry.path[len(baseUrl):])
				#Skip changes outside the requested path and files not existing files in the working copy
				if pathEntry.path.startswith(baseUrl) and inspath in pathChanges:
					pathChanges[inspath] += 1
		# TODO return a frozendict
		return pathChanges
		
	def getChangeCountOfFileList(self, files, start, end):
		"""Gibt die �nderungen von den Dateien path zur�ck, seit start (die Dateien m�ssen alle in einem SVN sein)"""
		#Check file existence
		for f in files:
			if not os.path.exists(f):
				raise FileNotFoundError(f)
			
		prefix = os.path.dirname(os.path.commonprefix(files))
		logging.info("Using SVN Prefix: %s" % prefix)
		if prefix == "" or not os.path.exists(prefix):
			raise NoCommonPathError
		
		changeInformation = self.getChangeCountOfPath(prefix, start, end)
		import pprint
		# TODO use logging.debug( ... pprint.pformat ) instead
		#pprint.pprint(changeInformation)
		result = dict()
		for file in files:
			# TODO do not reuse local variable names...
			if os.path.isabs(file):
				file = os.path.relpath(file, prefix)
			else:
				file = self.__remove_prefix(file, prefix)
			logging.debug("SVN Change Count for file '%s' is %s", file, changeInformation[file])
			result[os.path.join(prefix,file)] = changeInformation[file]
		# TODO better return a frozendict or yield the individual entries
		return result
		
		
# TODO move this test to test/unitTests !
class TestSVNFreqAnalyser(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		# TODO SGi Warum ist das hier in setUpClass und nicht in setUp?
		cls.analyseRangeStart = time.mktime(datetime.date(2012, 7,31).timetuple())
		cls.analyseRangeEnd = time.mktime(datetime.date(2012, 7,1).timetuple())
		# TODO SGi Warum liegt end vor start? Das ist etwas verwirrend, bitte dokumentieren!
		#cls.checkoutDir = tempfile.mkdtemp()
		cls.checkoutDir = "SVNFreqAnalyserTestCheckout/"
		client = pysvn.Client()
		client.checkout("http://svn.e-konzern.de/repo/btc-project-epm/btc/epm/Source/trunk/CoreAssetBase/BTC/Commons/Core/NET", cls.checkoutDir)
	#@classmethod
	#def tearDownClass(cls):
	# TODO SGi Warum ist das auskommentiert? In der Tat sollten die temporären Dateien eigtl. wieder gelöscht werden.
	#	time.sleep(2)
	#	client = pysvn.Client()
	#	shutil.rmtree(cls.checkoutDir)
	def setUp(self):
		self.analyser = SVNFreqAnalyser()
	def test_getChangeCountOfPath(self):
		result = self.analyser.getChangeCountOfPath(self.checkoutDir, self.analyseRangeStart, self.analyseRangeEnd)
		self.assertEqual(result["WaitableHandler.cs"],1)
		self.assertEqual(result["AutoFinish2.cs"],0)
	def test_getChangeCountOfFileList(self):
		# TODO SGi Warum hast du hier erst einen String, den du dann splittest? 
		fileList = "AutoFinish2.cs;AutoFinish.cs;ArrayList.cs"
		fileList = fileList.split(";")
		fileList = [os.path.join(self.checkoutDir, file) for file in fileList]
		result = self.analyser.getChangeCountOfFileList(fileList, self.analyseRangeStart, self.analyseRangeEnd)

		self.assertEqual(result[os.path.normpath(os.path.join(self.checkoutDir,"AutoFinish2.cs"))],0)
		self.assertEqual(result[os.path.normpath(os.path.join(self.checkoutDir,"AutoFinish.cs"))],0)
		self.assertEqual(result[os.path.normpath(os.path.join(self.checkoutDir,"ArrayList.cs"))],0)
		
	# TODO ein Testfall für getChangeCountOfFileList, bei dem nicht alle change counts 0 sind, sollte noch ergänzt werden.
	
if __name__ == "__main__":
	unittest.main()
