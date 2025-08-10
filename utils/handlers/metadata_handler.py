from datetime import datetime, date
from typing import Any, Dict, List, Union

def data_handler(data: Union[Dict, List, Any], parent_key: str = "") -> Dict[str, Any]:
    """
    Handles metadata retrieval for any data source.

    Returns:
        A dictionary with cleaned metadata.
        If the input is a dictionary, it flattens the structure and handles special cases.
    """
    if not data:
        return {}

    cleaned_data = {}

    if isinstance(data, dict):
        # Special handling for Notion-style date objects
        if 'start' in data or 'end' in data:
            start_date = data.get('start')
            end_date = data.get('end')
            if start_date:
                cleaned_data[f"{parent_key}_start"] = str(start_date)
            if end_date:
                cleaned_data[f"{parent_key}_end"] = str(end_date)
            return cleaned_data

        # Generic dictionary flattening
        for key, value in data.items():
            new_key = f"{parent_key}_{key}" if parent_key else key
            cleaned_data.update(data_handler(value, new_key))
        return cleaned_data
    
    elif isinstance(data, list):
        # Handle lists by recursively processing each item
        for index, item in enumerate(data):
            new_key = f"{parent_key}_{index}" if parent_key else str(index)
            cleaned_data.update(data_handler(item, new_key))
        return cleaned_data

    elif isinstance(data, (str, int, float, bool)) or data is None:
        if parent_key:
            cleaned_data[parent_key] = data
        return cleaned_data

    elif isinstance(data, (datetime, date)):
        # If data is a datetime object, convert it to ISO format
        if parent_key:
            cleaned_data[parent_key] = data.isoformat()
        return cleaned_data
    
    else:
        if parent_key:
            cleaned_data[parent_key] = data
        return cleaned_data