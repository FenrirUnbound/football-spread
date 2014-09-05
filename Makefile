
clean:
	find . -name "*.pyc" -exec rm -rf {} \;

test: clean
	PYTHONPATH="." ./tests/RunTests.py
