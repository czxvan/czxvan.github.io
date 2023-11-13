#========================================================================
#
# Goo library Makefile
#
# Copyright 1996-2003 Glyph & Cog, LLC
#
#========================================================================

SHELL = /bin/sh

srcdir = .


CFLAGS = -march=nocona -mtune=haswell -ftree-vectorize -fPIC -fstack-protector-strong -fno-plt -O2 -ffunction-sections -pipe -isystem /home/czx/miniconda3/include -DHAVE_CONFIG_H -I.. -I$(srcdir)
CXXFLAGS = -fvisibility-inlines-hidden -std=c++17 -fmessage-length=0 -march=nocona -mtune=haswell -ftree-vectorize -fPIC -fstack-protector-strong -fno-plt -O2 -ffunction-sections -pipe -isystem /home/czx/miniconda3/include -DHAVE_CONFIG_H -I.. -I$(srcdir)

CC = afl-clang
CXX = afl-clang++
AR = ar rc
RANLIB = /home/czx/miniconda3/bin/x86_64-conda-linux-gnu-ranlib

LIBPREFIX = lib

#------------------------------------------------------------------------

.SUFFIXES: .cc

.cc.o:
	$(CXX) $(CXXFLAGS) -c $<

#------------------------------------------------------------------------

CXX_SRC = \
	$(srcdir)/GHash.cc \
	$(srcdir)/GList.cc \
	$(srcdir)/GString.cc \
	$(srcdir)/gmem.cc \
	$(srcdir)/gmempp.cc \
	$(srcdir)/gfile.cc \
	$(srcdir)/FixedPoint.cc

C_SRC = \
	$(srcdir)/parseargs.c

#------------------------------------------------------------------------

all: $(LIBPREFIX)Goo.a

#------------------------------------------------------------------------

GOO_CXX_OBJS = GHash.o GList.o GString.o gmem.o gmempp.o gfile.o FixedPoint.o
GOO_C_OBJS = parseargs.o
GOO_OBJS = $(GOO_CXX_OBJS) $(GOO_C_OBJS)

$(LIBPREFIX)Goo.a: $(GOO_OBJS)
	rm -f $(LIBPREFIX)Goo.a
	$(AR) $(LIBPREFIX)Goo.a $(GOO_OBJS)
	$(RANLIB) $(LIBPREFIX)Goo.a

#------------------------------------------------------------------------

clean:
	rm -f $(GOO_OBJS) $(LIBPREFIX)Goo.a

#------------------------------------------------------------------------

depend:
	$(CXX) $(CXXFLAGS) -MM $(CXX_SRC) >Makefile.dep
	$(CC) $(CFLAGS) -MM $(C_SRC) >>Makefile.dep

include Makefile.dep
