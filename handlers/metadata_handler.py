from typing import Any, Dict, List, Union
import fitz

from utils.logger import log_message

def metadata_handler(data: Union[Dict, List, Any], parent_key: str = "") -> Dict[str, Any]:
    """
    Handles metadata retrieval for documents.

    Returns:
        A dictionary with cleaned metadata.
        If the input is a dictionary, it flattens the structure and handles special cases like
        Notion-style date objects.
    """
    if not data:
        return {}
    
    cleaned_data = {}
    
    if isinstance(data, str) and data.lower().endswith('.pdf'):
        # Special handling for PDF metadata
        try:
            cleaned_data[parent_key] = data
            pdf_text = ""
            with fitz.open(data) as pdf_document:
                for page in pdf_document:
                    pdf_text += page.get_textbox(rect=page.rect)
            cleaned_data[f"{parent_key}_text"] = pdf_text
        except Exception as e:
            cleaned_data[f"{parent_key}_content"] = f"Error processing PDF: {e}"
            log_message(f"Error processing PDF metadata: {e}", "ERROR")
            return cleaned_data

    # Handle simple data types and None
    if isinstance(data, (str, int, float, bool)) or data is None:
        if parent_key:
            cleaned_data[parent_key] = data
            return cleaned_data
        
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
            cleaned_data.update(metadata_handler(value, new_key))
        return cleaned_data
    
    elif isinstance(data, list):
        # Handle lists by recursively processing each item
        for index, item in enumerate(data):
            new_key = f"{parent_key}_{index}" if parent_key else str(index)
            cleaned_data.update(metadata_handler(item, new_key))
        return cleaned_data
    
    return cleaned_data