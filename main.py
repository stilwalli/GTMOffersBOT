from fastapi import FastAPI, Request
import json
import base64
import logging
import google.cloud.logging
import config
import model

app = FastAPI()

# Configure the client library
#client = google.cloud.logging.Client()
#client.setup_logging()

# Create a logger
#logger = logging.getLogger()
#logger.setLevel(logging.INFO)  # Adjust log level as needed

def decode_base64(data):
  #logger.info("decode_base64")
  try:
    return base64.b64decode(data)
  except (TypeError, ValueError) as e:
    # Handle invalid base64 data gracefully
    print(f"Error decoding base64: {e}")
    return None

@app.post('/initializeIndex')
async def initializeIndex():
    try:
        print("initializeIndex")
        df = model.getBQResponse(config.PROJECT_ID, config.REGION, config.QUERY_ALL)
        uriList = model.generate_pdf(df)
        model.ingestFiles(uriList, 0)

        # Return the response with a 200 status code
        return {"message": "Index initialization in progress"}, 200

    except Exception as e:
        # Handle any exceptions that might occur during the process
        print(f"Error during index initialization: {e}")
        # Return an error response with a 500 status code
        return {"message": "Internal Server Error"}, 500


@app.post('/updateIndex')
async def updateIndex(request: Request):
    try:
        print("updateIndex")
        message = await request.json()
        json_data = json.dumps(message)
        data = json.loads(json_data)
        extracted_data = data['message']['data']
        decodedMessage = decode_base64(extracted_data)
        logMessage = json.loads(decodedMessage)
        query = logMessage['protoPayload']['serviceData']['jobCompletedEvent']['job']['jobConfiguration']['query']['query']
        statementType = logMessage['protoPayload']['serviceData']['jobCompletedEvent']['job']['jobConfiguration']['query']['statementType']
        print ("xxxstatementType: ", statementType)
        selectQuery = model.generateQuery(config.PROJECT_ID, config.REGION, query)
        print(f"Received Query:  ", query)
        print ("Generated Select Query", selectQuery)
        df = model.getBQResponse(config.PROJECT_ID, config.REGION, selectQuery)
        uriList = model.generate_pdf(df)
        model.ingestFiles(uriList, 0)
        # Return the response
        return {"message": "Update initialization in progress"}, 200

    except Exception as e:
        # Handle any exceptions that might occur during the process
        print(f"Error during index update: {e}")

        # Return an error response with a 500 status code
        return {"message": "Internal Server Error"}, 500


@app.get('/')
async def index(request: Request):
    return {"message": "Available APIs /initializeIndex or /updateIndex"}, 200



#model.generateQuery(config.PROJECT_ID, config.REGION, "INSERT INTO programs.program (is_pilot, offer_name) VALUES (TRUE, 'ddfdf');")
#df = model.getOffers(config.PROJECT_ID, config.REGION, config.QUERY_ALL)
#model.generate_pdf(df)
