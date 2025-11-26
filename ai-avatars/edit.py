import streamlit as st
import os
from dotenv import load_dotenv
from google import genai
import vertexai
#from google.genai.types import HttpOptions, Part, GenerateContentConfig
from vertexai.generative_models import GenerativeModel,Part,GenerationConfig, Image, Tool, grounding 
#from vertexai.preview.vision_models import ImageGenerationModel, Image
from vertexai.preview.vision_models import (
    Image as vision_image,
    ImageGenerationModel,
    RawReferenceImage,
    SubjectReferenceImage,
)
import PIL.Image
import re
import json
from IPython.display import HTML, Markdown
import asyncio
import concurrent.futures
import pandas as pd
from io import StringIO
from google.cloud import storage
from io import BytesIO
import time

load_dotenv()
PROJECT_ID = os.environ.get("PROJECT_ID")
LOCATION = os.environ.get("LOCATION")
BUCKET = os.environ.get("BUCKET")

vertexai.init(project=PROJECT_ID, location=LOCATION)


MODEL = "gemini-1.5-flash-002"
#MODEL = "gemini-2.0-flash-001"

def call_gemini(prompt_template, img=None, ret_type=None, search=False):

    tools = [
            Tool.from_google_search_retrieval(
                google_search_retrieval=grounding.GoogleSearchRetrieval()
            ),
        ]
    
    if search:
        model = GenerativeModel(MODEL,tools=tools)
    else:
        model = GenerativeModel(MODEL)

    if ret_type == None:
        generate_content_config = GenerationConfig(
            temperature = 0.6,
            top_p = 0.93,
            top_k=32,
            max_output_tokens = 4192,
            response_mime_type="application/json" #, response_schema=response_schema
        )
    elif ret_type == 'text':
        generate_content_config = GenerationConfig(
            temperature = 0.6,
            top_p = 0.93,
            top_k=32,
            max_output_tokens = 4192,
        )

    if img == None:
        response = model.generate_content(
            [prompt_template],
            generation_config=generate_content_config,
            stream=False
        ) 
    else :   
        response = model.generate_content(
            [prompt_template,img],
            generation_config=generate_content_config,
            stream=False
        ) 
    print(response.text)
    
    return response.text

def call_gemini_for_editing(product, prompt):
    prompt_template = f"""
        You are an advertising professional utilizing Imagen for ad creation.
        Generate an Imagen prompt in English that features the specified product and fulfills the user's request.  
        Use a professional tone and style suitable for advertising.  Craft a detailed and descriptive prompt that leverages industry-specific terminology and evokes a strong sense of the desired ad aesthetic. 
        Aim for a comprehensive prompt that provides ample direction for image generation.


        User Request: {prompt} 

        <instructions>
        - Include {product}[1] in the positive prompt.  Be specific about the product's placement, interaction with other elements, and desired appearance.
        - Adhere completely to the user's request. The size of  {product}[1] may be adjusted within the final image positive prompt.
        - Specify camera focus, mood, tone, and color style. Use evocative language to describe the desired atmosphere and visual impact.
        - Specify lighting, composition, and other relevant artistic details. Consider using advanced image generation techniques like depth of field, specific lenses (e.g., wide-angle, telephoto), and camera angles.
        - Enumerate important forbidden keywords in the negative prompt (within 60 tokens). Avoid redundant keywords in the negative prompt.  Provide specific and targeted exclusions to ensure the generated image aligns precisely with the desired outcome.
        - All outputs must be in English.

        Example:
        (e.g., "A sophisticated woman in her late 30s driving a sleek, silver car[1] in a vibrant, modern city setting at sunset. The focus should be on the woman's confident expression as she navigates the bustling streets, with the car[1] seamlessly integrated into the scene")
        </instructions>

        <output>
        {{
        "positive_prompt" : ...,
        "negative_prompt" : ...,
        }}
        </output>
        """

    response_schema = {
        "type" : "OBJECT",
        "properties" : {
            "positive_prompt": {"type": "STRING"},
            "negative_prompt": {"type": "STRING"},
        }
    }
    model = GenerativeModel("gemini-1.5-flash-002")
    response = model.generate_content(
        [prompt_template],
        generation_config=GenerationConfig(
            max_output_tokens=4192,
            temperature=0.6,
            top_p=0.93,
            top_k=32,
            response_mime_type="application/json", response_schema=response_schema
        )
    )    
    json_response = json.loads(response.text)
    print(json_response)

    return json_response

