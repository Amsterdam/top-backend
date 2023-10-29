# TOP app (Toezicht op pad)
Dankzij de TOP app hebben toezichthouders Wonen veel informatie over zaken, adressen en bewoners bij de hand als zij op straat hun werk doen. Ook kunnen zij hun eigen looplijst samenstellen, op basis van instellingen die planners hebben klaargezet.

# Prerequisites

- [Docker](https://docs.docker.com/docker-for-mac/install/)

# Steps For Local Development

## Build:
```bash
docker-compose build
```

## Creating networks
Before running the project, you need to create the networks:
```bash
docker network create looplijsten_backend
docker network create top_and_zaak_backend_bridge
```
## Starting the development server:
Start the dev server for local development:
```bash
docker-compose up
```

## Importing fixtures dump
The Django project needs some configuration in order to run locally. It's possible to add these manually, but the quickest way is importing using fixtures from the acceptance environment. You can download these at: https://acc.api.top.amsterdam.nl/admin/planner/ by clicking on "DOWNLOAD JSON FIXTURE". You'll need to be logged in using an admin account first to access this url.

Move the json into the app directory on the root of your project, and run the following command

```bash
docker-compose run --rm api python manage.py loaddata <name of fixture>
```
Remove the json fixture after installing it.

## Creating a superuser:
```bash
docker-compose run --rm api python manage.py createsuperuser
```
A superuser can be used to access the Django backend

## Accessing the Django admin and adding users:
In order to generate lists you need at least 2 other users.
You can add other users easily through the Django admin.
Navigate to http://localhost:8000/admin and sign in using the superuser you just created.
Once you're in the admin, you can click on "add" in the User section to create new users.

## Accessing the API documentation

You can access the documentation at:
http://localhost:8000/api/v1/swagger/

## Bypassing Keycloak and using local development authentication:
It's possible to bypass Keycloak authentication when running the project locally.
To do so, make sure the LOCAL_DEVELOPMENT_AUTHENTICATION flag is set to True in docker-compose.yml.

## Bypassing multiprocessing and use threads:
The algorithm uses multiprocessing to select cases for a list. Multiprocessing sometimes freezes during local development. You will see a database SSL error:
```
    SSL error: decryption failed or bad record mac
    could not receive data from client: Connection reset by peer
    unexpected EOF on client connection with an open transaction
```
To fix this use threads instead by setting LOCAL_DEVELOPMENT_USE_THREADS to True in the .env file.


# Running commands
Run a command inside the docker container:

```bash
docker-compose run --rm api [command]
```

Running migrations:
```bash
docker-compose run --rm api python manage.py migrate
```

## Adding pre-commit hooks
You can add pre-commit hooks for checking and cleaning up your changes:
```
bash install.sh
```

You can also run the following command to ensure all files adhere to coding conventions:
```
bash cleanup.sh
```
This will autoformat your code, sort your imports and fix or find overal problems.

The Github actions will use the same bash script to check if the code in the pull requests follows the formatting and style conventions.

## Coding conventions and style
The project uses [Black](https://github.com/psf/black) for formatting and [Flake8](https://pypi.org/project/flake8/) for linting.

# Testing
## Running unit tests
Unit tests can be run using the following command:
```
docker-compose run --rm api python manage.py test
```

## Unit test in pull requests
Unit tests are part of the Github action workflows, and will be run when a pull request is made. This ensures tests are maintained and increases maintainability and dependability of automatic pull requests.
