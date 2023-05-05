import json
from textwrap import wrap
from typing import IO, List, Optional, Tuple

from IPython.display import clear_output
from langchain.input import print_text
import numpy as np
import pandas as pd


STOP_SEQUENCE = "END"


def _render_conversation(df: pd.DataFrame) -> None:
    """Render conversation for review."""
    max_line_width = 100
    messages = []
    for _, row in df.iterrows():
        if row["is_from_me"]:
            messages.append("Sent:".rjust(max_line_width))
            wrapped = wrap(row["text"])
            for line in wrapped:
                messages.append(line.rjust(max_line_width))
        else:
            messages.append("Received:")
            wrapped = wrap(row["text"])
            for line in wrapped:
                messages.append(line)
        messages.append("")

    print_text("\n".join(messages))


def load_jsonl(file_path: str) -> List[dict]:
    """Load .jsonl file."""
    records = []
    with open(file_path, "r") as fp:
        for line in fp.readlines():
            records.append(json.loads(line))

    return records


def collect_samples(
    message_df: pd.DataFrame,
    output_file: IO,
    random_state: Optional[int] = None,
    min_chunk: int = 1,
    max_chunk: int = 6,
    num_samples: int = 50,
) -> None:
    """Review and collect training samples into .jsonl at output_path.

    Args:
        message_df: (pd.DataFrame) messages to sample.
        output_path: (IO) file-like object for .jsonl to which to save records.
        random_state: (int) if provided, random seed for numpy.
        min_chunk: (int) minimum number of conversation messages before completion.
        max_chunk: (int) maximum number of conversation messages before completion.
        num_samples: (int) number of samples to collect.

    Returns: None
    """
    if random_state:
        np.random.seed(random_state)
    n_rows = message_df.shape[0]
    samples = 0
    iterations = 0
    while samples < num_samples:

        chunk_size = np.random.randint(
            min_chunk + 1, max_chunk + 2
        )  # add last row for completion
        start_index = np.random.randint(n_rows - (chunk_size + 1))
        sample_df = message_df.iloc[start_index : (start_index + chunk_size)]
        if (sample_df["is_from_me"].iloc[-1] == 1) & (
            sample_df["is_from_me"].nunique() == 2
        ):
            iterations = iterations + 1
            _render_conversation(sample_df)
            print_text("")
            print_text(
                f"save this conversation? y/n. q to quit. ({samples} total so far)"
            )
            user_input = input()
            if user_input == "y":
                output_file.write(f"{sample_df.to_json()}\n")
                samples = samples + 1
            elif user_input == "q":
                break
            clear_output(wait=False)
        else:
            continue


def conversation_to_prompt(
    prompt_template: str, conversation: pd.DataFrame, ai_prefix: str, human_prefix: str
) -> Tuple[str, str]:
    """Format conversation as prompt and completion given template."""
    # TODO: conversation does not need to be a dataframe.
    conversation_rows = []
    for _, row in list(conversation.iterrows())[:-1]:
        if row["is_from_me"] == 1:
            author = ai_prefix
        else:
            author = human_prefix
        conversation_rows.append(f"{author}: {row['text']}")
    chat_history = "\n".join(conversation_rows)

    if conversation["is_from_me"].iloc[-1] != 1:
        raise AssertionError("Conversation must end with is_from_me == 1")

    prompt = prompt_template.format(chat_history=chat_history)
    completion = (
        f" {conversation['text'].iloc[-1]} {STOP_SEQUENCE}"  # Begin with whitespace
    )

    return prompt, completion
