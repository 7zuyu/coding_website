import requests
import cv2
import numpy as np
import base64

def display_polygon_image():
    url = "http://localhost:5000/get_polygon_image"  # URL to the Flask endpoint
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        image_data = data['image']
        
        # Log the length of the received image data
        print(f"Received image data length: {len(image_data)} bytes")

        # Add padding to the Base64 string
        image_data = add_padding(image_data)
        
        # Decode Base64 string to bytes
        try:
            image_bytes = base64.b64decode(image_data)
        except Exception as e:
            print(f"Failed to decode image data: {e}")
            return
        
        # Convert bytes data to numpy array
        np_arr = np.frombuffer(image_bytes, np.uint8)
        
        # Decode image array to an OpenCV image
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        
        # Check if image is valid
        if img is None:
            print("Failed to decode image.")
            return
        
        # Log image shape
        print(f"Image shape: {img.shape}")
        
        # Display the image using OpenCV
        cv2.imshow("Polygon Image", img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print(f"Failed to get image: {response.status_code}")

def add_padding(base64_string):
    return base64_string + '=' * (4 - len(base64_string) % 4)

if __name__ == "__main__":
    display_polygon_image()
