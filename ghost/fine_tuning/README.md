# Fine-tuning
Ghost enables you to fine-tune an OpenAI completion model using text message data from an iPhone backup.

## Accessing your iPhone's sqlite database
iPhones store text message data in a built-in SQLite database. If you generate an unencrypted local backup of your iPhone, you should be able to access the SQLite database. Follow [this guide](https://support.apple.com/en-us/HT203977) to create a local backup and [this guide](https://support.apple.com/en-us/HT204215) to locate the backup on your filesystem. Importantly, the backup must not be encrypted.

The SQLite database is contained in this backup with a filename of `3d0d7e5fb2ce288813306e4d4636395e047a3d28`. It may be located inside a subfolder `3d/`. You can copy this file before sampling messages and fine-tuning.

## Sampling text message data
Ghost provides functionality to extract snippet of conversations from your text message history and renders them for review. You can inspect each snippet before accepting or rejecting it from the training data, to ensure no sensitive information is uploaded to third party servers.

![Sample and preview training records for a given contact](https://github.com/ccurme/ghost/assets/26529506/6a2bf481-ce48-4da8-8d11-44f1c2a45830)

This workflow is set up in a [Jupyter notebook](notebooks/sample_records.ipynb), to take advantage of Jupyter's rendering capabilities, for use with your own data. You will need to set the following in the notebook:
* `path_to_sqlite_db`: the path to the SQLite database `3d0d7e5fb2ce288813306e4d4636395e047a3d28`.
* `contact_number`: the phone number to sample from, e.g., `"+18001234567"`.
* `path_to_output_records`: path to which to write a .jsonl file containing the sampled coversations.
* `path_to_output_train_data`: path to which to write a .jsonl file of training data for OpenAI. Ghost will format the conversations into prompts and completions using the information in [prompt_prefix.md](../settings/prompt_prefix.md) and [contacts.json](../settings/contacts.json).

## Fine-tuning a model
