import csv
import openai
import os

# Set your OpenAI API key
openai.api_key = 'your-api-key-here'

def evaluate_jokes(jokes):
    # Format the prompt for the GPT API
    prompt = "\n\n".join([f"Joke {id}: {joke}\nEvaluate in CSV format (Irony,Exaggeration,Wordplay,Deprecation,Overall Humor):" for id, joke in jokes])
    prompt += "\n\n" + RUBRIC

    # Call the GPT API
    try:
        response = openai.Completion.create(prompt=prompt, engine="davinci", max_tokens=1500)
        return parse_gpt_response(response, jokes)
    except Exception as e:
        print(f"Error in GPT API call: {e}")
        return [("0", "0", "0", "0", "1") for _ in jokes]

def parse_gpt_response(response, jokes):
    # Extract evaluations from the response
    try:
        evaluations = response['choices'][0]['text'].strip().split('\n')
        return [tuple(evaluation.split(',')) for evaluation in evaluations if evaluation]
    except Exception as e:
        print(f"Error parsing GPT response: {e}")
        return [("0", "0", "0", "0", "1") for _ in jokes]

def chunk_data(data, chunk_size):
    for i in range(0, len(data), chunk_size):
        yield data[i:i + chunk_size]

# Define the rubric
RUBRIC = ("Please provide evaluations in a CSV-like format. For Irony, Exaggeration, Wordplay, and Deprecation,"
          " give a binary score (0 or 1). For Overall Humor, score from 1 to 3, where 1 is not funny, 2 is slightly funny, and 3 is funny.")

# Read the CSV file
jokes = []
with open('jokes.csv', mode='r', encoding='utf-8') as file:
    reader = csv.reader(file)
    next(reader)  # Skip header row
    jokes = list(reader)

# Process the jokes in chunks and collect evaluations
all_evaluations = []
for chunk in chunk_data(jokes, 30):
    evaluations = evaluate_jokes(chunk)
    all_evaluations.extend(evaluations)

# Update the CSV file with evaluations
with open('jokes_evaluated.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['id', 'joke', 'irony', 'exaggeration', 'wordplay', 'deprecation', 'overall humor'])
    for (id, joke), evaluation in zip(jokes, all_evaluations):
        writer.writerow([id, joke] + list(evaluation))

print("Jokes evaluation completed and saved to jokes_evaluated.csv")
