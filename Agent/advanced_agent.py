from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
import sqlite3
import json
from datetime import datetime   
import os


from dotenv import find_dotenv, load_dotenv

path_enev=find_dotenv()
load_dotenv(path_enev)

#  there are a lot of ways to talk to azure foundry using any type of sdk
# this  entra id which is in the foundry sdk 


project = AIProjectClient(
    endpoint=os.environ.get("PROJECT_ENDPOINT"),
    credential=DefaultAzureCredential()
)

openai = project.get_openai_client(
    agent_name=os.environ.get("AGENT_NAME")
)

conversation = openai.conversations.create()


# print("Ask a question about your business! (Type 'exit' to quit)\n")
# while True:
#     user_input = input("\nYou: ")
#     if user_input.lower() == "exit": break

#     response=openai.responses.create(
#         conversation=conversation.id,
#         input=user_input
#     )
#     agent_text = response.output_text

#     # if "SAVE_FILE:" in agent_text:

#     #     start_index = agent_text.find('{')
#     #     end_index = agent_text.rfind('}')

#     #     if start_index != -1 and end_index != -1:
#     #             # Slice the string to get pure JSON
#     #             clean_json_string = agent_text[start_index : end_index + 1]
                
#     #             # Now json.loads will never crash!
#     #             data = json.loads(clean_json_string)
#     #             sql_code = data["QUERY"]
                
#     #             # print(f"[Intern is running query on laptop...]: {sql_code}")
                
#     #             # Open the laptop database and run the AI's query
#     #             conn = sqlite3.connect("business_data.db")
#     #             cursor = conn.cursor()
#     #             try:
#     #                 cursor.execute(sql_code)
#     #                 db_result = str(cursor.fetchall())
#     #             except Exception as e:
#     #                 db_result = f"Error running query: {e}"
#     #             conn.close()


#     #             today = datetime.now()
#     #             formatted_date = today.strftime("%Y-%m-%d")
#     #             area=os.getcwd()
#     #             filename="SalesReport"+formatted_date+".txt"
#     #             path=os.path.join(area,filename)
#     #             print(path)

#     #             with open(path, "w", encoding="utf-8") as file:
#     #                 file.write(db_result)
                
#     #             follow_up_message = "I have successfully saved CA_Report.txt to the computer. Please tell the shopkeeper it is ready."
                
#     #             final_response = openai.responses.create(
#     #                 conversation=conversation.id,
#     #                 input=follow_up_message
#     #             )
                
#     #     else:
#     #         print("\nAgent:", agent_text)
                




#     start_index = agent_text.find('{')
#     end_index = agent_text.rfind('}')
    

#     if start_index != -1 and end_index != -1:
#         # Slice the string to get pure JSON
#         clean_json_string = agent_text[start_index : end_index + 1]
        
#         # Now json.loads will never crash!
#         data = json.loads(clean_json_string)
#         sql_code = data["QUERY"]
        
#         # print(f"[Intern is running query on laptop...]: {sql_code}")
        
#         # Open the laptop database and run the AI's query
#         conn = sqlite3.connect("business_data.db")
#         cursor = conn.cursor()
#         try:
#             cursor.execute(sql_code)
#             db_result = str(cursor.fetchall())
#         except Exception as e:
#             db_result = f"Error running query: {e}"
#         conn.close()
        
#         # 3. Send the numbers back to the Agent!
#         print(f"[Intern got the data from the database... sending it back to AI]")
#         follow_up_message = f"I ran your query. The database returned exactly this data: {db_result}. Please give the user a friendly final answer now."
        
#         final_response = openai.responses.create(
#             conversation=conversation.id,
#             input=follow_up_message
#         )
#         print("\nAgent:", final_response.output_text)
#         agent_text=final_response.output_text


#     else:
#         print("\nAgent:", agent_text)
print("--- CA AGENT IS READY ---")
print("Ask a question about your business! (Type 'exit' to quit)\n")

while True:
    user_input = input("\nYou: ")
    if user_input.lower() == "exit": break

    print("Agent is thinking...")
    response = openai.responses.create(
        conversation=conversation.id,
        input=user_input
    )
    agent_text = response.output_text

    # --- THE AUTOMATIC PROCESSING LOOP ---
    # This loop lets the AI do multiple things back-to-back without stopping!
    while True:
        
        # SCENARIO 1: The AI wants to save a file!
        if "SAVE_FILE:" in agent_text:
            report_text = agent_text.split("SAVE_FILE:")[1].strip()
            
            today = datetime.now()
            filename = f"SalesReport_{today.strftime('%Y-%m-%d')}.txt"
            path = os.path.join(os.getcwd(), filename)
            
            print(f"\n[Intern is creating {filename} on your laptop...]")
            with open(path, "w", encoding="utf-8") as file:
                file.write(report_text)
                
            follow_up_message = f"I successfully saved {filename} to the computer. Please tell the user it is ready."
            
            # Send success message to AI and update agent_text for the next loop
            agent_text = openai.responses.create(
                conversation=conversation.id,
                input=follow_up_message
            ).output_text

        # SCENARIO 2: The AI wants to run a SQL Query!
        elif "{" in agent_text and "QUERY" in agent_text:
            start_index = agent_text.find('{')
            end_index = agent_text.rfind('}')
            
            clean_json = agent_text[start_index : end_index + 1]
            sql_code = json.loads(clean_json)["QUERY"]
            
            print(f"[Intern is running query on laptop...]")
            
            conn = sqlite3.connect("business_data.db")
            cursor = conn.cursor()
            try:
                cursor.execute(sql_code)
                db_result = str(cursor.fetchall())
            except Exception as e:
                db_result = f"Error running query: {e}"
            conn.close()
            
            follow_up_message = f"I ran your query. The database returned exactly this data: {db_result}. Please give the user a friendly final answer or generate the report."
            
            # Send DB numbers to AI and update agent_text for the next loop
            agent_text = openai.responses.create(
                conversation=conversation.id,
                input=follow_up_message
            ).output_text

        # SCENARIO 3: The AI is just talking normally!
        else:
            print("\nAgent:", agent_text)
            break  # Break out of the processing loop to let the user type again