"""LLM service: builds the prompt and calls the language model.

Implemented in step 4: builds the system prompt (expert estimator role plus every
`ESTIMATION_EXAMPLES` entry), sends the meeting transcription as the user message
and returns the generated estimation.
"""
