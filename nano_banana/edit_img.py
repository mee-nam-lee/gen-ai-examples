from google import genai
from google.genai.types import GenerateContentConfig, Modality
from PIL import Image
from io import BytesIO

client = genai.Client(vertexai=True)

# Using an image of Eiffel tower, with fireworks in the background.
image = Image.open("banner4.png")

response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents=[image, "Edit this image to make it look like a cartoon."],
    config=GenerateContentConfig(response_modalities=[Modality.TEXT, Modality.IMAGE]),
)
for part in response.candidates[0].content.parts:
    if part.text:
        print(part.text)
    elif part.inline_data:
        image = Image.open(BytesIO((part.inline_data.data)))
        image.save("edit_banner4.png")