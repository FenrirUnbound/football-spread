FILENAME:="google_appengine_1.9.10.zip"
SDK:="https://storage.googleapis.com/appengine-sdks/featured/$(FILENAME)"

clean:
	find . -name "*.pyc" -exec rm -rf {} \;
	if [ -d venv ] ; \
	then \
		rm -rf venv ; \
	fi;

test: clean
	PYTHONPATH="." ./tests/RunTests.py

venv: venv/bin/activate
venv/bin/activate: requirements.txt
	test -d venv || virtualenv venv
	. venv/bin/activate; pip install -Ur requirements.txt
	touch venv/bin/activate

google_appengine:
	wget $(SDK) -nv || curl -O $(SDK)
	unzip -q $(FILENAME)

build: venv google_appengine
	. venv/bin/activate; PYTHONPATH=./tests/ nosetests --with-xunit --with-coverage --cover-html --cover-erase --with-gae --gae-lib-root=./google_appengine/ ./tests/func/ ./tests/unit/ ./tests/test_lib/