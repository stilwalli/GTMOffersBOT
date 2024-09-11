import vertexai
import re
from google.cloud import bigquery
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from google.cloud import storage
from io import BytesIO
from google.api_core.client_options import ClientOptions
from google.cloud import discoveryengine

import config

from vertexai.generative_models import (
    GenerationConfig,
    GenerativeModel,
    HarmBlockThreshold,
    HarmCategory,
    Part,
)

def generateQuery(project_id: str, region: str, input_string: str) -> str:
    try:
        vertexai.init(project=project_id, location=region)
        MODEL_ID = "gemini-1.5-flash-001" 
        example_model = GenerativeModel(
            MODEL_ID,
            system_instruction=[
                "Your mission is generate valid GCP select BQ queries.",
            ],
        )

        generation_config = GenerationConfig(
            temperature=0.9,
            top_p=1.0,
            top_k=32,
            candidate_count=1,
            max_output_tokens=8192,
        )

        # Set safety settings
        safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
        }

        prompt = """
            **Table Name:** scratchzone.programs.program

            **Columns:**

            * **offer_Name**: Unique offer name
            * **program_description**: Gives description of the offers
            * **qualification_criteria**: Gives the qualification critieria
            * **calltoaction**: Consists of URL which will give more information about the offer

        Query Rules
             1. Use select query include all the columns in schema based on the insert statement given. 
             2. Use where clause if needed
             3. Do not add delimiters to response

            """
        # Combine the schema information with the user's query request
        #prompt = "Given the table schema with the following table name columns:\n\nscratchzone.programs.program: offer_Name, program_description, qualification_criteria, calltoaction\n\n. The calltoaction gives more information on the corresponding offername"
        prompt += input_string
        # Set contents to send to the model
        contents = [prompt]
        # Prompt the model to generate content
        response = example_model.generate_content(
            contents,
            generation_config=generation_config,
            safety_settings=safety_settings,
        )
        print("BQ Table Updated for: ", response.text)
        # Return the generated query (or an error message if something went wrong)
        if response.text:
            return response.text
        else:
            return "No query generated. Please check your input and try again."

    except Exception as e:
        return f"Error generating query: {e}"
    


def getBQResponse(project_id: str, region: str, query: str) -> str:
    # Construct a BigQuery client object.
    print ("Query: ", query)
    client = bigquery.Client()
    query_job = client.query(query)
    results = query_job.result()
    df = results.to_dataframe()
    print("BQ Response", df)
    return df

def getOffers(project_id: str, region: str, query: str):
    client = bigquery.Client()
    query_job = client.query(query)
    results = query_job.result()
    df = results.to_dataframe()
    print("Query: ", query, ", Offer Query Response\n", df)
    return df


def generate_pdf(df):
    storage_client = storage.Client()
    bucket = storage_client.bucket(config.BUCKET_NAME)
    df = df.fillna('None')
    pattern = r"[^a-zA-Z0-9\s]" 
    uris = ""
    uriList = []
    for index, row in df.iterrows():
        cleaned_text = re.sub(pattern, '', row['offer_Name'])
        fileName = cleaned_text + ".pdf"

        buffer = BytesIO()
        #doc = SimpleDocTemplate(fileName, pagesize=letter)
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()

        # Section 1
        story.append(Paragraph(row['offer_Name'], styles['Heading1']))
        story.append(Paragraph(row['program_description'], styles['Normal']))

        story.append(Spacer(1, 12))  # Add some space after para#1

        # Section 2
        story.append(Paragraph("Eligibility Criteria", styles['Heading1']))
        story.append(Paragraph(row['qualification_criteria'], styles['Normal']))

        story.append(Spacer(1, 12))  # Add some space after para#2

        # Section 3

        story.append(Paragraph("More Details", styles['Heading1']))
        story.append(Paragraph(row['calltoaction'], styles['Normal']))

        story.append(Spacer(1, 12))  # Add some space after para#3
  
        # Section 4
        story.append(Paragraph("Program Status", styles['Heading1']))
        story.append(Paragraph(row['offer_status'], styles['Normal']))

        doc.build(story)
        blob = bucket.blob(fileName)
        blob.upload_from_string(buffer.getvalue(), content_type='application/pdf')
        uriList.append("gs://" + config.BUCKET_NAME + "/" + fileName)
        #print(f"PDF '{fileName}' uploaded to Google Cloud Storage bucket '{config.BUCKET_NAME}'")
        #uris = uris + "gs://" + config.BUCKET_NAME + "/" + fileName + ", "

    return uriList


def ingestFiles(gcsUris, flag):
    client_options = (
        ClientOptions(api_endpoint=f"{config.LOCATION}-discoveryengine.googleapis.com")
        if config.LOCATION != "global"
        else None
    )

    if (flag == 0):
        mode = discoveryengine.ImportDocumentsRequest.ReconciliationMode.INCREMENTAL
    else:
        mode = discoveryengine.ImportDocumentsRequest.ReconciliationMode.INCREMENTAL


    # Create a client
    client = discoveryengine.DocumentServiceClient(client_options=client_options)

# The full resource name of the search engine branch.
# e.g. projects/{project}/locations/{location}/dataStores/{data_store_id}/branches/{branch}
    parent = client.branch_path(
        project=config.PROJECT_ID,
        location=config.LOCATION,
        data_store=config.DATA_STORE_ID,
        branch="default_branch",
    )

    request = discoveryengine.ImportDocumentsRequest(
        parent=parent,
        gcs_source=discoveryengine.GcsSource(
            # Multiple URIs are supported
            input_uris=gcsUris,
            # Options:
            # - `content` - Unstructured documents (PDF, HTML, DOC, TXT, PPTX)
            # - `custom` - Unstructured documents with JSONL metadata
            # - `csv` - Unstructured documents with CSV metadata
            data_schema="content",
        ),
        # Options: `FULL`, `INCREMENTAL`
        reconciliation_mode=mode,
    )

    # Make the request
    operation = client.import_documents(request=request)

    print(f"Waiting for operation to complete: {operation.operation.name}")
    response = operation.result()

    # After the operation is complete,
    # get information from operation metadata
    metadata = discoveryengine.ImportDocumentsMetadata(operation.metadata)

    # Handle the response
    print("Response: ", response)
    print("Metadata: ", metadata)


