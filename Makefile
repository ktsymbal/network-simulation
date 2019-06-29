.PHONY: venv
venv:
	[ -n "$(shell pip3 show virtualenv)" ] || pip3 install virtualenv

.PHONY: env
env: venv
	[ -d "env" ] || python3 -m venv env

.PHONY: deps
deps: env
	( \
       source env/bin/activate; \
       pip3 install -r requirements.txt; \
    )

.PHONY: run 
run: deps
	( \
       source env/bin/activate; \
       FLASK_APP=run.py flask run; \
    )