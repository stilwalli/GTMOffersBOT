from fastapi import FastAPI, Request
import json
import base64
import config
import model

app = FastAPI()

def decode_base64(data):
  try:
    return base64.b64decode(data)
  except (TypeError, ValueError) as e:
    # Handle invalid base64 data gracefully
    print(f"Error decoding base64: {e}")
    return None

#@app.post('/initialize')
def initializeIndex():
    try:
        print("initializeIndex")
        model.delete_all_blobs(config.BUCKET_NAME)
        it = model.getOffers(config.PROJECT_ID, config.REGION, config.QUERY_ALL)
        uriList = model.generate_pdf(it)
        group_size = config.GROUP_SIZE
        full = True
        for i in range(0, len(uriList), group_size):
            group = uriList[i:i + group_size]  # Slice the list into groups of 5
            model.ingestFiles(group, 1)
            """
            if (full):
                print("Group Full ",  group)
                model.ingestFiles(group, 1)
                full = False
            else:
                print("Group Incremental ",  group)
                model.ingestFiles(group, 1)
            """
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
        print ("statementType: ", statementType)
        selectQuery = model.generateQuery(config.PROJECT_ID, config.REGION, query)
        print(f"Received Query:  ", query)
        print ("Generated Select Query", selectQuery)
        it = model.getOffers(config.PROJECT_ID, config.REGION, selectQuery)
        uriList = model.generate_pdf(it)
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
    print ("Shashank")
    return {"message": "Available APIs /initialize or /updateIndex"}, 200


#model.generateQuery(config.PROJECT_ID, config.REGION, "INSERT INTO programs.program (is_pilot, offer_name) VALUES (TRUE, 'ddfdf');")
initializeIndex()