def call_gemini_for_generating(product, prompt):
    prompt_template = f"""
        You're an advertising professional utilizing Imagen for ad campaign banner creation. 
        Generate an English Imagen prompt following these guildlines.

        - Please reconstruct the original user request in detail
        - Must include {product} in a final prompt
        - Specifically describe the overall atmosphere and emotion of the scene.
        - Describe the appearance, texture, and condition of the elements in detail.
        - Add descriptions that express a sense of space and perspective.
        - Include environmental elements such as lighting, shadows, and time of day.
        - Appropriately utilize sensory and metaphorical expressions.

        User Request: {prompt} 
        """

    model = GenerativeModel("gemini-1.5-flash-002")
    response = model.generate_content(
        [prompt_template],
        generation_config=GenerationConfig(
            max_output_tokens=2048,
            temperature=0.8,
            top_p=0.93,
            top_k=32,
        )
    )    
    return response.text

def edit_image(product, img, edit_json, ratio="16:9") -> None:   
    edit_model = ImageGenerationModel.from_pretrained("imagen-3.0-capability-001")
    
    print(edit_json["positive_prompt"])

    subject_reference_image = SubjectReferenceImage(
            reference_id=1,
            image=img,
            subject_description=product,
            subject_type="product",
        )

    edited_image = edit_model._generate_images(
            prompt=f"Generate an image of the {product}[1] to match this description: {edit_json['positive_prompt']}",
            negative_prompt=edit_json["negative_prompt"],
            number_of_images=1,
            aspect_ratio=ratio,
            reference_images=[subject_reference_image],
            #guidance_scale=float(edit_json["guidance_scale"]),
            safety_filter_level="block_some",
            person_generation="allow_adult",
        )       
    
    return edited_image[0]

def generate_image(idx, prompt, ratio="16:9") -> None:   
    generate_model = ImageGenerationModel.from_pretrained("imagen-3.0-generate-002")
    
    print(prompt)

    generated_images = generate_model.generate_images(
        prompt=prompt,
        number_of_images=1,
        language="en",
        aspect_ratio=ratio,
        safety_filter_level="block_some",
        person_generation="allow_adult",
        output_gcs_uri=f"gs://{BUCKET}/HS"
    )
    if len(generated_images.images) == 0:
        print("image hasn't generated")
        return None
    else:
        print(generated_images.images[0]._gcs_uri)
        return generated_images.images[0]
    
    #generated_images[0].save(f"product_{idx}.png")
    #upload_image(idx)
    #generated_images[0].save(location=f"product_{idx}.png", include_generation_parameters=False)
    #return generated_images[0]


st.set_page_config(
    page_title='AI (AD) Avatars',
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
)

if 'image' not in st.session_state:
    st.session_state.image = None

if 'image_edit' not in st.session_state:
    st.session_state.image_edit = None


#product = st.sidebar.text_input("Product :", value="mazda 3 hatchback")
product = st.sidebar.text_input("Product :", value="LG 트롬 오브제컬렉션 워시콤보")

product_image = st.sidebar.file_uploader("Choose a image file", type=["jpg", "jpeg", "png"])
if product_image is not None:
    # To read file as bytes:
    st.session_state.image = Part.from_image(Image.from_bytes(product_image.getvalue()))
    st.session_state.image_edit = vision_image(product_image.getvalue())
    st.sidebar.image(product_image.getvalue())

user_prompt = st.sidebar.text_input("User Prompt", "원룸 하우스에 세탁기가 놓여있는 모습")

if st.sidebar.button("Generate Image"):
    
    st.header("Generated Image", divider=True)
    if product == None:
        st.write("제품명을 입력하세요")
    else:
        edit_prompt = call_gemini_for_editing(product,user_prompt)
        edited_image = edit_image(product, st.session_state.image_edit, edit_prompt)


        st.image(edited_image._pil_image)
