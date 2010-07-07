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
#

from raptor_tests import SmokeTest

def run():
	t = SmokeTest()
	t.description = "test mmpkeyword: traceon"
	t.id = "108a"
	t.name = "traceon_mmpkeyword"
	t.command = "sbs -b smoke_suite/test_resources/tracecompiler/traceon/group/bld.inf -c armv5.tracecompiler"	
	t.targets = [
		"$(EPOCROOT)/epoc32/release/armv5/udeb/traceon.exe",
		"$(EPOCROOT)/epoc32/release/armv5/urel/traceon.exe",
		"$(SBS_HOME)/test/smoke_suite/test_resources/tracecompiler/traceon/traces/traceon_exe/traceonTraces.h",
		"$(EPOCROOT)/epoc32/ost_dictionaries/traceon_exe_0x11100010_Dictionary.xml",
		"$(EPOCROOT)/epoc32/include/platform/symbiantraces/autogen/traceon_exe_0x11100010_TraceDefinitions.h"
		]
	t.addbuildtargets('smoke_suite/test_resources/tracecompiler/traceon/group/bld.inf', [
		"traceon_exe/armv5/udeb/traceon.o",
		"traceon_exe/armv5/urel/traceon.o",
		"traceon_exe/tracecompile_traceon_exe_11100010.done",
	])
	t.run()
	
	t.id = "108"
	t.name = "tracecompiler_new"
	return t

