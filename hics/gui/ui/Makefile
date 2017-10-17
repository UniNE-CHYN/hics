all: cameraoutput.py camera.py mainwindow.py scanner.py settings.py waterfall.py focus.py

%.py: %.ui
	pyuic4 -x $< > $@
