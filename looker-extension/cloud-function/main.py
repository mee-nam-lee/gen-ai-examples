import functions_framework
import vertexai
import os
from urllib.parse import urlparse, parse_qs
import json
import re
import looker_sdk
import os
from google.cloud import bigquery
import pandas as pd
from langchain.llms import VertexAI
from looker_sdk.sdk.api40 import models as ml
from typing import cast, Dict, List, Union
import ast

def looker_init():
    #os.environ['LOOKERSDK_BASE_URL'] = ''
    #os.environ['LOOKERSDK_CLIENT_ID'] = ''
    #os.environ['LOOKERSDK_CLIENT_SECRET'] = ''
    #os.environ['LOOKERSDK_VERIFY_SSL'] = 'True'

    sdk = looker_sdk.init40()
    return sdk

def get_right_explore(question):
    print(f"BQ call")
    client = bigquery.Client()
    dataset = os.environ.get("DATASET")
    query_string=f'''
        SELECT query.query AS query, base.model_name AS model_name, base.explore_name AS explore_name
        FROM VECTOR_SEARCH(
        TABLE `{dataset}.embeddings`, 'ml_generate_embedding_result',
        (
            SELECT ml_generate_embedding_result, content AS query
            FROM ML.GENERATE_EMBEDDING(
            MODEL `{dataset}.embedding_model`,(
                SELECT '{question}' AS content
            )
            )
        ), top_k => 1)
        '''
    print(f"BQ :  {query_string}")
    query_job = client.query(query_string)
    result = query_job.result()
    #print(result)
    df = result.to_dataframe()
    #print(df)
    return df.loc[0, 'model_name'], df.loc[0, 'explore_name']

def get_field_values(sdk, model_name, explore_name):

  print(f"get Looker fields")
  explore = sdk.lookml_model_explore(
    lookml_model_name=model_name,
    explore_name=explore_name,
    fields="id, name, description, fields",
  )

  my_fields = []

  # Iterate through the field definitions and pull in the description, sql,
  # and other looker tags you might want to include in  your data dictionary.
  if explore.fields and explore.fields.dimensions:
    for dimension in explore.fields.dimensions:
      if dimension.hidden:
        print(dimension)
        continue
      dim_def = {
        "field_type": "Dimension",
        "view_name": dimension.view_label,
        "field_name": dimension.name,
        "type": dimension.type,
        "description": dimension.description,
        #"sql": dimension.sql,
      }
      my_fields.append(dim_def)
  if explore.fields and explore.fields.measures:
    for measure in explore.fields.measures:
      mes_def = {
        "field_type": "Measure",
        "view_name": measure.view_label,
        "field_name": measure.name,
        "type": measure.type,
        "description": measure.description,
        #"sql": measure.sql,
      }
      my_fields.append(mes_def)
  if explore.fields and explore.fields.parameters:
    for parameter in explore.fields.parameters:
      par_def = {
        "field_type": "Parameter",
        "view_name": parameter.view_label,
        "field_name": parameter.name,
        "default_filter_value": parameter.default_filter_value,
        "type": parameter.type,
        "description": parameter.description,
        #"sql": parameter.sql,
      }
      my_fields.append(par_def)
  return my_fields

def choose_right_fields(llm, fields, question):
    sample_json = """
                {
                "dimensions": [
                    "dimension1",
                ],
                "measures": [
                    "measure1",
                ],
                "filters": [
                    {
                    "field_name": "field_name1",
                    "values": [
                        "value1"
                    ]
                    }
                ],
                "sorts": [
                    {
                    "field_name": "field_name1",
                    "direction": "asc"
                    }
                ],
                "parameters": [
                    "param1",
                ],
                "pivots": [
                    "field1"
                ],
                "hidden_fields": [
                    "field1"
                ]
                }
                """

    prompt_template = """As a looker developer, choose right dimesions and measures for the question below. 
        You should choose right fields as least as possible, find possible filter fields as many as possible and sort fields must be choosen in the dimension fields.

        fields : {fields}

        question: {question}

        answer format: json
        {sample_json}
        """

    response = llm.predict(prompt_template.format(fields=fields, question=question, sample_json=sample_json))
    return response

