#!/usr/bin/env python
#
# Copyright (c) 2010 Nokia Corporation and/or its subsidiary(-ies).
# All rights reserved.
# This component and the accompanying materials are made available
# under the terms of the License "Eclipse Public License v1.0"
# which accompanies this distribution, and is available
# at the URL "http://www.eclipse.org/legal/epl-v10.html".
#
# Initial Contributors:
# Nokia Corporation - initial contribution.
#
# Contributors:
#
# Description: 
# grokbuild
#

"""
Gathers performance metrics from the logs of a complex multi-step build.
Supports Helium 9 at the moment but is adaptable.

Can read from emake annotation files.  
"""

import sys
import os
import re
from  optparse import OptionParser
import annofile
import datetime


class UndeterminedBuildID(Exception):
	pass

class LogfileNotFound(Exception):
	pass

class HeliumLog(object):
	""" Some common properties of any log file in a helium build """
	filenamesuffix = None

	def __init__(self, logpath, buildid):

		self.logfilename = os.path.join(logpath, buildid + self.filenamesuffix)
		self.buildid = buildid

	@classmethod
	def findall(c, logpath):
		""" Find all the logs that are of this type - essentially also finds all builds 
		    which dumped their output in the same place """
		filename_re = re.compile('(.*/)?(?P<buildid>[^\\\/]*)' + c.filenamesuffix)
		logs = {}
		for f in os.listdir(logpath):
			m = filename_re.match(f)
			if m:
				file_buildid = m.groupdict()['buildid']
				logs[file_buildid] = os.path.join(logpath,f)
		return logs


	def __str__(self):
		return "<metric name='buildid'  value='%s'>\n" % self.buildid

class MainAntLog(HeliumLog):
	""" This is the promary log of the helium build.  Useful for obtaining the total build time. Not good for this if the build failed. """
	# output/logs/92_7952_201020_003_main.ant.log
	filenamesuffix = "_main.ant.log"
	timeformat = "%Y/%m/%d %H:%M:%S:%f" # e.g. Thu 2010/06/24 09:15:42:625 AM

	def __init__(self, logpath, buildid):
		super(MainAntLog,self).__init__(logpath, buildid)

		# Starting logging into y:\output\logs\mcl_7901_201024_20100623181534_main.ant.log at Wed 2010/06/23 21:16:12:972 PM
		# Stopping logging into y:\output\logs\mcl_7901_201024_20100623181534_main.ant.log from hlm:record task at Thu 2010/06/24 09:15:42:625 AM

		start_re = re.compile("Starting logging into [^ ]+ at ... ([^ ]+ +[^ ]+) .*")
		stop_re = re.compile("Stopping logging into [^ ]+ from [^ ]+ task at ... ([^ ]+ +[^ ]+) (AM)|(PM).*")
		start_time = None
		stop_time = None
		with open(self.logfilename) as f:
			for l in f:
				if start_time is None:
					m = start_re.match(l)
					if m:
						#sys.stderr.write("start TIME: %s\n" %m.groups()[0])
						start_time = datetime.datetime.strptime(m.groups()[0], self.timeformat)
						
				else: # if there are many stop lines then make sure the last one overrides the others
					m = stop_re.match(l)
					if m:
						stop_time = datetime.datetime.strptime(m.groups()[0], self.timeformat)
						#sys.stderr.write("stop TIME: %s\n" %m.groups()[0])

		#sys.stderr.write("build start/stop: %s / %s  from %s\n" % (start_time, stop_time, self.logfilename))
		build_duration = stop_time - start_time  # returns a timedelta object
		self.build_duration = build_duration.seconds +  86400 * build_duration.days  # seconds

	def __str__(self):
		return "<metric name='build_duration'  value='%d'>\n" % self.build_duration
		
class AntEnvLog(HeliumLog):
	# output/logs/92_7952_201020_003_ant_env.log
	filenamesuffix = "_ant_env.log"

	def __init__(self, logpath, buildid):
		super(AntEnvLog,self).__init__(logpath, buildid)

