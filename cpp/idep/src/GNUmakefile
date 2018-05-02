ifeq ($(wildcard .config.mk),.config.mk)
include .config.mk
first: all
else
first:
	@echo "run './configure' first"
endif

###################################################

TARGETS = adep$(LDSUF) cdep$(LDSUF) ldep$(LDSUF)

###################################################

SRC_IDEP = \
		   idep_adep.cpp \
		   idep_altab.cpp \
		   idep_alutil.cpp \
		   idep_binrel.cpp \
		   idep_cdep.cpp \
		   idep_fdepitr.cpp \
		   idep_ldep.cpp \
		   idep_namea.cpp \
		   idep_nimap.cpp \
		   idep_string.cpp \
		   idep_tokitr.cpp

SRC_ADEP = \
		   adep.cpp \
		   $(SRC_IDEP)

SRC_CDEP = \
		   cdep.cpp \
		   $(SRC_IDEP)

SRC_LDEP = \
		   ldep.cpp \
		   $(SRC_IDEP)

###################################################

all: $(TARGETS)

clean:
	rm -fr $(SRC_ADEP:.cpp=.o) $(SRC_LDEP:.cpp=.o) $(SRC_CDEP:.cpp=.o)

distclean: clean
	rm -f $(TARGETS)


###################################################

adep$(LDSUF) : $(SRC_ADEP:.cpp=.o)
	$(LDD) $(LDOUT)$@ $^

cdep$(LDSUF) : $(SRC_CDEP:.cpp=.o)
	$(LDD) $(LDOUT)$@ $^

ldep$(LDSUF) : $(SRC_LDEP:.cpp=.o)
	$(LDD) $(LDOUT)$@ $^

###################################################

%$.o : %.cpp
	$(CXX) $(CXXOUT)$@ $(CXXFLAGS) $<

