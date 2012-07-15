.PHONY: all gui install clean inplace test lint jenkinslintall jenkinslint changelint \
	check test-coverage install main-install install-gui main-install-gui release \
	xfixsmb help custom-all custom-inplace custom-install custom-clean

SHELL=/bin/bash

RCC = pyrcc4
PYTHON = /usr/bin/python

all:
	$(PYTHON) setup.py build -e "/usr/bin/env python"
	$(PYTHON) etc/set_version.py build/lib*
	-make custom-all

gui: lib/nicos/gui/gui_rc.py
	$(PYTHON) setup.py build -e "/usr/bin/env python"
	$(PYTHON) etc/set_version.py build/lib*
	-make custom-gui

lib/nicos/gui/gui_rc.py: resources/nicos-gui.qrc
	-$(RCC) -o lib/nicos/gui/gui_rc.py resources/nicos-gui.qrc

clean:
	rm -rf build
	find -name '*.pyc' -exec rm -f {} +
	-make custom-clean

inplace:
	rm -rf build
	$(PYTHON) setup.py build_ext
	cp build/lib*/nicos/daemon/*.so lib/nicos/daemon
	-make custom-inplace

T = test

test:
	@$(PYTHON) `which nosetests` $(T) -e test_stresstest -d $(O)

testall:
	@$(PYTHON) `which nosetests` $(T) -d $(O)

test-coverage:
	@$(PYTHON) `which nosetests` $(T) -d --with-coverage --cover-package=nicos --cover-html $(O)

lint:
	-pylint --rcfile=./pylintrc lib/nicos/

jenkinslintall:
	-pylint --rcfile=./pylintrc --files-output=y lib/nicos/

jenkinslint: PYFILESCHANGED:= $(shell git diff --name-status `git merge-base HEAD HEAD^` | sed -e '/^D/d' | sed -e 's/.\t//' |grep ".py")
jenkinslint:
	-if [[ -n "$(PYFILESCHANGED)" ]] ; then \
		pylint --rcfile=./pylintrc  --files-output=y  $(PYFILESCHANGED) ; else echo 'no python files changed' ; fi  

changelint: PYFILESCHANGED:= $(shell git diff --name-status `git merge-base HEAD HEAD^` | sed -e '/^D/d' | sed -e 's/.\t//'  | grep ".py")
changelint:
	-if [ -n "$(PYFILESCHANGED)" ] ; then \
		pylint --rcfile=./pylintrc  $(PYFILESCHANGED) ; else echo 'no python files changed' ;fi

check:
	pyflakes lib/nicos custom/*/lib

# get the instrument from the full hostname (mira1.mira.frm2 -> mira)
INSTRUMENT = $(shell hostname -f | cut -d. -f2)
ifneq "$(INSTRUMENT)" ""
  INSTRDIR = $(wildcard custom/$(INSTRUMENT))
endif

# check for install customizations
ifeq "$(INSTRDIR)" ""
  INSTALL_ERR = $(error No customization found for instrument $(INSTRUMENT). \
    If this is not the correct instrument, use 'make install INSTRUMENT=instname', \
    where instname can also be "test")
  # dummy targets
  custom-all:
  custom-inplace:
  custom-install:
  custom-clean:
else
  include $(INSTRDIR)/make.conf
  # check that the include provided all necessary variables
  ifeq "$(ROOTDIR)" ""
    INSTALL_ERR = $(error make.conf or cmdline must provide a value for ROOTDIR)
#  else ifeq "$(XXX)" ""
#    INSTALL_ERR = $(error make.conf or cmdline must provide a value for XXX)
  endif
endif

PYPLATFORM = $(shell $(PYTHON) -c 'import distutils.util as u; print u.get_platform()')
PYVERSION  = $(shell $(PYTHON) -c 'import sys; print sys.version[0:3]')

ifeq "$(V)" "1"
  VOPT = -v
endif

install: all main-install custom-install

