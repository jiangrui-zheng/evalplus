import openai
from openai import OpenAI

openai.api_key = "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"
client = OpenAI(api_key = "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")
def GEN_SOLUTION(model, prompt, before_prompt, system_prompt):
    try:
        response = client.chat.completions.create(
            model=model,
            temperature=0,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": before_prompt + prompt}
            ]
        )
        return response.choices[0].message.content
    except:
        return "Bad gateway."

system_prompt = "You are a coder specializing in Python."
before_prompt = "Please directly generate code function for above requirements, start with def, not ```python:\n" #, and do not contain any other things like comment or example or assertions:\n"
# model = "gpt-4-0125-preview"
model = "gpt-3.5-turbo-0125"

solution = GEN_SOLUTION(model,"sum of integers a and b", before_prompt, system_prompt)
print(solution)