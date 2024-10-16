# Tests:

## Test
t: 
    poetry run pytest -v > /dev/null 2> /dev/null && echo "failed" || echo "passed"
    poetry run pytest -v --branch=default > /dev/null 2> /dev/null && echo "failed" || echo "passed"
    poetry run pytest -v --branch weak > /dev/null 2> /dev/null && echo "passed" || echo "failed"
    poetry run pytest -v --branch "strong" > /dev/null 2> /dev/null && echo "failed" || echo "passed"

# Git:

amend:
    git add . && git commit --amend --no-edit
