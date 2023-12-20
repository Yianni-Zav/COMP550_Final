import csv
import openai
import time

# Set your OpenAI API key
openai.api_key = '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'

# Define the rubric
RUBRIC = ("Please provide evaluations in a CSV-like format. For Irony, Exaggeration, Wordplay, and Deprecation, give a binary score (0 or 1). For Overall Humor, score from 1 to 3, where 1 is not funny, 2 is slightly funny, and 3 is funny.")


def evaluate_jokes(jokes):
    prompt = RUBRIC + "\n\n" + "\n\n".join([f"Joke {id}: {joke}\nEvaluate in CSV format (Irony,Exaggeration,Wordplay,Deprecation,Overall Humor):" for id, joke in jokes])

    retry_attempts = 3
    for attempt in range(retry_attempts):
        try:
            response = openai.Completion.create(
                engine="text-davinci-003",  # or "gpt-4" as per your preference
                prompt=prompt,
                max_tokens=1500
            )
            return parse_gpt_response(response, jokes)
        except openai.error.RateLimitError as e:
            if attempt < retry_attempts - 1:
                wait_time = 10  # Wait for 10 seconds before retrying
                print(f"Rate limit reached, retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print(f"Error in GPT API call after {retry_attempts} attempts: {e}")
                return [("0", "0", "0", "0", "1") for _ in jokes]
        except Exception as e:
            print(f"Error in GPT API call: {e}")
            return [("0", "0", "0", "0", "1") for _ in jokes]


def parse_gpt_response(response, jokes):
    # Extract the text from the GPT response
    response_text = response['choices'][0]['text'].strip()

    # Split the response text into individual evaluations
    evaluations = response_text.split("\n")

    # Initialize a list to hold parsed evaluations
    parsed_evaluations = []

    # Iterate through the evaluations
    for eval_text in evaluations:
        # Split the evaluation into its components
        parts = eval_text.split(":")[-1].strip().split(",")
        # Ensure we have the right number of components
        if len(parts) == 5:
            # Add the tuple of evaluation scores
            parsed_evaluations.append(tuple(parts))
        else:
            print("\n\nFUCKED UP PARSING \n\n")
            # Add a default evaluation in case of parsing error
            parsed_evaluations.append(("0", "0", "0", "0", "1"))

    # Ensure we have the same number of evaluations as jokes
    if len(parsed_evaluations) != len(jokes):
        # Fill in missing evaluations with default values
        print("\n\nFUCKED UP PARSING \n\n")
        parsed_evaluations.extend([("0", "0", "0", "0", "1")] * (len(jokes) - len(parsed_evaluations)))
    print("Parse Successfull")
    return parsed_evaluations

def chunk_data(data, chunk_size):
    for i in range(0, len(data), chunk_size):
        yield data[i:i + chunk_size]

if __name__ == "__main__":
    # Read the CSV file
    jokes = []
    with open('headlines.csv', mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header row
        jokes = [(row[0], row[1]) for row in reader]

    # Process the jokes in chunks and collect evaluations
    all_evaluations = []
    for chunk in chunk_data(jokes, 30):
        evaluations = evaluate_jokes(chunk)
        all_evaluations.extend(evaluations)

    # Update the CSV file with evaluations
    with open('jokes_evaluated.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['irony', 'exaggeration', 'wordplay', 'deprecation', 'overall humor'])
        for (id, joke), evaluation in zip(jokes, all_evaluations):
            writer.writerow([id, joke] + list(evaluation))

    print("Jokes evaluation completed and saved to jokes_evaluated.csv")
