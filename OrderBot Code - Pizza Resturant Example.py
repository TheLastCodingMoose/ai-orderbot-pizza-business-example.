import os
import time
from openai import OpenAI, RateLimitError, APIError
from dotenv import load_dotenv

# from dotenv import load_dotenv, find_dotenv
# _ = load_dotenv(find_dotenv()) # read local .env file

# Load .env file variables into environment
load_dotenv()

api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    print("ERROR: OPENAI_API_KEY environment variable not found!")
    print("Please set your OpenAI API key in the Secrets tool.")
else:
    print("API key found and configured.")

client = OpenAI(api_key=api_key)

def get_completion(prompt, model="gpt-3.5-turbo"):
    messages = [{"role": "user", "content": prompt}]
    max_retries = 3
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0, # this is the degree of randomness of the model's output
            )
            return response.choices[0].message.content
        except RateLimitError:
            if attempt < max_retries - 1:
                print(f"Rate limit exceeded. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                return "Sorry, I'm currently experiencing high demand. Please try again later."
        except APIError as e:
            return f"API Error: {str(e)}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"

def get_completion_from_messages(messages, model="gpt-3.5-turbo", temperature=0):
    max_retries = 3
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature, # this is the degree of randomness of the model's output
            )
            return response.choices[0].message.content
        except RateLimitError:
            if attempt < max_retries - 1:
                print(f"Rate limit exceeded. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                return "Sorry, I'm currently experiencing high demand. Please try again later."
        except APIError as e:
            return f"API Error: {str(e)}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"

def collect_messages(_):
    prompt = inp.value_input
    inp.value = ''
    context.append({'role':'user', 'content':f"{prompt}"})
    response = get_completion_from_messages(context) 
    context.append({'role':'assistant', 'content':f"{response}"})
    panels.append(
        pn.Row('User:', pn.pane.Markdown(prompt, width=600)))
    panels.append(
        pn.Row('Assistant:', pn.pane.Markdown(response, width=600)))

    return pn.Column(*panels)

import panel as pn  # GUI
pn.extension()

panels = [] # collect display 

context = [ {'role':'system', 'content':"""
You are OrderBot, an automated service to collect orders for a pizza restaurant. \
You first greet the customer, then collects the order, \
and then asks if it's a pickup or delivery. \
You wait to collect the entire order, then summarize it and check for a final \
time if the customer wants to add anything else. \
If it's a delivery, you ask for an address. \
Finally you collect the payment.\
Make sure to clarify all options, extras and sizes to uniquely \
identify the item from the menu.\
You respond in a short, very conversational friendly style. \
The menu includes \
pepperoni pizza  12.95, 10.00, 7.00 \
cheese pizza   10.95, 9.25, 6.50 \
eggplant pizza   11.95, 9.75, 6.75 \
fries 4.50, 3.50 \
greek salad 7.25 \
Toppings: \
extra cheese 2.00, \
mushrooms 1.50 \
sausage 3.00 \
canadian bacon 3.50 \
AI sauce 1.50 \
peppers 1.00 \
Drinks: \
coke 3.00, 2.00, 1.00 \
sprite 3.00, 2.00, 1.00 \
bottled water 5.00 \
"""} ]  # accumulate messages


inp = pn.widgets.TextInput(value="Hi", placeholder='Enter text here…')
button_conversation = pn.widgets.Button(name="Chat!")

interactive_conversation = pn.bind(collect_messages, button_conversation)

dashboard = pn.Column(
    inp,
    pn.Row(button_conversation),
    pn.panel(interactive_conversation, loading_indicator=True, height=300),
)

dashboard.servable()

# Removed automatic API call - this was causing rate limiting on startup
# You can manually trigger order summaries through the chat interface instead