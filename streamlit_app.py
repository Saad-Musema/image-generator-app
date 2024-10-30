import streamlit as st
import requests
import io
from PIL import Image

# Set the API URL and headers for Stable Diffusion
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-3.5-large"
headers = {"Authorization": "Bearer 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"}

def query(image_bytes, prompt):
    """Function to send a request to the Stable Diffusion image generation API."""
    # Prepare the payload with the initial image and the text prompt
    files = {'file': image_bytes}
    data = {"inputs": prompt}

    # Send the request to the API
    response = requests.post(API_URL, headers=headers, files=files, data=data)
    
    if response.status_code == 200:
        return response.content
    else:
        st.error(f"Error: {response.status_code} - {response.text}")
        return None

# Streamlit app layout
st.title("Image-to-Image Generation with Stable Diffusion")

# User input for the prompt
prompt = st.text_input("Enter a prompt for image generation:", "A futuristic city landscape")

# Image upload option
uploaded_file = st.file_uploader("Upload an initial image to condition the generation", type=["jpg", "jpeg", "png"])

if st.button("Generate Image"):
    with st.spinner("Generating image..."):
        # Prepare the image bytes if an image is uploaded
        if uploaded_file is not None:
            # Load the uploaded image
            uploaded_image = Image.open(uploaded_file)
            # Convert the uploaded image to bytes for the API call
            buffer = io.BytesIO()
            uploaded_image.save(buffer, format="PNG")
            image_bytes = buffer.getvalue()

            # Make the API request for image generation
            generated_image_bytes = query(io.BytesIO(image_bytes), prompt)

            if generated_image_bytes is not None:
                try:
                    # Load the generated image from bytes
                    generated_image = Image.open(io.BytesIO(generated_image_bytes))
                    
                    # Display the generated image
                    st.image(generated_image, caption=prompt, use_column_width=True)
                except Exception as e:
                    st.error(f"Could not open the generated image: {e}")
        else:
            st.error("Please upload an initial image.")
