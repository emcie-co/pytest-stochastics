# Semi-Automates Test
t: 
    poetry run pytest -v > /dev/null 2> /dev/null && echo "failed" || echo "passed"
    poetry run pytest -v --plan=default > /dev/null 2> /dev/null && echo "failed" || echo "passed"
    poetry run pytest -v --plan weak > /dev/null 2> /dev/null && echo "passed" || echo "failed"
    poetry run pytest -v --plan "strong" > /dev/null 2> /dev/null && echo "failed" || echo "passed"

tt: 
    poetry run pytest -v --plan "strong" --junit-xml=testresults.xml --tap-combined > log; echo $?

check:
    ruff check .
    mypy