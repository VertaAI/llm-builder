import openai

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
        engine = "text-davinci-003",
        prompt = prompt,
        max_tokens = 1024,
        n = 1,
        stop = None,
        temperature=0.5,
    )
    return completions["choices"][0]["text"]