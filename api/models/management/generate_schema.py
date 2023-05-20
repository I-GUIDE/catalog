import json
import os

import typer

from api.models.schema import DatasetSchema


def main(output_name: str = "api/models/schema.json"):
    schema = embed_definitions()
    current_directory = absolute_directory(output_name)
    with open(current_directory, "w") as f:
        f.write(json.dumps(schema, indent=2))


def embed_definitions():
    schema = DatasetSchema.schema()
    return schema


def absolute_directory(output_name):
    current_directory = os.getcwd()
    current_directory = os.path.join(current_directory, output_name)
    return current_directory


if __name__ == "__main__":
    typer.run(main)
