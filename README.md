# Ansible Role - z/OS RACF List DATASET profiles

The Ansible role `zos_racf_list_dataset_profiles` will execute z/OS RACF LISTDSD command to list one or more DATASET profiles and parse information from its output, considering the variables informed by the user on the specified z/OS host(s).

## Requirements

Python and Z Open Automation Utilities must be installed on the remote z/OS system, since the module `zos_tso_command` from the collection `ibm.ibm_zos_core` is used along the role.

## Role Variables

This role has multiple variables. The descriptions and defaults for all these variables can be found in the **[`defaults/main.yml`](/defaults/main.yml)** file and **[`meta/argument_specs.yml`](/meta/argument_specs.yml)**, together with a detailed description below:

| Variable | Description | Optional? |
| -------- | ----------- | :-------: |
| **[`show_output`](/meta/argument_specs.yml)** | Display the output at the end | Yes<br>(default: `true`) |
| **[`parameters`](/meta/argument_specs.yml)** | Parameters to be used on the LISTDSD command | Yes<br>(default: `{}`) |

### Detailed structure of variable `parameters`, based on IBM RACF documentation (see **[LISTDSD (List data set profile)](https://www.ibm.com/docs/en/zos/3.1.0?topic=syntax-listdsd-list-data-set-profile)**):

| Variable | Attribute | Type | Optional? |
| -------- | --------- | :--: | :-------: |
| `parameters` | `all` | boolean | Yes |
| `parameters` | `at` | string | Yes |
| `parameters` | `authuser` | boolean | Yes |
| `parameters` | `csdata` | boolean | Yes|
| `parameters` | `dataset` | string or list[string] | Yes |
| `parameters` | `dfp` | boolean | Yes |
| `parameters` | `generic` | boolean | Yes |
| `parameters` | `history` | boolean | Yes |
| `parameters` | `id` | string or list[string] | Yes |
| `parameters` | `prefix` | string or list[string] | Yes |
| `parameters` | `statistics` | boolean | Yes |
| `parameters` | `tme` | boolean | Yes |
| `parameters` | `volume` | string or list[string] | Yes |

Note that all attributes of `parameters` are optional. If `parameters` is not specified or specified with no attributes, it will take the same effect of running the RACF command LISTDSD with no attributes.

Attributes `dataset`, `id` and `prefix` are mutually exclusive, as per the IBM RACF documentation.

`dfp`, `tme` and `csdata` are not currently supported. Although you can inform the attribute and its value, the segment is not being parsed from the output of the command(s).

## Dependencies

None.

## Example Playbook

On the scenario below, the role `zos_racf_list_dataset_profiles` is being used to list the generic DATASET profiles `SYS1.DSNAAA.SDSNLOAD`, `SYS1.PARMLIB` and `DB2.*`. It is also being requested to list `AUTHUSER` information

    - hosts: zos_server
      roles:
        - role: zos_racf_list_dataset_profiles
          parameters:
            authuser: true
            dataset:
              - SYS1.DSNAAA.SDSNLOAD
              - SYS1.PARMLIB
              - DB2SUP.*
            generic: true
          show_output: true

## Sample Output

When this role is executed, it will execute the RACF LISTDSD command, failing and displaying its output if return code of the TSO command is greater than 4, otherwise it will end successfully.

A fact named `zos_racf_list_dataset_profiles_details` will be set if the role runs successfully, containing parsed detail information of the output of the commands that were executed. It will be displayed if `show_output` is set to `true`.

    "zos_racf_list_dataset_profiles_details": [
        {
            "command": "LISTDSD DATASET('SYS1.DSNAAA.SDSNLOAD') AUTHUSER GENERIC",
            "content": [
                {
                    "msg": "NO RACF DESCRIPTION FOUND FOR SYS1.DSNAAA.SDSNLOAD"
                }
            ],
            "rc": 4
        },
        {
            "command": "LISTDSD DATASET('SYS1.PARMLIB') AUTHUSER GENERIC",
            "content": [
                {
                    "access_counts": {
                        "alter": null,
                        "control": null,
                        "read": null,
                        "update": null
                    },
                    "access_list": [
                        {
                            "access": "ALTER",
                            "access_count": null,
                            "id": "MVSSUP"
                        }
                    ],
                    "access_list_conditional": [],
                    "auditing": [
                        "ALL(READ)"
                    ],
                    "categories": [],
                    "creation_date_day": "100",
                    "creation_date_year": "20",
                    "creation_group": "SYSTEM",
                    "csdata": null,
                    "dataset_type": "NON-VSAM",
                    "dfp": null,
                    "dsns": [],
                    "erase": false,
                    "globalaudit": [],
                    "installation_data": null,
                    "is_generic": true,
                    "last_change_date_day": null,
                    "last_change_date_year": null,
                    "last_reference_date_day": null,
                    "last_reference_date_year": null,
                    "level": "00",
                    "notify": null,
                    "owner": "MVSSUP",
                    "profile_name": "SYS1.PARMLIB",
                    "seclabel": null,
                    "security_level": null,
                    "tme": null,
                    "universal_access": "READ",
                    "warning": false,
                    "your_access": "ALTER"
                }
            ],
            "rc": 0
        },
        {
            "command": "LISTDSD DATASET('DB2SUP.*') AUTHUSER GENERIC",
            "content": [
                {
                    "access_counts": {
                        "alter": null,
                        "control": null,
                        "read": null,
                        "update": null
                    },
                    "access_list": [
                        {
                            "access": "ALTER",
                            "access_count": null,
                            "id": "DB2SUP"
                        }
                    ],
                    "access_list_conditional": [],
                    "auditing": [
                        "ALL(READ)"
                    ],
                    "categories": [],
                    "creation_date_day": "350",
                    "creation_date_year": "24",
                    "creation_group": "SYSTEM",
                    "csdata": null,
                    "dataset_type": "NON-VSAM",
                    "dfp": null,
                    "dsns": [],
                    "erase": false,
                    "globalaudit": [],
                    "installation_data": null,
                    "is_generic": true,
                    "last_change_date_day": null,
                    "last_change_date_year": null,
                    "last_reference_date_day": null,
                    "last_reference_date_year": null,
                    "level": "00",
                    "notify": null,
                    "owner": "DB2SUP",
                    "profile_name": "DB2SUP.*",
                    "seclabel": null,
                    "security_level": null,
                    "tme": null,
                    "universal_access": "READ",
                    "warning": false,
                    "your_access": "ALTER"
                }
            ],
            "rc": 0
        }
    ]

## License

This role is licensed under [Apache License, Version 2.0](http://www.apache.org/licenses/LICENSE-2.0).

## Author Information

This role was created in 2025 by Luiggi Torricelli.
