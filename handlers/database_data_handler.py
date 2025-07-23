from datetime import datetime, date
from typing import Any, Dict, List

def databaseDataHandler(data: Any, parent_key: str = "") -> Dict[str, Any]:
    """
    Handles metadata retrieval for database records.

    Returns:
        A dictionary with cleaned metadata.
        If the input is a dictionary, it flattens the structure and handles special cases.
    """
    if not data:
        return {}
    
    cleaned_data = {}
    
    for key, value in data:
        if isinstance(value, dict):
            # Recursively handle nested dictionaries
            cleaned_data.update(databaseDataHandler(value, parent_key=key))
        elif isinstance(value, (str, int, float, bool)) or value is None:
            cleaned_data[key] = value
        elif isinstance(value, (datetime, date)):
            # If data is a datetime object, convert it to ISO format
            cleaned_data[key] = value.isoformat()
        elif isinstance(value, list):
            # Handle lists by processing each item
            cleaned_data[key] = [databaseDataHandler(item, parent_key=key) for item in value]
        else:
            cleaned_data[key] = value
    
    
    
    
    
    return cleaned_data