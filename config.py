prompt = "Given the below big query schema with the following table name columns:\n\nscratchzone.programs.program: offer_Name, program_description, qualification_criteria, calltoaction\n\n"
PROJECT_ID = 'scratchzone' 
REGION = 'us-central1' # or your preferred region
BUCKET_NAME = "pdfsfortesting0716"
LOCATION = "global"
DATA_STORE_ID = "testds_1725538248679"
QUERY_ALL = "SELECT offer_Name, program_description, qualification_criteria, calltoaction, offer_status FROM `scratchzone.programs.program` WHERE offer_status IN ('Active');"
