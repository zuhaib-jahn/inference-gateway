import os

provider = os.getenv("RELAY_PROVIDER", "rules")

if provider != "rules":
    raise ValueError(f"Unsupported RELAY_PROVIDER: {provider}")
