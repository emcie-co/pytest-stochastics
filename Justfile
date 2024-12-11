# Semi-Automates Test
t: 
    poetry run pytest -vvv tests/test_func_tests.py > /dev/null 2> /dev/null && echo "failed" || echo "passed"
    poetry run pytest -vvv tests/test_func_tests.py --plan=default > /dev/null 2> /dev/null && echo "failed" || echo "passed"
    poetry run pytest -vvv tests/test_func_tests.py --plan weak > /dev/null 2> /dev/null && echo "passed" || echo "failed"
    poetry run pytest -vvv tests/test_func_tests.py --plan "strong" > /dev/null 2> /dev/null && echo "failed" || echo "passed"

tt: 
    poetry run pytest -vvv tests/test_func_tests.py --plan "weak" --junit-xml=testresults.xml --tap-combined ; echo $?

check:
    ruff check .
    mypy