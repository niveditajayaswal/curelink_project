import requests
import json
import copy
from anthropic import Anthropic
from datetime import datetime

# Loading the data
data_url = "https://clchatagentassessment.s3.ap-south-1.amazonaws.com/queries.json"

response = requests.get(data_url)
data = response.json()


# Connecting to claude api key
claude_api_key = "api-key"
client = Anthropic(api_key=claude_api_key)

# prompt: deepcopy
deepcopied_data = copy.deepcopy(data)

# Function to extract day 
def get_date_index_to_consider(start_of_the_week,target_day_of_the_week):
  days_of_week = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
  start_index = days_of_week.index(start_of_the_week.lower())
  target_index = days_of_week.index(target_day_of_the_week.lower())

  days_difference = (target_index - start_index) % 7

  return days_difference


# Function to extract date and time
def filter_diet_chart(diet_chart,chat_date_str):
  diet_start_date = datetime.strptime(diet_chart['start_date'], '%Y-%m-%dT%H:%M:%SZ')
  diet_start_day = diet_start_date.strftime('%A')
  chat_date = datetime.strptime(chat_date_str, '%B %d, %Y, %I:%M %p')
  chat_day = chat_date.strftime('%A')
  index_for_chat_date = get_date_index_to_consider(diet_start_day,chat_day)
  return diet_chart['meals_by_days'][index_for_chat_date]


# Connecting with the model and prompting 
def generate_claude_response(input_json):

    profile_context = input_json['profile_context']
    patient_profile = profile_context['patient_profile']
    diet_chart = profile_context['diet_chart']

    ideal_response=  copy.deepcopy(input_json["ideal_response"])
    del input_json["ideal_response"]

    chat_date_str = input_json['chat_context']['ticket_created']
    filtered_diet_chart = filter_diet_chart(diet_chart,chat_date_str)

    chat_history = input_json['chat_context']['chat_history']
    latest_query = input_json['latest_query']
    input_json['profile_context']['diet_chart']['meals_by_days'] = [filtered_diet_chart]

    prompt = f"""
    You are provided with patient's data in input_json including their personal data including age, preferred language, diet prefernece etc and their diet plan prescribed by dietician. You are also provided with chat context including the decriptive image of the meal they are having at a specific time and one ideal response. Your task is to take that meal image and check with the diet plan to see whether they are eating prescribed food at correct time or not.

    Following are the steps you must follow to complete the task.
    1. First, you will receive a JSON file containing sample queries.

      <queries_json>
    {json.dumps(input_json, indent=2)}
    </queries_json>
     The content of this file will be provided in the following format:

                  profile_context:
                    patient_profile -> Text data for patient's profile containing medical conditions, food preferences etc.
                    program_name -> Careplan they are enrolled into
                    diet_chart -> raw json data of the diet chart they have been prescribed
                    diet_chart_url -> pdf of the diet chart precribed


                  latest_query -> Array of latest messages sent by the patient which we need to generate a reply for
                  ideal_response -> Ideal expected response for the latest query
                  chat_context:
                    ticket_id -> Unique identifier for the patient query
                    ticket_created -> timestamp at which the patient asked the query
                    chat_history -> historical chat messages with the patient from previous 6hrs


       a. Extract the relevant information, including the meal picture, patient's medical profile, diet chart, and previous chat history.

       b. Determine the ideal meal for the specific day and time based on the patient's diet chart.

       c. Compare the ideal meal with the meal in the picture to check compliance.

       d. Generate a response based on the comparison, the patient's medical profile, and previous chat history.

    4. The output for each query should be structured as follows:


    <output>
    {{

        "ticket_id": "[Query ID from the input JSON]",
        "latest_query": "[latest query from the input JSON]",,
        "generated_response": "[Generated response]",
        "ideal_response": "[Ideal response from the deepcopy of input JSON]"


    }}
    </output>




    5. When generating generated_responses:

       a. Provide specific, actionable advice in a concise form.

       b. Use the same messaging language/style as the patient.

       c. Ensure the advice is tailored to the patient's specific health conditions.

       d. Be encouraging and supportive, even when pointing out non-compliance.

       e. If the meal is not according to diet plan ask them why they are not following diet plan.

      


 


    \n\nAssistant:


    """
 
    system_prompt = "You are an expert in meal compliance and patient diet plans."
    human_prompt = f"\n\nHuman: {prompt}"

    
    response = client.completions.create(
    prompt=human_prompt,
    model="claude-2", 
    max_tokens_to_sample=300,
    temperature=0.5
)
    
    return response, ideal_response

def extract_final_response(generated_response):
    try:
        # Spliting on the 'generated_response' key and get the last segment
        response_part = generated_response.split('generated_response": "')[-1]
        
        
        final_response = response_part.rsplit('"', 1)[0]
        
        return final_response
    except IndexError:
        return ""

output_data = []

for i, patient_instance in enumerate(data):
    if i < 4:  
        response, ideal_response = generate_claude_response(patient_instance)

        generated_response_raw = response.completion.strip()
        generated_response = extract_final_response(generated_response_raw) 

  

        result = {
            "ticket_id": patient_instance['chat_context']['ticket_id'],
            "latest_query": patient_instance['latest_query'],
            "generated_response": generated_response,
            "ideal_response": ideal_response
        }

        output_data.append(result)
    else:
      break


with open('output.json', 'w') as outfile:
    json.dump(output_data, outfile, indent=2)

