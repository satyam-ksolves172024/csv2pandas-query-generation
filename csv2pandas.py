
from langchain.prompts import PromptTemplate
from datetime import datetime
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain_groq import ChatGroq
import matplotlib.pyplot as plt
import json
import base64
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
load_dotenv()
import pandas as pd 
import os
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
load_dotenv()
from prompts_and_descriptions import query_generation_template,graph_generation_template,predicting_plots_template

from langchain.chat_models import AzureChatOpenAI


# when using Groq
# llm = ChatGroq(
#     api_key="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", 
#     # model_name="llama3-70b-8192",
#     model_name = "llama-3.2-90b-vision-preview",
#     # model_name = "llama-3.3-70b-versatile",
#     temperature=0.7
# )


llm  = AzureChatOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    model= os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT"), # You must replace this value with the deployment name for your model.
    api_version="2024-05-01-preview",
        temperature=0.7
)


#Return the JSON of Pandas Query
def generate_response(question, csv_json):
    # start_time = time.time()

    try:
        response_schemas = [
            ResponseSchema(name="Pandas Query", description="The Hive SQL query")
        ]

        parser = StructuredOutputParser.from_response_schemas(response_schemas)

        system = query_generation_template

        if isinstance(csv_json, list):
            csv_json = {"csv_info": csv_json}  # Convert list to a dictionary

        prompt = ChatPromptTemplate.from_messages([("system", system), ("human", "{input}")])

        query_chain = prompt | llm


        next_full_chain =  query_chain | parser
        
        query = next_full_chain.invoke({"input": question,"csv_info": csv_json,"top_k":5})
        # print(question)
        # print(query)
        exec(query['Pandas Query'], globals(), locals())

        return query


    except Exception as e:
        return f"An error occurred: {e}"


# For Predicting Plots (line, bar, pie, etc.)
def pred_plots(question, df):
    # start_time = time.time()
    columns = df.columns
    dtype = [str(df[col].dtype) for col in columns]
    length_df = df.shape
    
    prompt = PromptTemplate(
    template=predicting_plots_template,
    input_variables=["question", "column_name", "column_data_dtype", "length_df"]
)
    prompt_formatted_str = prompt.format(
        question=question, column_name=list(columns), column_data_dtype=dtype, length_df=length_df
    )
    prediction = llm.predict(prompt_formatted_str)
    # data_dict = json.loads(prediction)

    start_index = prediction.find('{')
    end_index = prediction.rfind('}') + 1

    # Extract the JSON substring
    json_str = prediction[start_index:end_index]

# Convert the JSON string to a Python dictionary
    data = json.loads(json_str) 
    # execution_time = time.time() - start_time
    # logging.info(f"Pred Plot Generation time {execution_time:.2f} seconds")


    return data


#Function to generate graphs and saves in using its timestamp as file name
def graphs(pred,df):
    # start_time = time.time()
    plot_name = pred['Plot Name']
    variables = pred['Variables']

    # if not plot_name: return None
    
    prompt = PromptTemplate(
        template=graph_generation_template, input_variables=["plot_name", "variables"])

    
    prompt_formatted_str = prompt.format(plot_name=plot_name, variables=variables)
    prediction1 = llm.predict(prompt_formatted_str)

    cleaned_prediction = prediction1.strip("```python").strip("```")
    plt.clf()

    exec(cleaned_prediction, globals(), locals())
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")  # Full timestamp
    # time.sleep(10)

    path = f"output_plot_csv2pandas_{timestamp}.png"

    plt.draw()   # Ensure figure is drawn
    plt.pause(0.1)  # Pause briefly before saving
    plt.savefig(path, bbox_inches='tight')

    with open(path, 'rb') as imgfile:
        base64_bytes = base64.b64encode(imgfile.read())
        base64_encoded = base64_bytes.decode()


    return cleaned_prediction,path


