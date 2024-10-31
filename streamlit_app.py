import streamlit as st
from io import BytesIO
import IPython
import json
import os
from PIL import Image
import requests


STABILITY_KEY = os.getenv("STABILITY_API") 
print(os.getenv("STABILITY_API"))  # Ensure this prints your API key


def send_generation_request(
    host,
    params,
):
    headers = {
        "Accept": "image/*",
        "Authorization": f"Bearer {STABILITY_KEY}"
    }

    # Encode parameters
    files = {}
    image = params.pop("image", None)
    mask = params.pop("mask", None)
    if image is not None and image != '':
        files["image"] = open(image, 'rb')
    if mask is not None and mask != '':
        files["mask"] = open(mask, 'rb')
    if len(files) == 0:
        files["none"] = ''

    # Send request
    print(f"Sending REST request to {host}...")
    response = requests.post(
        host,
        headers=headers,
        files=files,
        data=params
    )
    if not response.ok:
        raise Exception(f"HTTP {response.status_code}: {response.text}")

    return response


# Streamlit app layout
st.title("Image Generation with Stable Diffusion")
st.markdown("Upload an image and enter a prompt to generate a new image.")

# Image upload
uploaded_image = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

# User input for prompts
prompt = st.text_input("Prompt")
negative_prompt = st.text_input("Negative Prompt", "")
seed = st.number_input("Seed", value=0, min_value=0)
output_format = st.selectbox("Output Format", ["jpeg", "png"])
strength = st.slider("Strength", 0.0, 1.0, 0.75, 0.01)

# Generate button
if st.button("Generate Image"):
    if uploaded_image is not None:
        # Save the uploaded image temporarily
        image_path = "./temp_image.jpg"
        with open(image_path, "wb") as f:
            f.write(uploaded_image.getbuffer())
        
        host = f"https://api.stability.ai/v2beta/stable-image/generate/sd3"

        params = {
            "image": image_path,
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "strength": strength,
            "seed": seed,
            "output_format": output_format,
            "model": "sd3.5-large",
            "mode": "image-to-image"
        }

        response = send_generation_request(host, params)

        # Decode response
        output_image = response.content
        finish_reason = response.headers.get("finish-reason")
        seed = response.headers.get("seed")

        # Check for NSFW classification
        if finish_reason == 'CONTENT_FILTERED':
            st.warning("Generation failed NSFW classifier")
        else:
            # Save and display result
            generated = f"generated_{seed}.{output_format}"
            with open(generated, "wb") as f:
                f.write(output_image)
            st.success(f"Saved image {generated}")

            # Display generated image
            st.image(generated, caption="Generated Image")

    else:
        st.error("Please upload an image before generating.")

