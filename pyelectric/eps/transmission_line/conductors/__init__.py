import json
import os
from typing import Any, Dict, Optional

conductors_dict: Optional[Dict[str, Any]] = None
conductors_json_path = os.path.join('pyelectric', 'eps', 'transmission_line', 'conductors', 'conductors.json')


def get_by_name(conductor_name: str) -> Dict[str, Any]:
    global conductors_dict
    if conductors_dict is None:
        with open(conductors_json_path) as f:
            conductors_dict = json.load(f)
    print(conductors_dict)
    return conductors_dict[conductor_name]


def get_radius_by_name(conductor_name: str) -> float:
    return get_by_name(conductor_name)['radius']


def get_gmr_by_name(conductor_name: str) -> float:
    return get_by_name(conductor_name)['gmr']
