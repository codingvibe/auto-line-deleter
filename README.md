# auto-line-deleter
Deletes a random line from the target file when you say a word from the ban list

# Setup Instructions
Create a `.env` file in the same directory as the script. This `.env` file should contain the following variables:

| Variable  | Description |
| ------------- | ------------- |
| ASSEMBLY_AI_API_KEY  | API key for your [Assembly AI](https://www.assemblyai.com/) account  |
| INPUT_FILE  | File path to the victim file  |
| METHOD | Method of line deletion. Currently supports LONGEST, and RANDOM |
| WORDS_LIST | Comma separated list of banned words e.g `code,array,loop` |

# Running
`python speech-to-text-to-pain.py`