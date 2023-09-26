import itertools
import os


def run_computations(model, prompt, dataset):
    # Create cache folder
    if not os.path.exists("../cache"):
        os.makedirs("../cache")

    for sample in dataset.samples:
        unique_id = "model_{}/prompt_{}/dataset_{}/sample_{}.txt".format(model.get_name(), prompt.id, dataset.id,
                                                                         sample.id)

        result = model.predict(prompt, sample.input_data)
        # Save result to the given file
        filepath = os.path.abspath("../cache/{}".format(unique_id))
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w") as f:
            f.write(result)


def run_all_computations(models, prompts, datasets):
    for (model, prompt, dataset) in itertools.product(models, prompts, datasets):
        run_computations(model, prompt, dataset)


def load_or_compute(model, prompt, dataset, sample):
    unique_id = "model_{}/prompt_{}/dataset_{}/sample_{}.txt".format(model.get_name(), prompt.id, dataset.id, sample.id)
    filepath = os.path.abspath("../cache/{}".format(unique_id))
    # If the file exists, load the result from it
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            return f.read()

    # Otherwise, compute the result and save it to the file
    result = model.predict(prompt, sample.input_data)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w") as f:
        f.write(result)
    return result


def load(model, prompt, dataset, sample):
    unique_id = "model_{}/prompt_{}/dataset_{}/sample_{}.txt".format(model.get_name(), prompt.id, dataset.id, sample.id)
    filepath = os.path.abspath("../cache/{}".format(unique_id))
    # If the file exists, load the result from it
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            return f.read()
    return ''
