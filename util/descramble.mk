# Copyright (c) 2006-2010 Nokia Corporation and/or its subsidiary(-ies).
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
# Utility makefile 
#
#

TARGET:=sbs_descramble
SOURCES:=$(SBS_HOME:\=/)/util/descramble/descramble.cpp 

ifeq ($(filter win,$(HOSTPLATFORM)),win)
CFLAGS:=-DWIN32
LDFLAGS:=
else
CFLAGS:=
LDFLAGS:=-lpthread
endif

$(eval $(cppprogram))
