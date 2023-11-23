from typing import Any, Dict

import yaml


def load_yaml(input_dict) -> Dict[str, Any]:
    return yaml.safe_load(input_dict)
