prompt = "Given the below big query schema with the following table name columns:\n\nscratchzone.programs.program: offer_Name, program_description, qualification_criteria, calltoaction\n\n"
PROJECT_ID = 'scratchzone' 
REGION = 'us-central1' # or your preferred region
BUCKET_NAME = "pdfsfortesting0716"
LOCATION = "global"
DATA_STORE_ID = "testds_1725538248679"
QUERY_ALL = "SELECT t.offer_name as program_name, t.program_description, t.program_number as p_number, t.offer_status as launch_status, t.program_visibility, t.segments as customer_segment, t.qualification_criteria as qualification_criteria, t.calltoaction as call_to_action, t.commit_required as commit_required, FROM `scratchzone.programs.program` t WHERE offer_status IN ('Evergreen', 'Active') AND program_visibility = 'Sales All'"