def parse_json_response(llm_json_response) -> any:
    #print('llm response:'+ response)
    start_char = '['
    end_char = ']'
    if llm_json_response.find('[') == -1 or llm_json_response.find('{') < llm_json_response.find('[') :
        start_char = '{'
        end_char = '}'
    start_index = llm_json_response.find(start_char)
    end_index = llm_json_response.rfind(end_char)
    json_data = llm_json_response[start_index:end_index+1]
    parsed_json = json.loads(json_data)
    return parsed_json

def get_field_type(field_name, schema_fields):
  for field in schema_fields:
    if field['field_name'] == field_name:
      return field['type']

def decide_to_retrieve_values_for_the_filters(llm, related_fields):
    output_sample = """
    {
        "required_target": ["field1","field2"]
    }
    """
    prompt_template = """As a looker developer, decide whether to retrieve values for the filters below. 
    For example, date / timestamp columns don't need to retrieve values. but string columns need to retrieve values from the database.

    filter fields : {filter_fields}

    output sample : json array
    {output_sample}
    """
    response = llm.predict(prompt_template.format(filter_fields=related_fields['filters'], output_sample=output_sample))
    return response

def get_validated_filter_values_from_looker(sdk, lookml_model, lookml_explore, retrieve_target_filter_obj):
    choose_right_filter_value_list = []
    for retrieve_target_filter in retrieve_target_filter_obj['required_target']:
        print(retrieve_target_filter)
        query_template = ml.WriteQuery(model=lookml_model, view=lookml_explore,fields=[retrieve_target_filter])
        query = sdk.create_query(query_template)
        json_ = sdk.run_query(query.id, "json")
        print(json_)
        choose_right_filter_value_list.append({ retrieve_target_filter : json_})
    return choose_right_filter_value_list

def choose_right_filter_value(llm, filter_values, wanted_value):
    example_json = "[ 'value1' , 'value2' , 'value3' ]"
    prompt_template = """As a looker developer, choose right filter value for the wanted value below without changing filter value itself.

    output format : json array
    {example_json}

    filter_values : {filter_values}

    wanted_values: {wanted_value}

    """
    response = llm.predict(prompt_template.format(example_json=example_json,filter_values=filter_values, wanted_value=wanted_value))
    return response  

def parse_python_object(llm_python_object) -> any:
    print('llm response:'+ llm_python_object)
    if llm_python_object.find('{') == -1:
        start_char = '['
        end_char = ']'
    elif llm_python_object.find('[') == -1 or llm_python_object.find('{') < llm_python_object.find('[') :
        start_char = '{'
        end_char = '}'
    start_index = llm_python_object.find(start_char)
    end_index = llm_python_object.rfind(end_char)
    object_data = llm_python_object[start_index:end_index+1]
    print(object_data)
    parsed_object = ast.literal_eval(object_data)
    return parsed_object

def get_user_input_value_for_filter_field(related_fields, field_name):
    for filter in related_fields['filters']:
        if filter['field_name'] == field_name:
            return filter['values']
    return ""

def get_appropriate_filter_value_pair(llm,related_fields, retrieve_filter_and_values):
    filter_value_pair = []
    for filter_and_values in retrieve_filter_and_values:
        field_name = list(filter_and_values.keys())[0]
        print(filter_and_values)
        user_input_value = get_user_input_value_for_filter_field(related_fields, field_name)
        print(user_input_value)
        actual_value = choose_right_filter_value(llm,filter_and_values, user_input_value)
        print(actual_value)  
        value_object = parse_python_object(actual_value)
        print(value_object)
        filter_value_pair.append({ field_name : value_object})
    return filter_value_pair

def get_quoted_value(valid_filter_values, field_name, schema_fields):
    values = []
    for filter_values in valid_filter_values:
        field_name_cmp = list(filter_values.keys())[0]
        if field_name_cmp == field_name:
            for field_value in list(filter_values.values())[0]:
                field_type = get_field_type(field_name, schema_fields)
                if field_type == 'string':
                    values.append(field_value)
                else:
                    values.append(str(field_value))
    return values

