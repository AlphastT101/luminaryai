from openai import OpenAI
import time
from colorama import Fore, Style, init

init(autoreset=True)

openai = OpenAI(
    api_key="aner123!",
    base_url="http://127.0.0.1/v1"
)

start_time = time.time()
response = openai.images.generate(
    prompt="A sunset over a mountain range",
    model="flux.1"
)
elapsed_time = time.time() - start_time
print(Fore.CYAN + "Prompt: A sunset over a mountain range")
print(Fore.GREEN + f"Generated Image: {str(response.data[0].url)}")
print(Fore.YELLOW + f"Generated in: {elapsed_time:.2f} seconds")

# message = []
# while True:
#     user = input(Fore.CYAN + "You: ")  
#     user_dict = {
#         "role": "user",
#         "content": user
#     }
#     message.append(user_dict)

#     # Start timing before making the API call
#     start_time = time.time()
#     completion = openai.chat.completions.create(
#         model="gpt-4-turbofgh",
#         messages=message
#     )
#     # Calculate elapsed time
#     elapsed_time = time.time() - start_time

#     ai_content = completion.choices[0].message.content
#     ai_dict = {
#         "role": "assistant",
#         "content": ai_content
#     }
#     message.append(ai_dict)

#     # Print AI response in green and time in yellow
#     print(Fore.GREEN + f"AI: {ai_content}")
#     print(Fore.YELLOW + f"Response Time: {elapsed_time:.2f} seconds")