.PHONY: qrc so clean test all

all:
	@echo 'Please use "python setup.py install" to build and'\
	      'install NICOS-ng.'

PREFIX = 
RCC = $(PREFIX)pyrcc4

qrc:
	$(RCC) -o nicos/gui/gui_rc.py resources/nicos-gui.qrc

so:
	rm -rf build
	python setup.py build_ext
	cp build/lib*/nicos/daemon/*.so nicos/daemon

clean:
	find -name '*.pyc' -exec rm {} +

test:
	@python test/run.py