main-install:
	$(INSTALL_ERR)
	@echo "============================================================="
	@echo "Installing NICOS to $(ROOTDIR)..."
	@echo "============================================================="
	install $(VOPT) -d $(ROOTDIR)/{bin,doc,etc,lib,log,pid,setups,scripts}
	rm -f $(VOPT) $(ROOTDIR)/lib/nicos/daemon/_pyctl.so
	cp -pr $(VOPT) build/lib.$(PYPLATFORM)-$(PYVERSION)/* $(ROOTDIR)/lib
	cp -pr $(VOPT) pid/README $(ROOTDIR)/pid
	chown $(SYSUSER):$(SYSGROUP) $(ROOTDIR)/pid
	cp -pr $(VOPT) log/README $(ROOTDIR)/log
	chown $(SYSUSER):$(SYSGROUP) $(ROOTDIR)/log
	cp -pr $(VOPT) etc/nicos-system $(ROOTDIR)/etc
	cp -pr $(VOPT) build/scripts-$(PYVERSION)/* $(ROOTDIR)/bin
	-cp -pr $(VOPT) doc/build/html/* $(ROOTDIR)/doc
	$(PYTHON) etc/create_nicosconf.py "$(SYSUSER)" "$(SYSGROUP)" "$(NETHOST)" \
	  "$(ROOTDIR)/setups" "$(SERVICES)" "$(ENVIRONMENT)" > $(ROOTDIR)/nicos.conf
	if [ -f $(INSTRDIR)/gui/defconfig.py ]; then \
	  cp -p $(INSTRDIR)/gui/defconfig.py "$(ROOTDIR)/lib/nicos/gui"; fi
	@echo "============================================================="
	@echo "Installing custom modules..."
	mkdir -p $(VOPT) $(ROOTDIR)/lib/nicos/$(INSTRUMENT)
	cp -pr $(VOPT) $(INSTRDIR)/lib/* $(ROOTDIR)/lib/nicos/$(INSTRUMENT)
	@echo "============================================================="
	@echo "Installing setups (not overwriting existing files)..."
	@for ifile in $(INSTRDIR)/setups/* ; do \
		if [ ! -f $(ROOTDIR)/setups/`basename $${ifile}` ]; then \
			echo $${ifile} '->' $(ROOTDIR)/setups; \
			cp -p $(VOPT) $${ifile} $(ROOTDIR)/setups; \
		fi \
	done
	@echo "============================================================="
	@echo "Everything is now installed to $(ROOTDIR)."
	@echo "Trying to create system-wide symbolic links..."
	@echo "============================================================="
	-ln -sf $(VOPT) -t /etc/init.d $(ROOTDIR)/etc/nicos-system
	-ln -sf $(VOPT) -t /usr/bin $(ROOTDIR)/bin/*
	@echo "============================================================="
	@echo "Finished."
	@echo "============================================================="

install-gui: gui main-install-gui custom-install-gui

main-install-gui:
	$(INSTALL_ERR)
	@echo "============================================================="
	@echo "Installing only NICOS GUI to $(ROOTDIR)..."
	@echo "============================================================="
	install $(VOPT) -d $(ROOTDIR)/{bin,lib,scripts}
	cp -pr $(VOPT) build/lib*/* $(ROOTDIR)/lib
	cp -pr $(VOPT) build/scripts*/nicos-gui $(ROOTDIR)/bin
	if [ -f $(INSTRDIR)/gui/defconfig.py ]; then \
	  cp -p $(INSTRDIR)/gui/defconfig.py "$(ROOTDIR)/lib/nicos/gui"; fi
	@echo "============================================================="
	@echo "Installing custom modules..."
	mkdir -p $(VOPT) $(ROOTDIR)/lib/nicos/$(INSTRUMENT)
	cp -pr $(VOPT) $(INSTRDIR)/lib/* $(ROOTDIR)/lib/nicos/$(INSTRUMENT)
	@echo "============================================================="
	@echo "The GUI is now installed to $(ROOTDIR)."
	@echo "Trying to create system-wide symbolic link..."
	@echo "============================================================="
	-ln -sf $(VOPT) -t /usr/bin $(ROOTDIR)/bin/nicos-gui
	@echo "============================================================="
	@echo "Finished, now running custom install..."
	@echo "============================================================="

release:
	make test
	cd doc; rm -r build/html; make html
	python setup.py sdist

fixsmb:
	chmod +x bin/*
	chmod +x etc/create_nicosconf.py
	chmod +x etc/nicos-system
	chmod +x custom/panda/bin/pausebutton

help:
	@echo "Important targets:"
	@echo "  all           - build everything for installation except GUI"
	@echo "  inplace       - build everything for running NICOS from here"
	@echo "  gui           - build GUI"
	@echo
	@echo "  install       - install everything except GUI"
	@echo "  install-gui   - install GUI"
	@echo "    Customization autoselected for install: $(INSTRUMENT)"
	@echo "    Use 'make INSTRUMENT=instname ...' to select a different one;"
	@echo "    instname can also be test"
	@echo
	@echo "Development targets:"
	@echo "  test          - run test suite"
	@echo "  test-coverage - run test suite with coverage reporting"
	@echo "  check         - check source with pyflakes"
	@echo "  lint          - check source with pylint"
	@echo "  release       - create tarball for official release"
