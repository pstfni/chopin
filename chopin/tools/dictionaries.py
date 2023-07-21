"""Utilities to help with dictionaries."""


def flatten_dict(dictionary: dict) -> dict:
    """Flatten a dictionary with potential nested dictionaries, into a single dictionary.

    !!! example
        ```
        {'my_key': 'my_value',
         'a_nested_dict':
            {'my_key': 'my_value',
             'version': '1'
             }
        }
        ```
        will become:

        ```
        {'my_key': 'my_value',
         'a_nested_dict.my_key' : 'my_value',
         'a_nested_dict.version': '1'
        }
        ```
    """
    final_dict = {}
    for key, value in dictionary.items():
        if isinstance(value, dict):
            for sub_key, sub_value in value.items():
                final_dict[f"{key}.{sub_key}"] = sub_value
        else:
            final_dict[key] = value
    return final_dict
