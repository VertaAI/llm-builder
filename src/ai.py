import io
import os
import urllib
from dataclasses import dataclass
from typing import Union

import openai
import requests
import validators
from bs4 import BeautifulSoup


@dataclass
class Doc:
    content: str = ""
    url: str = ""
    filename: Union[str, os.PathLike] = ""

    @classmethod
    def from_url(cls, url: str):
        # Validate URL
        validation = validators.url(url)
        if validation:
            # Parse wikipedia links
            if url.lower().find("wikipedia") != -1:
                r = urllib.request.urlopen(url).read()

                # Parsing the HTML
                soup = BeautifulSoup(r, "lxml")

                texts = soup.findAll("p")

            else:
                r = requests.get(url)
                # Parsing the HTML
                soup = BeautifulSoup(r.content, "html.parser")

                s = soup.find("div")
                texts = s.findAll("p", text=True, class_="")

            lines = [line.text.strip() for line in texts]
            content = " ".join(lines)

            # print(content)

            return cls(content=content, url=url)

        raise validators.ValidationError(message="Please provide a valid URL.")

    @classmethod
    def from_txt_file(cls, txt_file: Union[str, os.PathLike]):
        with open(txt_file, "r+") as f:
            content = f.read().decode("UTF-8")
        filename = f.name
        return cls(content=content, filename=filename)

    @classmethod
    def from_bytes(cls, fp: io.BytesIO):
        content = fp.read().decode("UTF-8")
        filename = fp.name
        return cls(content=content, filename=filename)

    @classmethod
    def from_string(cls, text: str):
        content = text
        return cls(content=content)


def summarize(text_to_summarize, prompt):
    prompt = prompt + f"{text_to_summarize}"
    return generate_response(prompt)


def refine_task_message_prompt(prompt, feedback):
    refine_prompt = f"Original instructions to student: {prompt}\n Teacher's Feedback: {feedback}\nProvide updated instructions to the student addressing the feedback as if providing instructions to a different student."
    # return single completion right now
    return generate_response(refine_prompt)


# TODO: allow hyperparameters to vary
def generate_response(prompt):
    completions = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.5,
    )
    return completions["choices"][0]["text"]
