import ollama
import time

def llm_generate(prompt, stream=True, model="mistral"):
    """
    Sends a prompt to Ollama LLM and returns the response.
    Streams output if stream=True.
    """
    if stream:
        response_text = ""
        for chunk in ollama.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            stream=True
        ):
            if "message" in chunk and "content" in chunk["message"]:
                text = chunk["message"]["content"]
                print(text, end="", flush=True)  # prints to console immediately
                response_text += text  # accumulate full text
        print()  # final newline
        return response_text  # return full accumulated text
    else:
        response = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response["message"]["content"]
