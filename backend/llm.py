import ollama
import time


def llm_generate(prompt, stream=True, model="mistral"):
    """
    Sends a prompt to Llama 2 (quantized) and returns the response.
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
                text = chunk["message"]["content"]  # print as tokens arrive
                # print(text, end="", flush=True)
                # response_text += text
        print()  # final newline
        return text
    else:
        response = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response["message"]["content"]
