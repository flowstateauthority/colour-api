import hashlib
import colorsys
import re
from flask import Flask, request, jsonify
from flask_cors import CORS

# --- This is your Flask app ---
app = Flask(__name__)
# This line allows your website to talk to this API
CORS(app)


# --- (YOUR COLOR GENERATOR FUNCTIONS) ---

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

# --- (END OF YOUR COLOR FUNCTIONS) ---


# --- This is your API "ENDPOINT" ---

@app.route('/generate-palette', methods=['POST'])
def generate_palette():
    """
    This function waits for a web request, gets the names,
    runs your color generator, and sends the colors back.
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        names_list = data.get('names')
        dob = data.get('dob')

        if not names_list or not dob:
            return jsonify({"error": "Missing 'names' list or 'dob'"}), 400

        generated_colors = []
        for index, name in enumerate(names_list):
            color = generate_color_final(name, 'name', position_index=index)
            generated_colors.append({"name": name, "color": color})
            
        date_color = generate_color_final(dob, 'date')
        
        response = {
            "name_colors": generated_colors,
            "date_color": {"name": dob, "color": date_color}
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# We no longer need the app.run() block at the end.
# The server (Gunicorn) will find the 'app' object automatically.