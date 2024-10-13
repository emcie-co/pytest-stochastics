t:
    poetry run pytest -v --tap-combined

tc:
    poetry run pytest -s -v --tap-combined


amend:
    git add . && git commit --amend --no-edit