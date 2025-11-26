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

RE_LIST = re.compile(r'\[.*\]', re.DOTALL)
RE_DICT = re.compile(r'{.*}', re.DOTALL)
RE_HTML = re.compile(r'<.*>', re.DOTALL)

def response_to_list(response):
  return json.loads(RE_LIST.search(response).group(0))

def response_to_dict(response):
  try:
    return json.loads(RE_DICT.search(response).group(0))
  except json.JSONDecodeError:
    print('Parse JSON Error:', response)

def json_to_markdown(json_data, indent=0):
    #print(json_data)
    markdown_string = ""
    indent_str = "  " * indent  # Two spaces for each indentation level

    if isinstance(json_data, dict):
        for key, value in json_data.items():
            markdown_string += f"{indent_str}- *{key}:*\n"
            markdown_string += json_to_markdown(value, indent + 1)
    elif isinstance(json_data, list):
        for i,item in enumerate(json_data):
            markdown_string += f"{indent_str}-  {i+1} : \n"
            markdown_string += json_to_markdown(item, indent + 1)
    elif isinstance(json_data, str):
        markdown_string += f"{indent_str}  {json_data}\n"  # Add two more spaces for string values
    elif isinstance(json_data, (int, float, bool, type(None))):  # Handle numbers, booleans and null
        markdown_string += f"{indent_str}  {str(json_data)}\n"  # Add two more spaces for scalar values
    else:
        markdown_string += f"{indent_str}  (Unsupported type)\n"

    return markdown_string

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

