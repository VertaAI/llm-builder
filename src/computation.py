import itertools
import os
import time


def write_result(model, prompt, dataset, record, result):
    unique_id = "model_{}/prompt_{}/dataset_{}/sample_{}_{}.txt".format(
        model.get_name(), prompt.id, dataset.id, record.id, str(time.time_ns()))

    # Save result to the given file
    filepath = os.path.abspath("../cache/{}".format(unique_id))
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w") as f:
        f.write(result)


def run_computations(model, prompt, dataset):
    # Create cache folder
    if not os.path.exists("../cache"):
        os.makedirs("../cache")

    for record in dataset.records:
        unique_id = "model_{}/prompt_{}/dataset_{}/sample_{}_{}.txt".format(model.get_name(), prompt.id, dataset.id,
                                                                         record.id, str(time.time_ns()))

        result = model.predict(prompt, record.input_data)
        # Save result to the given file
        filepath = os.path.abspath("../cache/{}".format(unique_id))
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w") as f:
            f.write(result)

def run_all_computations(models, prompts, datasets):
    for (model, prompt, dataset) in itertools.product(models, prompts, datasets):
        run_computations(model, prompt, dataset)
