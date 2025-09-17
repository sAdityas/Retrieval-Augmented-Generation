from llm import llm_generate
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

MAX_TOKENS = int(os.getenv("MAX_TOKENS", 300))



def fuse_context(docs, max_tokens=MAX_TOKENS):
    
    # Combine multiple docs into on document, non-repetitive summary
    combine_text = "\n".join(docs)
    prompt = f""" 
    You are a Smart assistant. Combine the following into text chunks into a single, clear, and concise context, Avoid Repetition. 
    Keep the meaning Accurate and under {max_tokens} tokens.
    Text Chunks:
    {combine_text}
    """

    return llm_generate(prompt)