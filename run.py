from evalplus.data import get_human_eval_plus, write_jsonl
import pandas
import os
import tqdm
import openai
from openai import OpenAI
from datasets import load_dataset


openai.api_key = "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"
client = OpenAI(api_key = "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")
TAB = "    "

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

samples = [
    dict(task_id=task_id, solution=GEN_SOLUTION(model,problem["prompt"], before_prompt, system_prompt))
    for task_id, problem in get_human_eval_plus().items()
]
write_jsonl("samples.jsonl", samples)