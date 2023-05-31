# catalogapi
I-GUIDE Catalog API

### Getting Started
```console
cp .env.template .env
make build
make up
```

### Formatting
```console
make format
```

### Schema Generation
```console
make schema
```

### JSON Schema file serving
Files in `api/models/schemas` are served at `/api/schemas`

(i.e. [https://localhost/api/schemas/dataset.json](https://localhost/api/schemas/dataset.json))

### Atlas
For discovery to work the mongo db must be configured to use Atlas, search indexes created and a couple of adminstrative settings must be configured. Reach out to sblack@cuahsi.org if you need a db for development work.

1. Update the .env file with Atlas credentials
```console
KEYCLOAK_ISSUER=https://auth.cuahsi.io/realms/HydroShare

DB_USERNAME={username}
DB_PASSWORD={password}
DB_HOST=cluster0.iouzjvv.mongodb.net
DATABASE_NAME=iguide_{user}
DB_PROTOCOL=mongodb+srv

TESTING=True
```

2. Login and submit a record to create all the collections
3. Run `triggers/management/change_streams_pre_and_post.py`
4. Create the catalog and typeahead indexes from `atlas/` (TODO detailed instructions)

### Triggers
Triggers have their own docker image (`docker/Dockerfile-triggers`).  There are two triggers:
1. `triggers/update_catalog.py` listens to the Submission collections and updates the discovery collection accordingly.
2. `triggers/update_typeahead.py` listens to the discovery collection and updates the typeahead collection accordingly.

The triggers have not been configured with a `resume_token` yet.

### Frontend
A vue application.  `docker/Dockerfile-fronted` deploys a development version of the vue application and is slow to start up.  Deployments should use `frontend/Dockerfile` as it is configured to generate the static files and then serve them.
