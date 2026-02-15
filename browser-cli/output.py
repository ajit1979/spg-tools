"""
Output formatting and masking utilities.
"""

import json


def format_output(data, output_format='plain'):
    """
    Format extracted data for output.
    
    Args:
        data: Dict of extracted tokens
        output_format: 'plain' or 'json'
        
    Returns:
        Formatted string
    """
    if output_format == 'json':
        return json.dumps(data, indent=2)
    else:
        # Plain text format
        lines = []
        for key, value in data.items():
            if value is not None:
                lines.append(f"{key.upper()}: {value}")
        
        # Add export statement if we have the required tokens
        jsessionid = data.get('jsessionid')
        token = data.get('token') or data.get('x-signavio-id')
        
        if jsessionid and token:
            lines.append("")  # Empty line for separation
            export_stmt = f"export SIGNAVIO_COOKIE=\"JSESSIONID={jsessionid}; token={token};\" X_SIGNAVIO_ID={token}"
            lines.append(export_stmt)
        
        return '\n'.join(lines) if lines else "No tokens extracted"


def mask_sensitive_data(data, mask_char='*', show_chars=4):
    """
    Mask sensitive data while keeping first/last characters visible.
    
    Args:
        data: Dict of tokens
        mask_char: Character to use for masking
        show_chars: Number of characters to show at start/end
        
    Returns:
        Dict with masked values
    """
    masked = {}
    
    for key, value in data.items():
        if value is None:
            masked[key] = None
        elif len(value) <= show_chars * 2:
            # Too short to mask meaningfully
            masked[key] = mask_char * len(value)
        else:
            # Show first and last characters
            start = value[:show_chars]
            end = value[-show_chars:]
            middle_length = len(value) - (show_chars * 2)
            masked[key] = f"{start}{mask_char * middle_length}{end}"
            
    return masked
