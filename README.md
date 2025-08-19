# TOP app (Toezicht op pad)
Dankzij de TOP app hebben toezichthouders Wonen veel informatie over zaken, adressen en bewoners bij de hand als zij op straat hun werk doen. Ook kunnen zij hun eigen looplijst samenstellen, op basis van instellingen die planners hebben klaargezet.

## Steps for local development

### Prerequisites

- [Docker](https://docs.docker.com/docker-for-mac/install/)

### Build
```bash
docker compose -f docker-compose.local.yml build
```

### Creating networks
Before running the project, you need to create the networks:
```bash
docker network create top_network
docker network create top_and_zaak_backend_bridge
```

### Starting the development server
Start the dev server for local development:
```bash
docker compose -f docker-compose.local.yml up
```

### Importing & generating data
This project needs some data configuration in order to run locally. It's possible to add this manually, but the quickest way is to import fixtures and generate day settings for all teams.

#### Step 1: Import fixtures
First, import fixtures. This will add planner data, like teams, postal codes and visit configurations:

```bash
docker compose -f docker-compose.local.yml exec api python manage.py loaddata fixture
```

> Note: you can also download updated fixture data from the [acceptance environment](https://acc.api.top.amsterdam.nl/admin/planner/). You'll need to be logged in using an admin account first to access this url.
>
> Click on "DOWNLOAD JSON FIXTURE". Move the JSON file into the `app` directory on the root of your project, and run the above command with the filename (`top-planner-<date>.json`) appended to it. Remove the JSON fixture after importing it.

#### Step 2a: Provide `zaak-gateway` data (optional)
For step 2b to be able to generate all data properly, it is important that data from the `zaak-gateway` is available:

- Either make sure the `ZAKEN_API_URL` from the `.env` is reachable. You can do this by by running the `zaak-gateway` from the [zaken-backend](https://github.com/Amsterdam/zaken-backend) repo.
- If you're unable to do so, add `USE_ZAKEN_MOCK_DATA=True` to your local `.env.local` to make use of some mock data, but this may result in data inconsistencies later on.

> Note: if you're not running the `zaak-gateway` or haven't enabled mock data, the next command will still fill most data. In that case "team schedules" and "reasons" will not be available and therefore generated.

#### Step 2b: Generate planner data
Finally, generate planner day settings for each team. Do this by running the planner `generate_daysettings` command:

```bash
docker compose -f docker-compose.local.yml exec api python manage.py generate_daysettings
```

> Note: if you'd like to clean up and delete existing day settings, append the `--cleanup` flag to the above command.

### Creating a superuser
For accessing the Django admin during local development you'll have to become a `superuser`. This user should have the same `email` and `username` as the one that will be auto-created by the SSO login.

Run the following command to either create the user, or make the existing one a superuser:

```bash
sh bin/setup_superuser.sh <email>
```

### Accessing the Django admin and adding users:
In order to generate lists you need at least 2 other users.
You can add other users easily through the Django admin.

Navigate to http://localhost:8000/admin and sign in using the superuser you just created.
Once you're in the admin, you can click on "add" in the User section to create new users.

### Accessing the API documentation

You can access the documentation at:
http://localhost:8000/api/v1/swagger/

### Bypassing Keycloak and using local development authentication
It's possible to bypass Keycloak authentication when running the project locally. \
To do so, create `.env.local` file with:

```bash
LOCAL_DEVELOPMENT_AUTHENTICATION=False
```

### Bypassing multiprocessing and use threads
The algorithm uses multiprocessing to select cases for a list. Multiprocessing sometimes freezes during local development. You will see a database SSL error:

> SSL error: decryption failed or bad record mac
> could not receive data from client: Connection reset by peer
> unexpected EOF on client connection with an open transaction

To fix this use threads instead by creating/updating your `.env.local` file:

```bash
LOCAL_DEVELOPMENT_USE_MULTIPROCESSING=False
```

## Running commands
Run a command inside the docker container:

```bash
docker compose run --rm api [command]
```

Running migrations:
```bash
docker compose run --rm api python manage.py migrate
```

### Adding pre-commit hooks
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

### Coding conventions and style
The project uses [Black](https://github.com/psf/black) for formatting and [Flake8](https://pypi.org/project/flake8/) for linting.

## Testing

### Running unit tests
Unit tests can be run using the following command:
```bash
docker compose -f docker-compose.local.yml run --rm api python manage.py test
```

To run tests for a specific module, add a path:

```bash
docker compose -f docker-compose.local.yml run --rm api python manage.py test apps/cases
```

### Unit test in pull requests
Unit tests are part of the Github action workflows, and will be run when a pull request is made. This ensures tests are maintained and increases maintainability and dependability of automatic pull requests.
