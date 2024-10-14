# Tests:

## Test
t: 
    poetry run pytest -v

## Test with out/err captured
tc:
    poetry run pytest -s -v

## Collect but don't run
tco:
    poetry run pytest -s -v --co


# Git:

amend:
    git add . && git commit --amend --no-edit
