import io
from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import base64
from PIL import Image
import logging
from dotenv import load_dotenv
import math

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Set up logging
logging.basicConfig(filename='app.log', level=logging.INFO)

# Load environment variables from .env file
load_dotenv()

def latlon_to_pixel(lat, lon, zoom):
    # Function to convert lat/lon to pixel coordinates
    # Using a common formula for Web Mercator projection
    siny = min(max(math.sin(lat * (math.pi / 180)), -0.9999), 0.9999)
    x = 256 * (0.5 + lon / 360)
    y = 256 * (0.5 - math.log((1 + siny) / (1 - siny)) / (4 * math.pi))
    return int(x * (2 ** zoom)), int(y * (2 ** zoom))

@app.route('/save_map_image', methods=['POST'])
def save_map_image():
    data = request.json
    image_data = data['imageData']
    bbox = data['bbox']

    # Decode base64 image data
    image_data = base64.b64decode(image_data.split(',')[1])
    image = Image.open(io.BytesIO(image_data))

    # Get bounding box coordinates
    north = bbox['north']
    south = bbox['south']
    east = bbox['east']
    west = bbox['west']

    # Convert lat/lon to pixel coordinates
    zoom = 18  # Assuming zoom level used when capturing the image
    x1, y1 = latlon_to_pixel(north, west, zoom)
    x2, y2 = latlon_to_pixel(south, east, zoom)

    # Crop image to bounding box
    cropped_image = image.crop((x1, y1, x2, y2))

    # Save cropped image to the desired location
    save_path = os.path.join('D:\\', 'Tugas Akhir', 'coding_website', 'map_image.png')
    cropped_image.save(save_path)

    response = jsonify({'message': 'Map image saved successfully'})
    response.headers.add('Access-Control-Allow-Origin', '*')
    
    return response, 200

if __name__ == '__main__':
    logging.info("Starting Flask server...")
    app.run(debug=True)
