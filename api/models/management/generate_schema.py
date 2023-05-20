import os

import typer

from api.models.schema import DatasetSchema


def main(output_name: str = "api/models/schema.json"):
    schema = DatasetSchema.schema()
    current_directory = os.getcwd()
    current_directory = os.path.join(current_directory, output_name)
    with open(current_directory, "w") as f:
        f.write(DatasetSchema.schema_json(indent=2))


if __name__ == "__main__":
    typer.run(main)
