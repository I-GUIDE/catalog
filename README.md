# I-GUIDE Catalog

The I-GUIDE Catalog is part of of the [I-GUIDE Cyberinfrastructure Platform](https://i-guide.io/platform/). The Platform supports collaborative research along with computation and data-intensive geospatial problem solving. Within the context of the I-GUIDE Platform, the goal of the Catalog is to allow users to find, explore, and share data, models, code, software, hosted services, computational resources, and learning materials. A major goal of the catalog is to make these resources "actionable" - e.g., once a user finds a resource, they should be able to interact with the content of the resource and/or launch it into an appropriate analysis or computational environment for execution and exploration.

## Deployment

The I-GUIDE Catalog is currently deployed at [https://iguide.cuahsi.io/](https://iguide.cuahsi.io/). 

## Issue Tracker

Please report any bugs or ideas for enhancements to the I-GUIDE Catalog issue tracker:

[https://github.com/I-GUIDE/catalog/issues](https://github.com/I-GUIDE/catalog/issues)

## License

The I-GUIDE Catalog is released under the BSD 3-Clause License. This means that you can do what you want with the code [provided that you inlude the BSD copyright and license notice in it](https://www.tldrlegal.com/license/bsd-3-clause-license-revised).

©2024 I-GUIDE Developers. 

## Sponsors and Credits

[![NSF-2118329](https://img.shields.io/badge/NSF-2118329-blue.svg)](https://nsf.gov/awardsearch/showAward?AWD_ID=2118329)

This material is based upon work supported by the National Science Foundation (NSF) under award [2118329](https://www.nsf.gov/awardsearch/showAward?AWD_ID=2118329). Any opinions, findings, conclusions, or recommendations expressed in this material are those of the authors and do not necessarily reflect the views of the NSF.

## Developer Information

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
OIDC_ISSUER=https://orcid.org/

DB_USERNAME={username}
DB_PASSWORD={password}
DB_HOST=cluster0.iouzjvv.mongodb.net
DATABASE_NAME=iguide_{user}
DB_PROTOCOL=mongodb+srv

HYDROSHARE_META_READ_URL=https://www.hydroshare.org/hsapi2/resource/%s/json/
HYDROSHARE_FILE_READ_URL=https://www.hydroshare.org/hsapi/resource/%s/files/

TESTING=True
```

2. Login and submit a record to create all the collections
3. Run `triggers/management/change_streams_pre_and_post.py`
4. Create the catalog and typeahead indexes from `atlas/` (TODO detailed instructions)

### Triggers
Triggers have their own docker image (`docker/triggers/Dockerfile`).  There are two triggers:
1. `triggers/update_catalog.py` listens to the Submission collections and updates the discovery collection accordingly.
2. `triggers/update_typeahead.py` listens to the discovery collection and updates the typeahead collection accordingly.

The triggers have not been configured with a `resume_token` yet.

### Frontend
A vue application.  `docker/frontend/Dockerfile` deploys a development version of the vue application and is slow to start up.  Deployments should use `frontend/Dockerfile` as it is configured to generate the static files and then serve them.
