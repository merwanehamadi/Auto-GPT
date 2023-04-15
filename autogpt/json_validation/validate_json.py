import json
from jsonschema import Draft7Validator
from autogpt.config import Config
from autogpt.logs import logger

CFG = Config()


def validate_json(json_obj: object, schema_name: object) -> object:
    """
    :type schema_name: object
    :param schema_name:
    :type json_obj: object
    """
    with open(f"autogpt/json_schemas/{schema_name}.json", "r") as f:
        schema = json.load(f)
    validator = Draft7Validator(schema)
    if errors := sorted(validator.iter_errors(json_obj), key=lambda e: e.path):
        print("The JSON object is invalid. The following issues were found:")
        for error in errors:
            if CFG.debug_mode:
                logger.error("The following issues were found:")
                logger.error(f"Error: {error.message}")

        return {}
    else:
        print("The JSON object is valid.")
        return json_obj
