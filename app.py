from bottle import Bottle, request, response, run, static_file
import os
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import logging

app = Bottle()

# Function to read API key from a file
def get_api_key(filepath='api_key.txt'):
    try:
        with open(filepath, 'r') as file:
            return file.read().strip()
    except FileNotFoundError:
        logging.error("API key file not found.")
        return None

# Load the API key
API_KEY = get_api_key()

# Directory to save original images
ORIGINAL_IMAGE_DIR = './original_images'

# Create directory if it doesn't exist
os.makedirs(ORIGINAL_IMAGE_DIR, exist_ok=True)

# Serve the index.html file
@app.route('/')
def index():
    return static_file('index.html', root='./')

# Serve CSS files from the /css/ directory
@app.route('/css/<filename>')
def serve_css(filename):
    return static_file(filename, root='./css')

# Serve images
@app.route('/images/<filename>')
def serve_images(filename):
    return static_file(filename, root='./images')

# Serve other static files like images or JavaScript
@app.route('/<filename:path>')
def serve_static(filename):
    return static_file(filename, root='./')

# Define the endpoint for generating images
@app.route('/generate-image', method='POST')
def generate_image():
    try:
        if not API_KEY:
            response.status = 500
            return {"error": "Server configuration error: API key is missing"}

        prompt = request.forms.get('prompt')
        size = request.forms.get('size', '1024x1024')

        if not prompt:
            response.status = 400
            return {"error": "Prompt is required"}

        # API request to OpenAI
        headers = {
            'Authorization': f'Bearer {API_KEY}',
            'Content-Type': 'application/json'
        }
        data = {
            'model': 'dall-e-2',
            'prompt': prompt,
            'n': 1,
            'size': size
        }
        api_url = 'https://api.openai.com/v1/images/generations'
        api_response = requests.post(api_url, headers=headers, json=data)

        if api_response.status_code != 200:
            response.status = api_response.status_code
            return {"error": api_response.json().get('error', 'Unknown error')}

        # Get the image URL from the response
        image_url = api_response.json()['data'][0]['url']
        image_response = requests.get(image_url)

        if image_response.status_code != 200:
            response.status = image_response.status_code
            return {"error": "Failed to fetch image"}

        # Open the image and ensure it's in RGBA mode and 1024x1024 size
        img = Image.open(BytesIO(image_response.content)).convert("RGBA")
        img = img.resize((1024, 1024))

        # Save the original image locally
        original_image_path = os.path.join(ORIGINAL_IMAGE_DIR, f'{prompt.replace(" ", "_")}_original.png')
        img.save(original_image_path, format='PNG')

        # Add a watermark
        watermark_text = "KI-Posters"
        font_size = 100  # Fixed font size for the watermark
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except IOError:
            font = ImageFont.load_default()

        # Create a transparent image for the watermark with the same size
        watermark = Image.new('RGBA', img.size, (255, 255, 255, 0))
        watermark_draw = ImageDraw.Draw(watermark)

        # Position the watermark at the center and rotate it
        text_position = (watermark.width // 2, watermark.height // 2)
        watermark_draw.text(text_position, watermark_text, font=font, fill=(255, 255, 255, 170), anchor="mm")

        # Rotate the watermark to make it diagonal
        watermark = watermark.rotate(45, expand=0, center=(watermark.width // 2, watermark.height // 2))

        # Composite the watermark with the original image
        watermarked_img = Image.alpha_composite(img, watermark)

        # Convert back to RGB before saving as JPEG/PNG
        watermarked_img = watermarked_img.convert("RGB")

        # Save the watermarked image to a byte stream
        img_byte_arr = BytesIO()
        watermarked_img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)

        # Return the watermarked image
        response.content_type = 'image/png'
        return img_byte_arr.read()
    
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        response.status = 500
        return {"error": "An internal error occurred"}

# Run the Bottle application
if __name__ == '__main__':
    run(app, host='localhost', port=8080, debug=True)