def call_gemini_for_editing(img, prompt):
    prompt_template = f"""
        You're an advertising professional utilizing Imagen for ad creation. 
        Generate an English Imagen prompt that will transform the provided image to meet the user's specifications.

        User Request: {prompt} 

        <instructions>

        <task1> Analyze the original photo and write a detailed description of it including photo or painting style (within 60 tokens). </task1>

        <task2> Identify and describe the most central object in the original photo (within 20 tokens). </task2>

        <task3> Determine the subject type:
        person: If the main object is a person.
        animal: If the main object is an animal.
        product: If the main object is a product.
        default: For all other cases.
        Store this information in the subject_type variable. You must use one of the values [person, animal, product, default] in the subject_type field. </task3>

        <task4> Write a imagen positive_prompt in English for generationg a banner image on the campaign landing page:
        * generate detailed description that describes the final desired image with main object and reference id and random camera angle in the positive prompt, if necessary, include the command to resize the reference subject with reference id in the positive prompt (within 120 tokens). 
        * list important forbidden keywords in the negative prompt(within 60 Tokens)
        (e.g., "A sophisticated, late 30s female driving a Mazda3 Hatchback[1] in a modern city setting.  The focus should be on the woman, either driving or working on her laptop inside the car[1]." )
        
        </task4>

        <task5> Guidance scale is a value that indicates the degree of influence a prompt has on an image. 
        When modifying the foreground, a value - 1.0 is generally used, while for background modifications, a value greater than 1.0 is used - generally 20. 
        Especially when the difference between the existing background and the desired background is significant during background modification, the guidance scale can be increased up to 20.0 to strengthen the influence of the prompt.</task5>

        <task6> The Mask Dilation value determines the degree to which the original image is reflected in the resulting image. 
        For minimal modifications to the original image, a value of 0.005 is recommended. For more significant alterations, a maximum value of 0.03 is appropriate. </task6>

        <task7> All outputs should be in English. </task7>

        <task8> Please DO NOT REPEAT same words in the negative prompt. </task8>

        </instructions>

        <output>
        {{
        "org_image_description" : ...,
        "main_object_description" : ...,
        "subject_type" : ...,
        "positive_prompt" : ...,
        "negative_prompt" : ...,
        "guidance_scale" : ...,
        "mask_dilation" : ...,
        }}
        </output>
        """

    response_schema = {
        "type" : "OBJECT",
        "properties" : {
            "org_image_description": {"type": "STRING"},
            "main_object_description": {"type": "STRING"},
            "subject_type": {"type": "STRING"},
            "positive_prompt": {"type": "STRING"},
            "negative_prompt": {"type": "STRING"},
            "guidance_scale": {"type": "STRING"},
            "mask_dilation": {"type": "STRING"},
            "control_type": {"type": "STRING"},
        }
    }
    model = GenerativeModel("gemini-1.5-flash-002")
    response = model.generate_content(
        [img, prompt_template],
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

def edit_image(img, edit_json, ratio="16:9") -> None:   
    edit_model = ImageGenerationModel.from_pretrained("imagen-3.0-capability-001")
    
    print(edit_json["positive_prompt"])

    subject_reference_image = SubjectReferenceImage(
            reference_id=1,
            image=img,
            subject_description=edit_json["main_object_description"],
            subject_type=edit_json["subject_type"],
        )

    edited_image = edit_model._generate_images(
            prompt=f'Generate an image about {edit_json["main_object_description"]} [1] to match this description: {edit_json["positive_prompt"]}',
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

async def generate_image_async(idx, prompt, ratio="16:9") -> None:   
    generate_model = ImageGenerationModel.from_pretrained("imagen-3.0-generate-002")
    
    print(prompt)

    loop = asyncio.get_event_loop()
    with concurrent.futures.ThreadPoolExecutor() as pool:
        response = await loop.run_in_executor(
            pool,
            lambda:generate_model.generate_images(
                prompt=prompt,
                number_of_images=1,
                language="en",
                aspect_ratio=ratio,
                safety_filter_level="block_some",
                person_generation="allow_adult",
                output_gcs_uri=f"{BUCKET}/HS"
            )
        )
    return(response)

def render_page(i):            
    avatar = st.session_state.avatars[i]

    print(avatar['edits']["suggest"][0])             

    ## generating 
    image_prompt = call_gemini_for_generating(product,avatar['edits']["suggest"][0])                    
    gen_image = generate_image(i, image_prompt)
    
    if gen_image == None:
        generated_image= f"https://storage.googleapis.com/lge_tv/HS/product_{i}.png"    
    else: 
       generated_image = gen_image._gcs_uri.replace("gs://", "https://storage.cloud.google.com/")               

    prompt = f"""Generate HTML markup from the provided JSON to construct a campaign landing page for the product: {product}.  Adhere to the following specifications:

                * **Image Tag Restriction:**  The `<img>` tag is strictly prohibited.
                * **Typography:** Employ a distinct font family for each section.
                * **Hero Section Background:** Utilize the provided image reference, `{generated_image}`, as the background image for the hero section.
                * **Color Accessibility:**  Ensure optimal readability by selecting appropriate font and background colors for each section.
                * **Text Alignment:** Implement center alignment for the hero and benefit sections.  Left alignment should be used for the social-proof and feature list sections.
                * **Section Padding:**  Apply left and right padding to each section.
	
                <json>{json.dumps(avatar["page"])}</json>"""
    #prompt_template = f"Format your response as a plain text question without quotes.\n\n{prompt}"
    response = call_gemini(prompt,ret_type="text")

    html = response.strip()

    if html.startswith("```html") and html.endswith("```"):
        html =  html[7:-3]  # Remove "```html" and "```"

    return html


def upload_image(i):
    storage_client = storage.Client()
    bucket = storage_client.bucket(BUCKET)

    blob = bucket.blob(f"HS/product_{i}.png")
    print(blob.path)
    blob.upload_from_filename(f"./product_{i}.png")        

st.set_page_config(
    page_title='AI (AD) Avatars',
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
)

methods = [
  {
    "title": "Floodlight Targeting",
    "description": "Tracks user behavior across web, app, and ads using Google Marketing Platform's conversion tracking pixel to create tag-based audiences."
  },
  {
    "title": "Activity-based Targeting",
    "description": "Creates audiences based on campaign interactions or excludes users based on impression counts."
  },
  {
    "title": "YouTube User List Targeting",
    "description": "Creates YouTube remarketing lists based on interactions with your videos, ads, or channel."
  },
  {
    "title": "Customer Match Targeting",
    "description": "Uploads customer CSV for targeting (minimum audience size of 1,000 users)."
  },
  {
    "title": "Google Analytics 360 Audience Targeting",
    "description": "Shares GA360 remarketing lists based on site/app behavior for targeting or building similar audiences."
  },
  {
    "title": "Demographics Targeting",
    "description": "Sets up ad targeting based on demographics like gender, age, parental status, and household income."
  },
  {
    "title": "Affinity Targeting",
    "description": "Targets users with a demonstrated interest in a specific topic."
  },
  {
    "title": "In-market Targeting",
    "description": "Targets users actively researching or comparing related products and services."
  },
  {
    "title": "Custom Audience Targeting",
    "description": "Reaches audiences based on keywords, URLs, and apps related to your product or service."
  },
  {
    "title": "Life Events Targeting",
    "description": "Reaches audiences during key life events like moving, graduating, getting married, or having a baby."
  },
  {
    "title": "Geography Targeting",
    "description": "Targets by region (states, cities, postcodes), or specific locations (business chains, POIs, street addresses, coordinates)."
  },
  {
    "title": "Day and Time Targeting",
    "description": "Specifies serving ads by days and times in user or advertiser timezones."
  },
  {
    "title": "Similar Audiences",
    "description": "Expands existing audiences by targeting users with similar behavior and interests."
  },
  {
    "title": "Third-party (DMP) Audiences",
    "description": "Syncs audiences from third-party Data Management Platforms (DMPs) for more granular targeting."
  },
  {
    "title": "Combined Audiences",
    "description": "Consolidates targeting from multiple sources for more precise ad targeting."
  }
]


st.sidebar.markdown("""
    ## 수행할 단계를 선택하세요.
    * [1] 단계는 제일 먼저 실행해야 합니다.     
    * 나머지 단계들은 순서에 상관없이 실행 가능합니다.         
""")
pd.set_option('display.max_colwidth', None)

if 'avatars' not in st.session_state:
    st.session_state.avatars = None

if 'image' not in st.session_state:
    st.session_state.image = None

if 'image_edit_1' not in st.session_state:
    st.session_state.image_edit_1 = None

if 'fit' not in st.session_state:
    st.session_state.fit = None

if 'tab_htmls' not in st.session_state:
    st.session_state.tab_htmls = None

#product = st.sidebar.text_input("Product :", value="mazda 3 hatchback")
product = st.sidebar.text_input("Product :", value="LG 트롬 오브제컬렉션 워시콤보")
#product = st.sidebar.text_input("Product :", value="LG 휘센 오브제컬렉션 뷰I 에어컨")


banner_image = st.sidebar.file_uploader("Choose a banner image file", type=["jpg", "jpeg", "png"])
if banner_image is not None:
    # To read file as bytes:
    st.session_state.image = Part.from_image(Image.from_bytes(banner_image.getvalue()))
    st.session_state.image_edit_1 = vision_image(banner_image.getvalue())
    st.sidebar.image(banner_image.getvalue())

if st.sidebar.button("[1] Get A List Of AI Recommended Avatars"):
    
    st.header("[1] Get A List Of AI Recommended Avatars", divider=True)
    if product == None:
        st.write("제품명을 입력하세요")
    else:
        prompt = f'Imagine you\'re an agency directory running an advertising campaign for the {product}, provide descriptive five persona names and explanations of why each is a fit.'
        prompt_template =f"Answer it in Korean. Format the response as JSON list with two keys: persona, description.\n\n {prompt}"

        response = call_gemini(prompt_template)

        st.session_state.avatars = response_to_list(response)
        st.session_state.avatars_str = response
        avatars_df = pd.read_json(StringIO(st.session_state.avatars_str))
        st.table(avatars_df)
        

if st.sidebar.button("[2] Evaluate The Creative"):
    st.header("[2] Evaluate The Creative Against Each Avatar", divider=True)
    if st.session_state.avatars == None:
        st.write("[1] 단계를 먼저 수행하세요")
    else:
        if st.session_state.image == None:
            st.write("제품 이미지를 업로드 해주세요")
        else:
            example = {
                        "keep": [], 
                        "change": [], 
                        "suggest": []
                        }
            for avatar in st.session_state.avatars:
                prompt = f"""Imagine you are a display marketing expert, evaluate the attached image against the persona {avatar["persona"]}, {avatar["description"]}. 
                            List things to keep, change, and suggest three ideal advertising images for {avatar["persona"]}
                            DO NOT modify {product} name.
                            suggest should include product "{product}":
                            <EXAMPLE>
                            {json.dumps(example)}
                            </EXAMPLE>
                            """
                prompt_template = f"Answer it in Korean with quotes. Format your response as JSON dictionary with the keys: keep, change, suggest\n\n{prompt}"
                response = call_gemini(prompt_template,img=st.session_state.image)
                
                st.markdown(f'### {avatar["persona"]}')
                avatar['edits'] = response_to_dict(response)       
                
                #st.write(response)
                st.json(response)
                #st.markdown(json_to_markdown(avatar['edits'] ))

                #for key, value in avatar['edits'].items():  # Iterate over the list of dictionaries
                #    st.markdown(f"#### {key}\n")
                #    for i, item in enumerate(value):
                #        st.markdown(f"* {item}")

if st.sidebar.button("[3] Rank The Avatars Based On Product Fit"):
    st.header("[3] Rank The Avatars Based On Product Fit", divider=True)
    if st.session_state.avatars == None:
        st.write("[1] 단계를 먼저 수행하세요")
    else:
        if st.session_state.image == None:
            st.write("제품 이미지를 업로드 해주세요")
        else:
            table = '\n'.join(f'<persona>{avatar["persona"]}: {avatar["description"]}</persona>' for avatar in st.session_state.avatars)
            prompt = f"""Of the following personas, which one is most and least likley to purchase after seeing the attached advetisement, and why:\n\n 
                        <personas>{table}</personas>"""
            prompt_template = f"Answer it with full persona name in Korean. Format your response as JSON dictionary with three keys: most, least, reason.\n\n{prompt}"

            response = call_gemini(prompt_template,img=st.session_state.image)
            st.session_state.fit = response_to_dict(response)
            st.json(response)
            #st.markdown(json_to_markdown(st.session_state.fit))

if st.sidebar.button("[4] Get Audience Suggestions"):
    st.header("[4] Get Audience Suggestions For Each Avatar", divider=True)
    table = '\n'.join(f'{method["title"]}: {method["description"]}' for method in methods)

    if st.session_state.avatars == None:
        st.write("[1] 단계를 먼저 수행하세요")
    else:
        for avatar in st.session_state.avatars:
            st.markdown(f"### {avatar['persona']}")
            prompt = f'Pretend you are a marketing expert, you are selling {product} to persona {avatar["persona"]}. Pick 5 audiences that will generate the most sales from the following list:\n\n{table}'
            prompt_template = f"Answer it in Korean. Format your response as a JSON list of dictionaries with keys: title, description.\n\n{prompt}"

            response = call_gemini(prompt_template)

            avatar['targeting'] = response_to_list(response)

            targeting_df = pd.read_json(StringIO(response))
            st.table(targeting_df)
            #for i, item in enumerate(avatar['targeting']):
            #    st.markdown(json_to_markdown(item))    

if st.sidebar.button("[5] Add Positive And Negative Keywords"):
    st.header("[5] Add Positive And Negative Keywords", divider=True)

    if st.session_state.avatars == None:
        st.write("[1] 단계를 먼저 수행하세요")
    else:

        for avatar in st.session_state.avatars:
            st.markdown(f"### {avatar['persona']}")
            #avatar['keywords'] = {'positive':[], 'negative':[]}

            prompt = f'I\'m running a search engine campaign to sell a {product}. My target audience is {avatar["persona"]}. Can you suggest 10 audience specific positive and negative keywords? Avoid the product name in the keywords.'
            prompt_template = f"Answer it in Korean. Format your response as a JSON list of dictionaries with the keys: positive, negative.\n\n{prompt}"

            response = call_gemini(prompt_template)

            avatar['keywords'] = response_to_list(response)

            keywords_df = pd.read_json(StringIO(response))
            st.table(keywords_df)

if st.sidebar.button("[6] Generate Questions"):
    st.header("Expected Questions by Each Avatar", divider=True)
    if st.session_state.avatars == None:
        st.write("[1] 단계를 먼저 수행하세요")
    else:
        if st.session_state.image == None:
            st.write("제품 이미지를 업로드 해주세요")
        else:
            for avatar in st.session_state.avatars:
                st.markdown(f"### {avatar['persona']}")
                prompt = f"""Pretend you are {avatar["persona"]}. What is the most likely question you will ask about the {product} Suggest 3 questions.
                             Answer them to each {avatar["persona"]} asking each qestion about {product} as a sales person. 
                        """
                prompt_template = f"Answer it in Korean. Format your response as a JSON list of dictionaries with the keys: question, response \n\n{prompt}"

                response = call_gemini(prompt_template,search=True)

                avatar['qna'] = response_to_list(response)
                qna_df = pd.read_json(StringIO(response))
                st.table(qna_df)
                              

if st.sidebar.button("[7] Generate Page Json"):
    st.header("Generate Page Json For Each Avatar", divider=True)
 
    if st.session_state.avatars == None:
        st.write("[1] 단계를 먼저 수행하세요")
    else:
        if st.session_state.image == None:
            st.write("제품 이미지를 업로드 해주세요")
        else:
            for avatar in st.session_state.avatars:
                st.markdown(f"### {avatar['persona']}")
                prompt = f"""Give me an example of a highly converting landing page for {avatar["persona"]} who want to buy a {product}.  
                             The landing page should include: Hero Section, Benefits, Social Proof, Features List, Address Objection With Response, and Call To Action for {product}. 
                             The objection to address is: {avatar["qna"][0]["question"]}. The response is: {avatar["qna"][0]["response"]}. Rephrase the obection to be more engaging to the persona."""
                prompt_template = f"Answer it in Korean.  Format your response as a JSON dictionary..\n\n{prompt}"

                response = call_gemini(prompt_template,search=True)

                avatar['page'] = response_to_dict(response)
                st.json(avatar['page'])



@st.fragment
def render_page_st(idx):      
    personas = [item["persona"] for item in st.session_state.avatars]
    cols = st.columns(len(personas))

    tab1 = st.tabs(["Landing Page"])
    
    if st.session_state.tab_htmls == None:
        st.session_state.tab_htmls = [""] * len(personas)

    st.session_state.idx = idx

    for i, col in enumerate(cols):
        with col:
            if st.button(personas[i]):
                st.session_state.tab_htmls[i] = render_page(i)
                st.session_state.idx  = i

    #with tab1:
    st.html(st.session_state.tab_htmls[st.session_state.idx]) 
    #st.write("")
       

if st.sidebar.button("[8] Generate A Landing Page"):
    st.header("Generate A Landing Page for Each Avatar)", divider=True)
 
    if st.session_state.avatars == None:
        st.write("[1] 단계를 먼저 수행하세요")
    else:
        if st.session_state.image_edit_1 == None:
            st.write("제품 이미지를 업로드 해주세요")
        else:
            render_page_st(0)
            #with tabs[1]:
            #    st.html(render_page(1))

#if st.sidebar.button("upload image"):
#    upload_image(0)
#    upload_image(1)

if st.sidebar.button("Generate Image"):
    st.header("Generate Image for Each Avatar)", divider=True)
 
    if st.session_state.avatars == None:
        st.write("[1] 단계를 먼저 수행하세요")
    else:
        if st.session_state.image_edit_1 == None:
            st.write("제품 이미지를 업로드 해주세요")
        else:
            tasks =[]
            for i, avatar in enumerate(st.session_state.avatars):
                #if i < 2 :
                    print(avatar['edits']["suggest"][0])
                
                    ## editing
                    # #prompt_json = call_gemini_for_editing(st.session_state.image,avatar['edits']["suggest"][0])
                    #generated_image = edit_image(st.session_state.image_edit_2, prompt_json)

                    ## generating 
                    st.markdown(f"### {avatar['persona']}")
                    image_prompt = call_gemini_for_generating(product,avatar['edits']["suggest"][0])                    
                    gen_image = generate_image(i, image_prompt)
                    st.image(gen_image._pil_image)