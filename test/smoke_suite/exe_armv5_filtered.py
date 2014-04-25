#
# Copyright (c) 2009-2014 Microsoft Mobile and/or its subsidiary(-ies).
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
#

from raptor_tests import SmokeTest

def run():
	t = SmokeTest()
	t.id = "2"
	t.name = "exe_armv5_filtered"
	t.description = "Run exe_armv5 with a customised filter. Will create then" \
			+ " remove filter file"
	t.usebash = True
	t.command = "cp -f smoke_suite/test_resources/filter_test/testfilter.py ../raptor/plugins/testfilter.py " \
				"&& chmod 600 ../raptor/plugins/testfilter.py " \
				"&& sbs -b smoke_suite/test_resources/simple/bld.inf -c armv5 --filters=TestFilter " \
				"&& rm -f ../raptor/plugins/testfilter.py*"
	t.targets = [
		"$(EPOCROOT)/epoc32/release/armv5/udeb/test.exe",
		"$(EPOCROOT)/epoc32/release/armv5/udeb/test.exe.map",
		"$(EPOCROOT)/epoc32/release/armv5/urel/test.exe",
		"$(EPOCROOT)/epoc32/release/armv5/urel/test.exe.map"
		]
	t.addbuildtargets('smoke_suite/test_resources/simple/bld.inf', [
		"test_/armv5/udeb/test.o",
		"test_/armv5/urel/test.o"
	])
	t.mustmatch = [
		".*Test Passed!.*"
		]
	t.run()
	return t
