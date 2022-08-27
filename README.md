
# NetCDF 2 Zarr

The goal of this project is to access NetCDF4 files via [Zarr](https://zarr.readthedocs.io/en/stable/).

## Workflows

The application provides two workflows:

### JSON workflow

With the **JSON workflow** you can generate JSON metadata for NetCDF4 files to access them with `xarray` without using the NetCDF4 APIs. The conversion code was taken and modified from [this](https://medium.com/pangeo/fake-it-until-you-make-it-reading-goes-netcdf4-data-on-aws-s3-as-zarr-for-rapid-data-access-61e33f8fe685) article.

### Complete conversion

With the complete conversion a NetCDF4 can be converted to Zarr.

## Intake

Both workflow results can be shared and used via [Intake](https://github.com/intake/intake).
To load Intake catalogs use the following Python code in Jupyter:

```python
import intake

# Add the Intake catalog to the Intake GUI
intake.gui.add('http://<content-url>/<catalog-name>.yaml')

# Select a data source
intake.gui

# Load the data source
intake.gui.item().read_chunked()
```

Or without the GUI:

```python
catalog = intake.open_catalog('http://<content-url>/<catalog-name>.yaml')
catalog['<data-source-name>'].read_chunked()
```


## Getting Started

To run the project you need [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/).
Create a file name `docker-compose.prod.yaml` in the root folder of the project and fill in the following content. 
Replace any placeholder in `<...>`.

```yaml
version: "3.8"

services:

  angular-frontend:
    ports:
      - "80:80"
    build:
      args:
        - NC2ZARR_BACKEND_URL=http://<domain>:<backend-port>
        - NC2ZARR_CONTENT_URL=http://<domain>:<nginx-port>/intake-catalogs

  redis:
    volumes:
      - <redis-directory>:/data
    expose:
      - "6379"

  django:
    ports:
      - "<backend-port>:8000"
    volumes:
      - <input-directory>:/root/public/input
      - <output-directory>:/root/public/output
      - <intake-catalogs-directory>:/root/public/intake-catalogs
    environment:
      - NC2ZARR_INPUT=/root/public/input
      - NC2ZARR_OUTPUT=/root/public/output
      - NC2ZARR_INTAKE_CATALOGS=/root/public/intake-catalogs
      - NC2ZARR_POSTGRES_PASSWORD=<postgres-password>
      - NC2ZARR_POSTGRES_HOST=postgres
      - NC2ZARR_URL=<domain>

  worker:
    volumes:
      - <intake-catalogs-directory>:/home/python/intake-catalogs
      - <input-directory>:/home/python/input
      - <output-directory>:/home/python/output
    environment:
      - NC2ZARR_INPUT=/home/python/input
      - NC2ZARR_OUTPUT=/home/python/output
      - NC2ZARR_INTAKE_CATALOGS=/home/python/intake-catalogs
      - NC2ZARR_PROD=True
      - NC2ZARR_PUBLIC_URL=http://<domain>:<nginx-port>/
    deploy:
      replicas: <worker-count> # 2
      resources:
        limits:
          cpus: <worker-cpu-limit> # '0.25'
          memory: <worker-ram-limit> # 512M

  nginx:
    image: nginx
    ports:
      - "<nginx-port>:<nginx-port>"
    volumes:
      - <parent-directory-for-input-output-and-intake-catalogs>:/usr/share/nginx/html
    environment:
      - NGINX_HOST=<domain>
      - NGINX_PORT=<nginx-port>

  postgres:
    volumes:
      - <postgres-directory>:/var/lib/postgresql/data
    environment:
      - POSTGRES_PASSWORD=<postgres-password>


```

Now use Docker Compose to start the application:

```commandline
docker compose -f docker-compose.yaml -f docker-compose.prod.yaml up -d
```

## Contributing

When contributing to the project it is helpful to run the Django backend and the Angular frontend in an IDE.
Here are the steps necessary to run them successfully.

### Other services

For the backend other services from the `docker-compose.yaml` like Postgres are needed. You can start them with:

```commandline
docker-compose up -d
```

### Django backend

Set the following environment variables to configure your local environment:

```commandline
NC2ZARR_INPUT               = <absolute_path_to_input_folder> (e.g. Q:\nc2zarr\input on Windows)
NC2ZARR_OUTPUT              = <absolute_path_to_output_folder> (e.g. Q:\nc2zarr\output on Windows)
NC2ZARR_INTAKE_CATALOGS     = <absolute_path_to_intake_catalogs_folder> (e.g. Q:\nc2zarr\intake-catalogs on Windows)
NC2ZARR_POSTGRES_HOST       = localhost
NC2ZARR_POSTGRES_PASSWORD   = development
NC2ZARR_URL                 = localhost
PYTHONUNBUFFERED            = 1
```

Use the environment variables for all Django commands. 

To generate database migrations run:

```commandline
python manage.py makemigrations db
```

To apply database migrations run:

```commandline
python manage.py migrate
```

To start the server run: 

```commandline
python manage.py runserver 127.0.0.1:8001
```

### Angular frontend

For the frontend you need to have `npm` installed.

Then run:

```commandline
npm install
npm run start
```