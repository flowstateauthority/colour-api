import hashlib
import colorsys
import re
from flask import Flask, request, jsonify
from flask_cors import CORS

# --- This is your Flask app ---
app = Flask(__name__)
CORS(app)


# --- (YOUR COLOR GENERATOR FUNCTIONS - UNCHANGED) ---

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
        normalized_string = re.sub(r'[^0-9]', '', input_string)
    else:
        normalized_string = re.sub(r'[^a-zA-Z]', '', input_string).lower()

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

# --- (END OF COLOR FUNCTIONS) ---


# --- THIS IS THE UPDATED API ENDPOINT ---

@app.route('/generate-palette', methods=['POST'])
def generate_palette():
    """
    This function now accepts a LIST of names and a LIST of dates.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Get the lists from the request. Default to empty list.
        names_list = data.get('names', [])
        dates_list = data.get('dates', [])

        # We must have at least one name
        if not names_list:
            return jsonify({"error": "No names provided"}), 400

        # Process Names (This loop is the same and works perfectly)
        generated_name_colors = []
        for index, name in enumerate(names_list):
            color = generate_color_final(name, 'name', position_index=index)
            generated_name_colors.append({"name": name, "color": color})
        
        # --- NEW: Process Dates ---
        # We add a new loop to process all dates in the dates_list
        generated_date_colors = []
        for date_str in dates_list:
            color = generate_color_final(date_str, 'date')
            generated_date_colors.append({"name": date_str, "color": color})
        
        # Build the new response
        response = {
            "name_colors": generated_name_colors,
            "date_colors": generated_date_colors  # New key
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
