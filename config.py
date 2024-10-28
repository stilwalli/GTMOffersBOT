prompt = "Given the below big query schema with the following table name columns:\n\nscratchzone.programs.program: offer_Name, program_description, qualification_criteria, calltoaction\n\n"
PROJECT_ID = 'helpdesk-bot-4wwq3' 
REGION = 'us-central1' # or your preferred region
BUCKET_NAME = "offersbotpdfs"
LOCATION = "global"
DATA_STORE_ID = "offersds_12w"
GROUP_SIZE = 40
QUERY_ALL = "SELECT t.offer_name as program_name, t.program_description, t.program_number as p_number, t.offer_status as launch_status, t.program_visibility, t.segments as customer_segment, t.qualification_criteria as qualification_criteria, t.calltoaction as call_to_action, t.commit_required as commit_required, FROM helpdesk-bot-422223.service_cloudbi.arcade_programs_all t WHERE offer_status IN ('Evergreen', 'Active') AND program_visibility = 'Sales All' order by t.offer_name"
#QUERY_BKPUP = "SELECT t.offer_name as program_name, t.program_description, t.program_number as p_number, t.offer_status as launch_status, t.program_visibility, t.segments as customer_segment, t.qualification_criteria as qualification_criteria, t.calltoaction as call_to_action, t.commit_required as commit_required, FROM `scratchzone.programs.program` t WHERE offer_status IN ('Evergreen', 'Active') AND program_visibility = 'Sales All'"





