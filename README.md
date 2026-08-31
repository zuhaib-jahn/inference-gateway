# Inference Gateway - Relay

Basically, I just wanted to build something around LLM providers and model APIs that isn't just another chatbot.

Relay's idea is to take standard user input or issues they'd feed into an LLM, that probably wouldn't be structured optimally, and pass that through a gateway that can swap or compare different providers and model outputs.

This is mainly a way for me to learn the backend engineering around LLM systems.

Later, I might extend it so that the model choice is tailored specifically to the type of task or request it's going to be dealing with because some models are surpisingly better for specific aspects. It'd be chosen based on task type, quality, cost, latency...

# Status

Foundation

# Next

Build and test the first API endpoint: GET /health