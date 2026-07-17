.PHONY: run migrate migrations superuser shell

run:
	python manage.py runserver 0.0.0.0:8000

migrate:
	python manage.py migrate

migrations:
	python manage.py makemigrations

superuser:
	python manage.py createsuperuser

shell:
	python manage.py shell

startapp:
	@read -p "App name: " name; \
	mkdir -p apps/$$name; \
	python manage.py startapp $$name apps/$$name