# LookML Filter values MUST be a string. 
def get_lookml_filter_values(valid_filter_values, filters,schema_fields):
    filter_dict:Dict[str, Any] = {}
    for filter in filters:
        field_name = filter['field_name']
        quoted_values = get_quoted_value(valid_filter_values, field_name, schema_fields)
        if(quoted_values == []):
            print(filter['values'])
            filter_dict[field_name] = ",".join(filter['values'])
            continue
        filter['values'] = quoted_values
        filter_dict[field_name] = ",".join(quoted_values)
    return filter_dict

def make_dimension_and_description_pair(related_fields, schema_fields):
    dimension_and_description_pair = []
    for one_dimension in related_fields['dimensions']:
        for dimension in schema_fields:
            if dimension['field_name'] == one_dimension:
                dimension_and_description_pair.append((one_dimension, dimension['description']))
    return dimension_and_description_pair

def choose_chart_type_and_pivots(llm, related_fields, schema_fields, question):
    dimension_and_description_pair = make_dimension_and_description_pair(related_fields, schema_fields)
    sample_json = """{
    "chart_type": "looker_column",
    "date_time_dimensions": ["dimension1"],
    "pivots": [
        "field1"
    ],
    "hidden_fields": [
        "field1"
    ]
    "reason_to_choose": "I choose field1 as a pivot field because ..."
    }"""
    prompt_template = """As a looker developer, choose chart type and pivot fields and hidden fields in the given dimensions for the question below. 
    Pivot field is a field that is used to create a pivot table. A pivot field converts category values in the field to columns so that you can compare different category values. 
    For example, if you have sales data, you can compare sales by product by setting the "Product" field as a pivot field. Date/time fields MUST not be used as pivot fields.
    Hidden field is a field that is not displayed in a chart. Hidden fields are used to hide fields that are not needed in the chart or that can confuse users. 
    For example, the "Product ID" field can be used to identify products, but it does not need to be displayed in a chart. If there are two same date fields, one of them can be hidden. 
    At least one field must be a visible field that is not used in pivot fields or hidden fields.

    chart_types : 
    looker_column - Column charts are useful when you want to compare the values of multiple fields for multiple records. It needs one main field to show the values separated by the main field. And this field must not be a pivot field.
    looker_line - Line charts are useful when you want to show the changes in a value over time. They are also useful for comparing the changes in two or more values over time.
    looker_area - Area charts are useful when you want to compare the trends of two or more values over time. They are also useful for showing the cumulative sum of values over time.
    looker_funnel - Funnel charts are useful to understand events in a sequential process, like prospect stages in a sales pipeline, engagement with a marketing campaign, or visitor movement through a website.
    looker_pie - Pie charts are useful when you want to show the proportion of values to the total value. They are also useful for comparing the proportional differences between values.
    looker_timeline - Timeline charts are useful when you want to show events over time. They are also useful for showing the duration of events. It needs at least 3 fields. 1. Event Name 2. Start Date 3. End Date
    looker_table - Table charts are useful when you want to show the values of multiple fields for multiple records. They are also useful for showing the values of multiple fields for a single record.

    dimensions : 
    {dimensions}

    question:
    {question}

    answer format: json
    {sample_json}
    """
    prompt_full = prompt_template.format(dimensions=dimension_and_description_pair, question=question, sample_json=sample_json)
    #print(prompt_full)
    response = llm.predict(prompt_full)
    return response

def validate_hidden_fields(chart_type_and_pivots, related_fields):
    hidden_fields = chart_type_and_pivots['hidden_fields']
    pivot_fields = chart_type_and_pivots['pivots']
    dimensions = related_fields['dimensions']
    if len(dimensions) == len(hidden_fields) + len(pivot_fields):
        return False
    return True

def refine_hidden_fields(llm, chart_type_and_pivots, question):
    hidden_fields = chart_type_and_pivots['hidden_fields']
    pivot_fields = chart_type_and_pivots['pivots']
    dimensions = hidden_fields
    
    sample_json = """{
    "dimension": "field1"
    }"""

    prompt_template = """As a looker developer, choose an appropriate field shown in the x-axis with the given dimensions and question.

    output json format:
    {sample_json}

    given dimensions :
    {dimensions}

    given question:
    {question}

    """
    prompt_full = prompt_template.format(sample_json=sample_json, dimensions=dimensions, question=question)
    response = llm.predict(prompt_full)
    return response

