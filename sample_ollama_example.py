import ollama
import base64
import time 
import os 
# no prxy for the localhost 
os.environ['NO_PROXY'] = 'localhost'
def encode_image(image_path):
    """Encodes an image to a base64 string."""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode('utf-8')

# Path to your image file
image_path = "test.jpg" # Replace with your image path

# Encode the image
base64_image = encode_image(image_path)

start_time = time.time()
# Send the image and prompt to Ollama
response = ollama.chat(
    model='deepseek-ocr',
    messages=[
        {
            'role': 'user',
            'content': 'Extract all the text from this image and format it as markdown.', # Or a more specific prompt like 'Extract structured data from this invoice.'
            'images': [base64_image]
        }
    ]
)
end_time = time.time() - start_time
print(f"Time elapsed: {end_time:.2f} seconds") 
print(response['message']['content'])
