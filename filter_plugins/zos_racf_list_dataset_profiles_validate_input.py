from __future__ import absolute_import, division, print_function
from ansible.parsing.yaml.objects import AnsibleUnicode
from ansible.errors import AnsibleFilterTypeError
from typing import Dict, List, Any

import re

__metaclass__ = type

class FilterModule(object):
    def filters(self) -> dict:
        filters = {
            "zos_racf_list_dataset_profiles_validate_input": self.zos_racf_list_dataset_profiles_validate_input,
        }
        return filters
    
    def validate_parameters(self, input_content: Dict[str, Any]) -> Dict[str, Any]:
        possible_attrs: Dict[str, List[Any]] = {
            "all": [bool()],
            "at": [str()],
            "authuser": [bool()],
            "csdata": [bool()],
            "dataset": [str(), list(), AnsibleUnicode()],
            "dfp": [bool()],
            "generic": [bool()],
            "history": [bool()],
            "id": [str(), list()],
            "prefix": [str(), list(), AnsibleUnicode()],
            "statistics": [bool()],
            "tme": [bool()],
            "volume": [str(), list(), AnsibleUnicode()]
        }

        error_msgs: List[str] = []
        result: Dict[str, Any] = {}

        # Error if more than one exclusive parameters is specified        
        exclusive_attrs: List[str] = ["dataset", "id", "prefix"]
        if sum(1 for key in exclusive_attrs if input_content.get(key) is not None) > 1:
            error_msgs.append(f"Only one or none of the following attributes must be specified at time: {str(exclusive_attrs)}.")

        # Check each input parameter individually
        input_attrs = input_content.keys()
        for attr in input_attrs:
            if attr not in possible_attrs:
                error_msgs.append(f"Attribute '{attr}' is not a possible attribute. Possible attributes are {str(possible_attrs)}.")
                continue
            
            possible_types: List[type] = list(type(t) for t in possible_attrs[attr])
            
            if input_content[attr] == None:
                continue
            elif type(input_content[attr]) not in possible_types:
                error_msgs.append(f"Attribute '{attr}' was informed with type '{type(input_content[attr])}' must have a value of type: {str(possible_types)}.")
            elif isinstance(input_content[attr], (str, AnsibleUnicode)) and input_content[attr].strip() == "":
                error_msgs.append(f"Attribute '{attr}' was informed with an empty value. Either inform a correct value or do not inform this attribute.")
            elif isinstance(input_content[attr], list) and len(input_content[attr]) == 0:
                error_msgs.append(f"Attribute '{attr}' was informed as an empty list. Either inform the proper valeus or do not inform this attribute.")
            elif attr in ['dataset', 'prefix']:
                regex_dataset = r"^((?:[a-zA-Z@#$\*%][a-zA-Z@#$0-9\*%]{0,7}(?:\.(?!$)|$)){1,8})$"
                tmp_list = [input_content[attr]] if not isinstance(input_content[attr], list) else input_content[attr]
                for dsn in tmp_list:
                    if not re.match(regex_dataset, dsn):
                        error_msgs.append(f"Value '{dsn}' is not valid for attribute '{attr}'.")
                    else:
                        if len(dsn) > 44:
                            error_msgs.append(f"Attribute '{attr}' received a value that has more than 44 characters: {dsn}.")
            elif attr in ['volume']:
                tmp_list = [input_content[attr]] if not isinstance(input_content[attr], list) else input_content[attr]
                for vol in tmp_list:
                    if len(vol) > 6:
                        error_msgs.append(f"Attribute '{attr}' received a value that has more than 6 characters: {vol}.")

            if isinstance(input_content[attr], (bool, int)):
                result[attr] = input_content[attr]
            elif isinstance(input_content[attr], (str, AnsibleUnicode)):
                result[attr] = input_content[attr].upper()
            elif isinstance(input_content[attr], (list)):
                result[attr] = list(v.upper() if isinstance(v, str) else str(v) for v in input_content[attr])
                
        if len(error_msgs) > 0:
            raise AnsibleFilterTypeError("zos_racf_list_dataset_profiles_validate_input - validate_parameters - %s" % "\n".join(error_msgs))

        return(result)

    def zos_racf_list_dataset_profiles_validate_input(self, input_content):
        if not isinstance(input_content, dict):
            raise AnsibleFilterTypeError("zos_racf_list_dataset_profiles_validate_input - Filter must be applied on a dictionary.")

        result = self.validate_parameters(input_content)
        
        return(result)