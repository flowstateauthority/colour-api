import hashlib
import colorsys
import re
from flask import Flask, request, jsonify
from flask_cors import CORS

# --- This is your Flask app ---
app = Flask(__name__)
CORS(app)


# --- (YOUR COLOUR GENERATOR FUNCTIONS) ---

def hsl_to_hex(h, s, l):
    h_norm = h / 360.0
    l_norm = l / 100.0
    s_norm = s / 100.0
    r, g, b = colorsys.hls_to_rgb(h_norm, l_norm, s_norm)
    r_int = round(r * 255)
    g_int = round(g * 255)
    b_int = round(b * 255)
    return f'#{r_int:02x}{g_int:02x}{b_int:02x}'

def generate_color_final(input_string, color_type="name", position_index=0):
    if color_type == 'date':
        # Date logic: Keep only numbers
        normalized_string = re.sub(r'[^0-9]', '', input_string)
    else:
        # Name logic: Keep letters AND numbers, then lowercase
        normalized_string = re.sub(r'[^a-zA-Z0-9]', '', input_string).lower()

    if not normalized_string:
        return "#CCCCCC" # Default grey

    hash_object = hashlib.sha256(normalized_string.encode('utf-8'))
    hex_hash = hash_object.hexdigest()
    
    hash_for_hue = hex_hash[0:5]
    hash_for_sat = hex_hash[5:10]
    
    hue_int = int(hash_for_hue, 16)
    sat_int = int(hash_for_sat, 16)
    hue = hue_int % 360
    
    saturation = (sat_int % 20) + 70
    
    if color_type == 'date':
        lightness = 40
    else:
        if position_index == 0:  # First name
            lightness = 75
        elif position_index == 1: # Second name
            lightness = 50
        else:
            lightness = 50 - ((position_index - 1) * 5)
            lightness = max(30, lightness) # Floor
        
    return hsl_to_hex(hue, saturation, lightness)

# --- (END OF COLOUR FUNCTIONS) ---


# --- THIS IS THE UPDATED API ENDPOINT ---

@app.route('/generate-palette', methods=['POST'])
def generate_palette():
    """
    This function now accepts a LIST of names and a LIST of dates.
    And uses UK spelling for "colour".
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Get the lists from the request. Default to empty list.
        names_list = data.get('names', [])
        dates_list = data.get('dates', [])

        if not names_list:
            return jsonify({"error": "No names provided"}), 400

        # Process Names
        generated_name_colours = [] # Renamed
        for index, name in enumerate(names_list):
            colour = generate_color_final(name, 'name', position_index=index) # Renamed
            generated_name_colours.append({"name": name, "colour": colour}) # Renamed
        
        # Process Dates
        generated_date_colours = [] # Renamed
        for date_str in dates_list:
            colour = generate_color_final(date_str, 'date') # Renamed
            generated_date_colours.append({"name": date_str, "colour": colour}) # Renamed
        
        # Build the new response
        response = {
            "name_colours": generated_name_colours, # Renamed
            "date_colours": generated_date_colours  # Renamed
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