def make_query_for_the_look(sdk,lookml_model, lookml_explore, related_fields, valid_filter_values, chart_type_and_pivots, schema_fields):
    fields = []
    fields.extend(related_fields['dimensions'])
    fields.extend(related_fields['measures'])
    filters = get_lookml_filter_values(valid_filter_values, related_fields['filters'], schema_fields )
    hidden_fields = chart_type_and_pivots['hidden_fields']
    pivot_fields = chart_type_and_pivots['pivots']
    chart_type = chart_type_and_pivots['chart_type']
    print('fields:' + str(fields))
    print('filters:' + str(filters))
    print('hidden_fields:' + str(hidden_fields))
    print('pivot_fields:' + str(pivot_fields))
    print('chart_type:' + str(chart_type))
    query_template = ml.WriteQuery(model=lookml_model, view=lookml_explore,fields=fields,filters=filters,pivots=pivot_fields,vis_config={'type':chart_type, 'hidden_fields':hidden_fields})
    query = sdk.create_query(query_template)
    print(query)
    print('query.id:' + str(query.id))
    print('query.client_id:' + str(query.client_id))
    #run_response = sdk.run_inline_query("json", query)
    #print('query.id:' + str(query.id))
    #print('query.client_id:' + str(query.client_id))
    return query

@functions_framework.http
def gen_looker_query(request):

    print("Request :", request)

    if request.method == "OPTIONS":
        headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Max-Age": "3600"
        }

        return ("", 204, headers)


    request_json = request.get_json(silent=True)

    project = os.environ.get("PROJECT")
    location = os.environ.get("REGION")


    if request_json and 'question' in request_json:
        question = request_json['question']
        print(question)
        sdk = looker_init()

        vertexai.init(project=project, location=location)

        llm = VertexAI(
            #model_name="text-bison@latest",
            #model_name="text-unicorn@001",
            model_name="text-bison-32k",
            max_output_tokens=1020,
            temperature=0,
            top_p=0.8,
            top_k=40,
        )

        model_name, explore_name = get_right_explore(question)  
        print(f"model_name :{model_name} {explore_name}")
        schema_fields = get_field_values(sdk,model_name, explore_name)
        right_fields = choose_right_fields(llm=llm, fields=schema_fields, question=question)
        right_fields_object = parse_json_response(right_fields)
        print(right_fields_object)
        retrieve_target_filters = decide_to_retrieve_values_for_the_filters(llm,right_fields_object)
        retrieve_target_filter_obj = parse_json_response(retrieve_target_filters)
        retrieve_filter_and_values = get_validated_filter_values_from_looker(sdk, model_name, explore_name, retrieve_target_filter_obj)
        valid_filter_values = get_appropriate_filter_value_pair(llm,right_fields_object, retrieve_filter_and_values)
        llm_response = choose_chart_type_and_pivots(llm, right_fields_object, schema_fields, question)
        chart_type_and_pivots = parse_json_response(llm_response)
        if not validate_hidden_fields(chart_type_and_pivots, right_fields_object): 
            field_shown = parse_json_response(refine_hidden_fields(chart_type_and_pivots, question))
            chart_type_and_pivots['hidden_fields'].remove(field_shown['dimension'])

        #lookml_filter = get_lookml_filter_values(valid_filter_values, right_fields_object['filters'], schema_fields)
        generated_query = make_query_for_the_look(sdk, model_name, explore_name, right_fields_object, valid_filter_values, chart_type_and_pivots,schema_fields )

        response = {
            "model_name" : f"{model_name}",
            "explore_name" : f"{explore_name}",
            "qid" : f"{generated_query.client_id}",
        }

        # Complete a structured log entry.
        entry = dict(
            severity="INFO",
            message={"request": request_json['question'],"response": json.dumps(response)},
            component="explore-assistant-metadata",
        )

        print(json.dumps(entry))       

        # Set CORS headers for extension request
        headers = {
            "Access-Control-Allow-Origin": "*"
        }

        print("Response: ",json.dumps(response), "Headers: ", headers)

        return (response,200,headers)
    else:
        return ('Bad Request',400)