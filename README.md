# curelink_project


This project checks whether a patient's meal aligns with their prescribed diet plan using the Claude API from Anthropic. The script processes a JSON file containing patient queries, compares the provided meal image with the prescribed diet, and generates a response based on the comparison.

Important:
"I have restricted the output generation to 4 responses due to the daily token limit associated with my API key."

## Prerequisites

Ensure you have the following installed:

- Python 3.6 or later
- Required Python libraries (see below)

## Installation & Setup

Follow these steps to get started:

```bash
# Step 1: Clone the Repository
git clone https://github.com/niveditajayaswal/curelink_project.git
cd curelink_project

# Step 2: Install Required Libraries
pip install requests anthropic

# Step 3: Set Up Your Claude API Key
# 1. Obtain your API key from the Anthropic website.
# 2. Open the diet_compliance.py file.
# 3. Replace the placeholder "api-key" with your actual API key:
# claude_api_key = "your-api-key-here"

# Run the Python script
python python.py

Files
python.py: The main Python script for processing patient queries.
output.json: The output file containing the generated responses.
README.md: This file, containing instructions for installation and usage.
