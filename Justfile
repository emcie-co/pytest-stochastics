t:
    poetry run pytest -v --tap-combined

tc:
    poetry run pytest -s -v --tap-combined

tco:
    poetry run pytest -s -v --co --tap-combined


amend:
    git add . && git commit --amend --no-edit