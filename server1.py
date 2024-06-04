from flask import Flask, jsonify, request, send_file, make_response
from flask_cors import CORS, cross_origin
from shapely.geometry import Polygon, Point
from PIL import Image, ImageDraw
import pymysql
import logging
import matplotlib
matplotlib.use('Agg')  # Gunakan backend non-GUI sebelum import pyplot
import matplotlib.pyplot as plt
import io
from io import BytesIO
import numpy as np
import base64
import cv2
import geopandas as gpd
import json
import os
from dotenv import load_dotenv
from datetime import datetime

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

# Set up logging
logging.basicConfig(filename='app.log', level=logging.INFO)

# Load environment variables from .env file
load_dotenv()

def create_connection():
    try:
        logging.info("Trying to establish connection to the database...")
        connection = pymysql.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', 'root123'),
            database=os.getenv('DB_NAME', 'tugas_akhir'),
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        logging.info("Connection to the database established successfully!")
        return connection
    except pymysql.Error as e:
        logging.error(f"Error: {e}")
        return None

# Function to find light intensity based on coordinates
def find_intensity(latitude, longitude, month, year):
    try:
        connection = create_connection()
        if connection is None:
            return None

        with connection.cursor() as cursor:
            query = f"SELECT {month}_{year} FROM data_{year} WHERE Latitude BETWEEN %s AND %s AND Longitude BETWEEN %s AND %s"
            cursor.execute(query, (latitude - 0.02, latitude + 0.02, longitude - 0.02, longitude + 0.02))
            result = cursor.fetchone()

            return result[f"{month}_{year}"] if result else None
    except Exception as e:
        logging.error(f"Error in find_intensity: {e}")
        return None
    finally:
        if connection:
            connection.close()

@app.route('/get_intensitas', methods=['POST'])
def get_intensitas():
    data = request.json

    if not all(key in data for key in ['latitude', 'longitude', 'month', 'year']):
        return jsonify({'error': 'Data latitude, longitude, bulan, dan tahun diperlukan'}), 400

    input_latitude = float(data['latitude'])
    input_longitude = float(data['longitude'])
    month = data['month']
    year = data['year']

    intensitas = find_intensity(input_latitude, input_longitude, month, year)

    if intensitas is None:
        return jsonify({'error': 'Data tidak ditemukan'}), 404
    else:
        response = jsonify({'intensitas': intensitas})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

def generate_grid_coordinates(polygon_coords, step=0.04):
    polygon = Polygon(polygon_coords)
    min_x, min_y, max_x, max_y = polygon.bounds
    
    grid_coordinates = []
    for x in np.arange(min_x, max_x, step):
        for y in np.arange(min_y, max_y, step):
            point = Point(x, y)
            if polygon.contains(point):
                grid_coordinates.append((y, x))  # Reversed due to (lat, lon) convention
    
    # If no grid coordinates are generated, use the centroid
    if not grid_coordinates:
        centroid = polygon.centroid
        grid_coordinates.append((centroid.y, centroid.x))

    return grid_coordinates

@app.route('/get_coordinates_with_intensity', methods=['POST'])
def get_coordinates_with_intensity():
    data = request.json

    if 'features' not in data:
        return jsonify({'error': 'Data features diperlukan'}), 400

    selectedMonth = data['month']
    selectedYear = data['year']
    step = data.get('step', 0.04)
    
    coordinates = []
    intensity_data = {}
    total_GHI = 0  # Inisialisasi total GHI
    total_GHI1 = 0
    
    for feature in data['features']:
        geometry = feature['geometry']
        if geometry['type'] == 'Polygon':
            polygon_coords = geometry['coordinates'][0]
            grid_coords = generate_grid_coordinates(polygon_coords, step)
            for lat, lon in grid_coords:
                intensity = find_intensity(lat, lon, selectedMonth, selectedYear)
                coordinates.append({'latitude': lat, 'longitude': lon, 'intensitas': intensity})
                intensity_data[f"{lat},{lon}"] = intensity
                if intensity is not None:
                    total_GHI1 += intensity  # Menambahkan GHI ke total
                    total_GHI = total_GHI1*24*28

    # Kirim respons ke klien dengan total GHI
    return jsonify({'coordinates': coordinates, 'intensity_data': intensity_data, 'total_GHI': total_GHI})