class TargetTimesLog(HeliumLog):
	"""Very useful timing data from Ant but does not get created in all builds by default (must be configured"""
	# output/logs/92_7952_custom_dilbert_201022_dilbert_targetTimesLog.csv
	filenamesuffix = "_targetTimesLog.csv"

	def __init__(self, logpath, buildid):
		super(TargetTimesLog,self).__init__(logpath, buildid)
		self.raptorsecs = 0
		self.totalsecs = 0

		with open(self.logfilename) as f:
			for ll in f:
				l = ll.rstrip("\n")
				#print self.logfilename
				#print "L:",l
				(rname, rsecs) = l.split(",")
				rsecs = int(rsecs)
				#print "rname, rsecs: %s %d"%(rname,rsecs)
				self.totalsecs += rsecs
				if rname == "compile-sbs":
					self.raptorsecs += rsecs

	def __str__(self):
		s = "<metric name='build_duration'  value='%s'>" % self.totalsecs  \
			+ "\n<metric name='raptor_duration'  value='%s'>\n" % self.raptorsecs
		return s

class RaptorAnnofile(object):
	"""Thin wrapper around the annofile class to make it relevant to this utility."""
	# Examples:
	# 92_7952_custom_dilbert_201022_dilbert_dfs_build_sf_tools_all.resource.emake.anno
	# 92_7952_custom_dilbert_201022_dilbert_dfs_build_sf_dfs_variants.default.emake.anno
	# 92_7952_201022_003_dfs_build_ncp_dfs_variants.resource_deps.emake.anno
	def __init__(self, filename, buildid):
		self.phase = ""
		self.filename = filename
		self.buildid = buildid

		self.annofile = annofile.Annofile(self.filename)

	def __str__(self):
		return "<annofile name='%s'\n" % os.path.split(self.filename)[-1] + "phase='%s'" % self.phase + ">\n" + str(self.annofile).replace("\n","\n    ") + "\n</annofile>\n"


class RaptorBuild(HeliumLog):
	"""Any Raptor logfile.  Mainly used for getting the names of the 
	annotation files which the annofile parser will use. Also gets
	the version of raptor and the total time taken by this particular
	invocation of Raptor"""
	def __init__(self, logpath, buildid, build):
		self.filenamesuffix = '_%s' % build
		super(RaptorBuild,self).__init__(os.path.join(logpath, "compile"), buildid)
		self.build = build

		if not os.path.isfile(self.logfilename):
			raise LogfileNotFound("missing log file: " + self.logfilename)
		
		self.annofile_names = []	
		self.build_duration = None
		run_time_re = re.compile("<info>Run time ([0-9]+) seconds</info>.*")
		
		emake_invocation_re = re.compile("<info>Executing.*--emake-annofile=([^ ]+) .*")
		sbs_version_re = re.compile("<info>sbs: version ([^\n\r]*).*")
		with open(self.logfilename) as f:
			sys.stderr.write("      parsing build log %s\n" % os.path.split(self.logfilename)[1])
			for l in f:
				m = run_time_re.match(l)
				if m:
					self.build_duration = int(m.groups()[0])
				
				m = emake_invocation_re.match(l)
				if m:
					(adir, aname) = os.path.split(m.groups()[0])
					if aname.find("pp")==-1: # no parallel parsing ones preferably
						sys.stderr.write("        found annotation file %s\n" % aname)
						self.annofile_names.append(os.path.join(logpath, "makefile", aname))

				m = sbs_version_re.match(l)
				if m:
					self.version = m.groups()[0]

		self.annofiles = []
		for p in self.annofile_names:
			self.annofiles.append(RaptorAnnofile(p, buildid))

	def __str__(self):
		return 	"<raptorbuild logfile='%s'>\n" % os.path.split(self.logfilename)[-1] + \
			" <metric name='raptor_version'  value='%s' />\n" % (self.version) + \
			" <metric name='raptor_duration_%s'  value='%d' />\n" % (self.build, self.build_duration) + \
			"".join([str(a) for a in self.annofiles]) + \
			"</raptorbuild>\n"
		


