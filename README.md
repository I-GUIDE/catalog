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

(i.e. [https://localhost/api/schemas/schema.json](https://localhost/api/schemas/schema.json))