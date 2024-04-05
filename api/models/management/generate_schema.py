import json
import os

import typer

from api.models.schema import (
    GenericDatasetMetadata,
    HSNetCDFMetadata,
    HSRasterMetadata,
    HSResourceMetadata,
)


def main():
    def generate_schema_json(schema_model, folder_name):
        base_directory = "api/models/schemas"
        schema_file_path = os.path.join(base_directory, folder_name, "schema.json")
        schema = schema_model.schema()
        json_schema = schema_model.schema_json()

        # Have to run it a few times for the definitions to get updated before inserted into another model
        while "#/definitions/" in json_schema:
            for definition in schema["definitions"]:
                class_definition = schema["definitions"][definition]
                # replace allOf with a single definition
                json_schema = json_schema.replace(
                    f'"allOf": [{{"$ref": "#/definitions/{definition}"}}]',
                    json.dumps(class_definition)[1:-1]
                )
                #replace definition directly
                json_schema = json_schema.replace(
                    f'"$ref": "#/definitions/{definition}"',
                    json.dumps(class_definition)[1:-1]
                )
        embedded_schema = json.loads(json_schema)
        current_directory = absolute_directory(schema_file_path)
        with open(current_directory, "w") as f:
            f.write(json.dumps(embedded_schema, indent=2))

    schemas = get_schemas()
    for schema_item in schemas:
        generate_schema_json(schema_model=schema_item["model"], folder_name=schema_item["folder_name"])


def get_schemas():
    schemas = [
        {
            "model": GenericDatasetMetadata,
            "folder_name": "generic",
        },
        {
            "model": HSResourceMetadata,
            "folder_name": "hs_resource",
        },
        {
            "model": HSNetCDFMetadata,
            "folder_name": "netcdf",
        },
        {
            "model": HSRasterMetadata,
            "folder_name": "raster",
        },
    ]
    return schemas


def absolute_directory(output_name):
    current_directory = os.getcwd()
    current_directory = os.path.join(current_directory, output_name)
    return "/" + current_directory


if __name__ == "__main__":
    typer.run(main)