class HeliumBuild(object):
	"""A build with any version of Helium"""
	def __init__(self, logpath, buildid):
		self.buildid = buildid
		self.logpath = logpath
		self.logfiles=[]

	def __str__(self):
		return  self.buildid + \
			"\n"+[str(a) for a in self.annofiles] + "\n"

class Helium9Build(HeliumBuild):
	""" Filenames, structure etc conform to Helium 9 """
	def __init__(self, logpath, buildid):
		super(Helium9Build,self).__init__(logpath, buildid)
		self.mainantlog = MainAntLog(logpath, buildid)
		self.raptorbuilds = []

		# mcl_7901_201024_20100623181534_dfs_build_ncp_variants.build_input_compile.log
		# mcl_7901_201024_20100623181534_dfs_build_sf_variants.build_input_compile.log
		# mcl_7901_201024_20100623181534_dfs_build_winscw_dfs_build_winscw_input_compile.log
		#
		# ....but the problem is that the anno files have a slightly differing convention:
		#        92_7952_201022_003_dfs_build_ncp_dfs_variants.resource_deps.emake.anno
		#  _dfs_build_ncp_variants
		#  _dfs_build_ncp_dfs_variants
                # read the annofile names from inside the raptor log output
		for r in ["dfs_build_ncp_variants.build_input_compile.log","dfs_build_sf_variants.build_input_compile.log","dfs_build_winscw_dfs_build_winscw_input_compile.log", "ncp_symbian_build_symtb_input_compile.log"]:
			try:
				self.raptorbuilds.append(RaptorBuild(logpath, buildid, r))
			except LogfileNotFound, ex:
				sys.stderr.write(str(ex))

	def __str__(self):

		raptor_duration = reduce(lambda x, y: x + y,[y.build_duration for y in self.raptorbuilds],0)
		return "<heliumbuild ver='9' id='%s'>\n" % (self.buildid) + \
			"<metric name='total_duration'  value='%d' />\n" % (self.mainantlog.build_duration) + \
			"<metric name='raptor_duration'  value='%d' />\n" % (raptor_duration) + \
	 		"".join([str(a) for a in self.raptorbuilds ]) + \
	 		"</heliumbuild>\n"
		

class HeliumLogDir(object):
	"""Multiple builds can be done one after another (usually when rebuilding 
	   things that failed, apparently) and their logs left in the output dir.
	   The naming convention ensures that they don't overwrite each other.
	   This class identifies each build and tries to analyse them one by one."""
	def __init__(self, epocroot):
		self.logpath = os.path.join(epocroot, "output/logs")
		logs = MainAntLog.findall(self.logpath)
		self.builds = []
		
		for b in logs.keys():
			try:
				sys.stderr.write("  Found build with id %s\n" % b)
				build = Helium9Build(self.logpath, b)
				self.builds.append(build)
			except IOError,e:
				sys.stderr.write("  Buildid %s found but does not refer to a complete build\n" % b)
				sys.stderr.write(str(e)+"\n")

	def write(self, stream):
		for b in self.builds:
			stream.write(str(b)+"\n")
 

parser = OptionParser(prog = "grokbuild",
        usage = "%prog [-h | options] path to $EPOCROOT (logs usually are in $EPOCROOT/output/logs)")

(options, args) = parser.parse_args()

if len(args) == 0:
	sys.stderr.write("Need at least one argument: a path to the logs.")
	sys.exit(-1)

epocroot = args[0]
sys.stderr.write("Gathering Performance Metrics for %s\n" % epocroot)

b = HeliumLogDir(epocroot)
b.write(sys.stdout)
