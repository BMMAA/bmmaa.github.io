from bottle import Bottle, request, response, run, static_file
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import logging

app = Bottle()

# Serve the index.html file
@app.route('/')
def index():
    return static_file('index.html', root='./')

# Serve CSS files from the /css/ directory
@app.route('/css/<filename>')
def serve_css(filename):
    return static_file(filename, root='./css')

# Serve images and other static files
@app.route('/images/<filename>')
def serve_images(filename):
    return static_file(filename, root='./images')

# Serve other static files
@app.route('/<filename:path>')
def serve_static(filename):
    return static_file(filename, root='./')

# Define the endpoint for generating images (returning a static image for now)
@app.route('/generate-image', method='POST')
def generate_image():
    try:
        # Open the static image
        image_path = './images/AL-Suggestion1.jpg'
        img = Image.open(image_path).convert("RGBA")

        # Ensure the image is exactly 1024x1024
        img = img.resize((1024, 1024))

        # Add a watermark
        watermark_text = "KI-Posters"
        font_size = 100  # Fixed font size for the watermark
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except IOError:
            font = ImageFont.load_default()

        # Create a transparent image for the watermark
        watermark = Image.new('RGBA', img.size, (255, 255, 255, 0))
        watermark_draw = ImageDraw.Draw(watermark)

        # Position the watermark at the center and rotate it
        text_position = (img.width // 2, img.height // 2)
        watermark_draw.text(text_position, watermark_text, font=font, fill=(255, 255, 255, 170), anchor="mm")

        # Rotate the watermark to make it diagonal
        watermark = watermark.rotate(45, expand=0, center=(img.width // 2, img.height // 2))

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