@app.route('/get_intensity_plot', methods=['POST'])
def get_intensity_plot():
    data = request.json

    if 'features' not in data:
        return jsonify({'error': 'Data features diperlukan'}), 400

    selectedMonth = data['month']
    selectedYear = data['year']
    step = data.get('step', 0.04)
    
    coordinates = []
    intensity_data = []

    for feature in data['features']:
        geometry = feature['geometry']
        if geometry['type'] == 'Polygon':
            polygon_coords = geometry['coordinates'][0]
            grid_coords = generate_grid_coordinates(polygon_coords, step)
            for lat, lon in grid_coords:
                intensity = find_intensity(lat, lon, selectedMonth, selectedYear)
                if intensity is not None:
                    coordinates.append((lon, lat))  # Longitude, Latitude
                    intensity_data.append(intensity)

    # Generate the plot
    plt.figure(figsize=(7, 4))
    sc = plt.scatter(
        [coord[0] for coord in coordinates], 
        [coord[1] for coord in coordinates], 
        c=intensity_data, 
        cmap='viridis'
    )
    plt.colorbar(sc, label='GHI')  # Add color bar to show GHI values
    plt.title('Intensity Data')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.grid(True)

    # Save the plot to a BytesIO object
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)

    filename = 'plot_image.png'  # Nama file yang diinginkan
    plt.savefig(filename, format='png')
    
    # Send the image as a response
    response = make_response(send_file(filename, mimetype='image/png'))
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/save_polygon_image', methods=['POST'])
def save_polygon_image():
    data = request.json

    # Pastikan data poligon diterima dengan benar
    if 'features' not in data:
        return jsonify({'error': 'Data features diperlukan'}), 400

    # Panggil fungsi untuk menyimpan poligon sebagai gambar
    # Anda perlu menyesuaikan fungsi ini sesuai dengan kebutuhan Anda
    save_polygon_as_image(data['features'])

    return jsonify({'message': 'Polygon image saved successfully'})

def save_polygon_as_image(polygon_features):
    fig, ax = plt.subplots(figsize=(8, 6))

    # Plot the polygon
    for feature in polygon_features:
        geometry = feature['geometry']
        if geometry['type'] == 'Polygon':
            coords = np.array(geometry['coordinates'][0])
            ax.fill(coords[:,0], coords[:,1], alpha=0.5)  # Plot the polygon
        elif geometry['type'] == 'MultiPolygon':
            for poly_coords in geometry['coordinates']:
                coords = np.array(poly_coords[0])
                ax.fill(coords[:,0], coords[:,1], alpha=0.5)  # Plot the polygon

    # Set title and axis labels
    ax.set_title('Polygon Image')
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')

    # Save the plot to a file
    filename = 'polygon_image.png'  # Nama file yang diinginkan
    plt.savefig(filename, format='png')

    # Tambahkan penanganan kesalahan jika perlu
    plt.close(fig)  # Tutup plot agar tidak memakan memori lebih lanjut

    return 'polygon_image.png'  # Return the path to the saved image

@app.route('/save_map_image', methods=['POST'])
@cross_origin()
def save_map_image():
    data = request.json
    image_data = data['imageData']

    # Decode base64 image data
    image_data = base64.b64decode(image_data.split(',')[1])  # Split and decode the base64 part
    image = Image.open(io.BytesIO(image_data))

    # Simpan gambar ke lokasi yang diinginkan
    save_path = os.path.join('D:\\', 'Tugas Akhir', 'coding_website', 'map_image.png')
    image.save(save_path)

    response = jsonify({'message': 'Gambar peta berhasil disimpan'})
    response.headers.add('Access-Control-Allow-Origin', '*')  # Menambahkan header CORS
    
    return response, 200

@app.route('/save_cropped_map_image', methods=['POST'])
def save_cropped_map_image():
    data = request.json
    image_data = data['image']
    
    # Menghapus prefix base64
    image_data = image_data.replace('data:image/png;base64,', '')
    
    # Dekode base64 string
    image = Image.open(BytesIO(base64.b64decode(image_data)))
    
    # Simpan gambar
    image.save('cropped_map_image.png')

    return jsonify({'message': 'Gambar berhasil disimpan!'})

if __name__ == '__main__':
    app.run(debug=True)

# Log server startup
logging.info("Starting Flask server...")
