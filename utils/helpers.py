import re

def get_postal_code(text):
    items = re.split('(\d{4})\s*([A-Z]{2})', text)
    postal_code_dict = {
        'address': items[0].strip(),
        'postal_code_area': items[1],
        'postal_code_street': items[2],
    }
    return postal_code_dict
