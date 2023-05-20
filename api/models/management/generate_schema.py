import json
import os
from typing import Any, Dict

import typer
from pydantic import BaseModel

from api.models.schema import DatasetSchema


def main(output_name: str = "api/models/schema.json"):
    schema = DatasetSchema.schema()
    schema = embed_definitions(schema)
    current_directory = absolute_directory(output_name)
    with open(current_directory, "w") as f:
        f.write(json.dumps(schema, indent=2))


def embed_definitions(schema: Dict[str, Any]):
    for _, property in schema["properties"].items():
        any_of = property['anyOf'] if 'anyOf' in property else None
        if any_of:
            for item in any_of:
                # print(item)
                ref: str = item['$ref'] if '$ref' in item else None
                if ref:
                    # print(ref)
                    definition = ref[len("#/definitions/") :]
                    print(definition)

    # for definition in schema["definitions"]:
    #    print(definition)

    # for key, val in schema.items():
    # val = schema['properties'][key]
    # print(key)
    # print(val)
    return schema


def absolute_directory(output_name):
    current_directory = os.getcwd()
    current_directory = os.path.join(current_directory, output_name)
    return current_directory


if __name__ == "__main__":
    typer.run(main)
