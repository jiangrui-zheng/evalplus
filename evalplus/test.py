import ast
import random
from typing import List
import json

import openai
from openai.types.chat import ChatCompletion

from evalplus.data.utils import to_raw
from evalplus.gen import BaseGen
from evalplus.gen.util.api_request import make_auto_request




class ChatGPTGen(BaseGen):
    def __init__(self, inputs: List, signature: str, gd_code: str):
        super().__init__(inputs, signature)
        self.gd_code = gd_code
        self.prompt_messages = [
            "Please generate complex inputs to test the function.",
            "Please generate corner case inputs to test the function.",
            "Please generate difficult inputs to test the function.",
        ]
        self.iteration = 20
        self.client = openai.Client()

    def seed_selection(self) -> List:
        # get 5 for now.
        return random.sample(self.seed_pool, k=min(len(self.seed_pool), 5))

    @staticmethod
    def _parse_ret(ret: ChatCompletion) -> List:
        rets = []
        output = ret.choices[0].message.content
        if "```" in output:
            for x in output.split("```")[1].splitlines():
                if x.strip() == "":
                    continue
                try:
                    # remove comments
                    input = ast.literal_eval(f"[{x.split('#')[0].strip()}]")
                except:  # something wrong.
                    continue
                rets.append(input)
        return rets




    def chatgpt_generate(self, selected_inputs: List) -> List:
        # append the groundtruth function
        # actually it can be any function (maybe we can generate inputs for each llm generated code individually)
        attempts = 0
        max_attempts = 3

        while attempts < max_attempts:
            # message = f"Here is a function that we want to test:\n```\n{self.gd_code}\n```"
            message = f"Here is a function that we want to test:\n```\n```"
            str_inputs = "\n".join(
                [
                    ", ".join([f"'{to_raw(i)}'" if type(i) == str else str(i) for i in x])
                    for x in selected_inputs
                ]
            )
            message += f"\nThese are some example inputs used to test the function:\n```\n{str_inputs}\n```"
            message += f"\n{random.choice(self.prompt_messages)}"
            ret = make_auto_request(
                self.client,
                message=message,
                model="gpt-3.5-turbo-0125",
                # model="gpt-4-0125-preview",
                max_tokens=256,
                response_format={"type": "text"},
            )
            parsed_ret = self._parse_ret(ret)
            if len(parsed_ret) > 0:
                return parsed_ret
            else:
                # If the response is empty, increment the attempt counter and try again
                attempts += 1

        print("Failed to generate valid inputs after several attempts.")
        return []
    # write a function of asum



    def generate(self, num: int):
        while len(self.new_inputs) < num and self.iteration >= 0:
            seeds = self.seed_selection()
            new_inputs = self.chatgpt_generate(seeds)
            for new_input in new_inputs:
                if hash(str(new_input)) not in self.seed_hash:
                    self.seed_pool.append(new_input)
                    self.seed_hash.add(hash(str(new_input)))
                    self.new_inputs.append(new_input)
            self.iteration -= 1
        return self.new_inputs[:num]

def main():
    problem = {"problem": "total_bill", "prints": "print(total_bill([['apples', 6, 0.99],['milk', 1, 1.49],['bread', 2, 3.50]], 0.07))\nprint(total_bill([['apples', 6, 0.99],['milk', 1, 1.49],['bread', 2, 3.50]], 0.0))\nprint(total_bill([['bread', 2, 3.50]], 0.5))", "username": "student23", "submitted_text": "This function takes in a list of the item purchased, the price, the tax, and the overall sales tax. All of the prices and taxes within the lists are added together. The sales tax is then multiplied by the outcome of the added prices, and then the result of the multiplication is added onto the total price. The total price is then returned as the output.", "tests_passed": 0, "total_tests": 3, "prompt": "def total_bill(grocery_list, sales_tax):\n    \"\"\"\n    This function takes in a list of the item purchased, the price, the tax, and the overall sales tax. All of the prices and taxes within the lists are added together. The sales tax is then multiplied by the outcome of the added prices, and then the result of the multiplication is added onto the total price. The total price is then returned as the output.\n    \"\"\"\n    ", "first_attempt": false, "last_attempt": false, "is_success": false, "is_first_success": false, "is_last_success": false, "is_first_failure": false, "is_last_failure": false, "entry_point": "total_bill", "test": "assert total_bill([['apples', 6, 0.99],['milk', 1, 1.49],['bread', 2, 3.50]], 0.07) == 15.44\nassert total_bill([['apples', 6, 0.99],['milk', 1, 1.49],['bread', 2, 3.50]], 0.0) == 14.43\nassert total_bill([['bread', 2, 3.50]], 0.5) == 10.5", "canonical_solution": "total_price = 0\n    for i in range(len(grocery_list)):\n        total_price += grocery_list[i][1]\n    for i in range(len(sales_tax)):\n        total_price += sales_tax[i]\n    return total_price\n", "task_id": 160}

    problem["base_input"] = [[1], [13], [19], [21]]
    code = problem["prompt"] + problem["canonical_solution"]

    input_gen = ChatGPTGen(
                    problem["base_input"], problem["entry_point"], code
                ).generate(10)
    print(input_gen)
    problem['input_plus'] = input_gen
    file_path = '/data/jzheng36/evalplus/generated_inputs.jsonl'


    with open(file_path, 'a') as file:
            json_record = json.dumps(problem)
            file.write(json_record + '\n')

if __name__ == "__main__":
    main()

# write a sum function
def