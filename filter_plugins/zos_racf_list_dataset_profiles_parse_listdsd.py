from __future__ import absolute_import, division, print_function
from ansible.parsing.yaml.objects import AnsibleUnicode
from ansible.errors import AnsibleFilterTypeError
from typing import Any, Dict, List, Union
import re

__metaclass__ = type

class FilterModule(object):
    def filters(self):
        filters = {
            "zos_racf_list_dataset_profiles_parse_listdsd": self.zos_racf_list_dataset_profiles_parse_listdsd,
        }
        return filters
    
    def zos_racf_list_dataset_profiles_parse_listdsd(self, cmd_response: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not isinstance(cmd_response, list):
            raise AnsibleFilterTypeError("zos_racf_list_dataset_profiles_parse_listdsd - Filter must be applied on a list of dictionaries.")

        result: List[Dict[str, Any]] = []

        # For each output inside of the list,
        for tso_cmd_output in cmd_response:
            if not tso_cmd_output.get("command") or not tso_cmd_output.get("content"):
                raise AnsibleFilterTypeError("zos_racf_list_dataset_profiles_parse_listdsd - The dictionaries inside the list must contain 'command' and 'content' attributes.")
            
            # For LISTDSD output parsing,
            if isinstance(tso_cmd_output["content"], list):
                content: str = '\n'.join(tso_cmd_output["content"])
            elif isinstance(tso_cmd_output["content"], (str, AnsibleUnicode)):
                content: str = tso_cmd_output["content"]
            else:
                raise AnsibleFilterTypeError("zos_racf_list_dataset_profiles_parse_listdsd - The 'content' attribute must be a list of strings or a string.")

            # Remove 'lines' attribute from output
            tso_cmd_output.pop('lines')

            # Make sure content is separated in case there is a list of profiles inside
            separate_content = re.sub(r"INFORMATION FOR DATASET ", r"<sep>INFORMATION FOR DATASET ", content).split('<sep>')
            separate_content = separate_content[1:] if len(separate_content) > 1 else separate_content

            inner_result: List[Dict[str, Any]] = []

            # For each profile listed inside the content
            for joined_content in separate_content:
                # Replace to enable the future regex expression to correctly parse the last section
                joined_content = re.sub(r"\n$", r"\n \n", joined_content)

                not_found_msg = re.match(r"(NO +RACF +DESCRIPTION +FOUND +FOR +\S+|NO +DATASETS +LISTED)", joined_content)
                if not_found_msg:
                    inner_result.append({"msg": not_found_msg.group()})
                    continue

                profile_name: Union[str, None] = next(iter(re.findall(r"INFORMATION +FOR +DATASET +(\S+)", joined_content)), None)

                is_generic: bool = True if re.match(r"INFORMATION +FOR +DATASET +\S+ *(\(G\))", joined_content) else False

                general_info: Union[List[str], None] = next(iter(re.findall(r"\nLEVEL +OWNER +UNIVERSAL +ACCESS +WARNING +ERASE *\n-+ +-+ +-+ +-+ +-+ *\n *(\S+) +(\S+) +(\S+) +(\S+) +(\S+) *", joined_content)), None)
                level: Union[str, None] = general_info[0] if general_info else None
                owner: Union[str, None] = general_info[1] if general_info else None
                universal_access: Union[str, None] = general_info[2] if general_info else None
                warning: Union[bool, None] = (True if general_info[3] == "YES" else False) if general_info else None
                erase: Union[bool, None] = (True if general_info[4] == "YES" else False) if general_info else None
                
                auditing_match: Union[str, None] = next(iter(re.findall(r"\nAUDITING\n-+\n *(.+) *\n", joined_content)), None)
                auditing: List[str] = auditing_match.split(',') if auditing_match else []
                
                notify_match: str = next(iter(re.findall(r"\nNOTIFY\n-+\n(.+)\n", joined_content)), '')
                notify: Union[str, None] = notify_match if notify_match not in ["NO USER TO BE NOTIFIED", ""] else None

                general_info_2: Union[List[str], None] = next(iter(re.findall(r"\nYOUR +ACCESS +CREATION +GROUP +DATASET +TYPE *\n-+ +-+ +-+ *\n *(\S+) *(\S+) *(\S+) *\n", joined_content)), None)
                your_access: Union[str, None] = general_info_2[0] if general_info_2 else None
                creation_group: Union[str, None] = general_info_2[1] if general_info_2 else None
                dataset_type: Union[str, None] = general_info_2[2] if general_info_2 else None

                globalaudit_match: Union[str, None] = next(iter(re.findall(r"\nGLOBALAUDIT\n-+\n *(.+) *\n", joined_content)), None)
                globalaudit: List[str] = globalaudit_match.split(',') if globalaudit_match and globalaudit_match not in ['NONE'] else []
                
                installation_data: Union[str, None] = next(iter(re.findall(r"\nINSTALLATION DATA *\n-+ *\n *([\s\S]+?)\n \n", joined_content)), None)
                
                security_level_match: Union[str, None] = next(iter(re.findall(r"\n *SECURITY +LEVEL *\n-+ *\n *(.+?) *\n", joined_content)), None)
                security_level: Union[int, None] = int(security_level_match) if security_level_match and security_level_match not in ["NO SECURITY LEVEL"] else None
                
                categories_match: Union[str, None] = next(iter(re.findall(r"\n *CATEGORIES *\n-+ *\n *(.+?) *\n", joined_content)), None)
                categories: List[str] = categories_match.split(',') if categories_match and categories_match not in ["NO CATEGORIES"] else []
                
                seclabel_match: Union[str, None] = next(iter(re.findall(r"\n *SECLABEL *\n-+ *\n *(.+?) *\n", joined_content)), None)
                seclabel: Union[str, None] = seclabel_match if seclabel_match and seclabel_match not in ["NO SECLABEL"] else None
                
                general_info_3: Union[List[str], None] = next(iter(re.findall(r"\n *CREATION +DATE +LAST +REFERENCE +DATE +LAST +CHANGE +DATE *\n.+\n-+ +-+ +-+ *\n *(\S+) +(\S+) +(NOT +APPLICABLE +FOR +GENERIC +PROFILE|\S+) *(\S*) *(\S*) *(\S*) *\n", joined_content)), None)
                creation_date_day: Union[str, None] = general_info_3[0] if general_info_3 else None
                creation_date_year: Union[str, None] = general_info_3[1] if general_info_3 else None
                last_reference_date_day: Union[str, None] = general_info_3[2] if general_info_3 and general_info_3[2] not in ["NOT APPLICABLE FOR GENERIC PROFILE"] else None
                last_reference_date_year: Union[str, None] = general_info_3[3] if general_info_3 and general_info_3[2] not in ["NOT APPLICABLE FOR GENERIC PROFILE"] else None
                last_change_date_day: Union[str, None] = general_info_3[4] if general_info_3 and general_info_3[2] not in ["NOT APPLICABLE FOR GENERIC PROFILE"] else None
                last_change_date_year: Union[str, None] = general_info_3[5] if general_info_3 and general_info_3[2] not in ["NOT APPLICABLE FOR GENERIC PROFILE"] else None

                access_counts_match: Union[List[str], None] = next(iter(re.findall(r"\n *ALTER +COUNT +CONTROL +COUNT +UPDATE +COUNT +READ +COUNT *\n-+ +-+ +-+ +-+ *\n *(NOT APPLICABLE FOR GENERIC PROFILE|\S*) *(\S*) *(\S*) *(\S*) *\n", joined_content)), None)
                access_counts: Dict[str, Union[int, None]] = {
                    "alter": int(access_counts_match[0]) if access_counts_match and access_counts_match[0] not in ["NOT APPLICABLE FOR GENERIC PROFILE"] else None,
                    "control": int(access_counts_match[1]) if access_counts_match and access_counts_match[0] not in ["NOT APPLICABLE FOR GENERIC PROFILE"] else None,
                    "update": int(access_counts_match[2]) if access_counts_match and access_counts_match[0] not in ["NOT APPLICABLE FOR GENERIC PROFILE"] else None,
                    "read": int(access_counts_match[3]) if access_counts_match and access_counts_match[0] not in ["NOT APPLICABLE FOR GENERIC PROFILE"] else None,
                }
                
                access_list_match: Union[str, None] = next(iter(re.findall(r"\n *ID +ACCESS *(?:ACCESS +COUNT|)\n-+ +-+(?: +-+|) *\n *([\s\S]+?) *\n \n", joined_content)), None)
                if access_list_match and access_list_match not in ["NO ENTRIES IN STANDARD ACCESS LIST"]:
                    access_list: List[Dict[str, Union[str, int, None]]] = [{"id": i, "access": j, "access_count": int(k) if k != '' else None} for i, j, k in re.findall(r"(\S+) +(\S+) *(\S*) *", access_list_match)]
                else:
                    access_list = []
                
                access_list_conditional_match: Union[str, None] = next(iter(re.findall(r"\n *ID +ACCESS +(?:ACCESS +COUNT +|)CLASS +ENTITY +NAME *\n[ -]+\n *([\s\S]+?) *\n \n", joined_content)), None)
                if access_list_conditional_match and access_list_conditional_match not in ["NO ENTRIES IN CONDITIONAL ACCESS LIST"]:
                    access_list_conditional: List[Dict[str, Union[str, int, None]]] = [{"id": i, "access": j, "access_count": int(k) if m != '' else None, "class": l if m != '' else k, "entity_name": m if m != '' else l} for i, j, k, l, m in re.findall(r"(\S+) +(\S+) +(\S+) +(\S+) *(\S*) *", access_list_conditional_match)]
                else:
                    access_list_conditional = []

                dsns_match: Union[str, None] = next(iter(re.findall(r"\n *CATALOGUED +DATA +SETS +AFFECTED +BY +PROFILE +CHANGE *\n[ -]+\n *([\s\S]+?) *\n \n", joined_content)), None)
                dsns: List[str] = re.sub(r" +\n", r"\n", dsns_match).split('\n') if dsns_match and dsns_match not in ["NO CATALOGUED DATA SETS WILL BE AFFECTED"] else []

                # TBD - At this moment, I could not find an output of a sample TME segment.
                tme = None
                
                # TBD - At this moment, I could not find an output of a sample CSDATA segment.
                csdata = None
                
                # TBD - At this moment, I could not find an output of a sample DFP segment.
                dfp = None
                inner_result.append({
                    "profile_name": profile_name,
                    "is_generic": is_generic,
                    "level": level,
                    "owner": owner,
                    "universal_access": universal_access,
                    "warning": warning,
                    "erase": erase,
                    "auditing": auditing,
                    "notify": notify,
                    "your_access": your_access,
                    "creation_group": creation_group,
                    "dataset_type": dataset_type,
                    "globalaudit": globalaudit,
                    "installation_data": installation_data,
                    "security_level": security_level,
                    "categories": categories,
                    "seclabel": seclabel,
                    "creation_date_day": creation_date_day,
                    "creation_date_year": creation_date_year,
                    "last_reference_date_day": last_reference_date_day,
                    "last_reference_date_year": last_reference_date_year,
                    "last_change_date_day": last_change_date_day,
                    "last_change_date_year": last_change_date_year,
                    "access_counts": access_counts,
                    "access_list": access_list,
                    "access_list_conditional": access_list_conditional,
                    "dsns": dsns,
                    "tme": tme,
                    "csdata": csdata,
                    "dfp": dfp,
                })

            tso_cmd_output["content"] = inner_result    
            result.append(tso_cmd_output)
        return result