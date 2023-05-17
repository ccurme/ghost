# Fine-tuning
Ghost enables you to fine-tune an OpenAI completion model using text message data from an iPhone backup.

## Accessing your iPhone's sqlite database

## Sampling text message data
Ghost provides functionality to extract snippet of conversations from your text message history and renders them for review. You can inspect each snippet before accepting or rejecting it from the training data, to ensure no sensitive information is uploaded to third party servers.

![Sample and preview training records for a given contact](https://github.com/ccurme/ghost/assets/26529506/6a2bf481-ce48-4da8-8d11-44f1c2a45830)

This workflow is set up in a [Jupyter notebook](notebooks/sample_records.ipynb), to take advantage of Jupyter's rendering capabilities, for use with your own data.

## Fine-tuning a model
