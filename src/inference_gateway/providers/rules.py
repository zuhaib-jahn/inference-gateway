from inference_gateway.schemas import TriageDecision


class RulesBaselineProvider:
    name = "rules-baseline"
    model = "relay-rules-v1"

    def triage(self, incident: str) -> TriageDecision:
        lowered = incident.lower()
        if "suspicious" in lowered or "account" in lowered:
            category = "account_security"
            priority = "high"
        elif "subtitle" in lowered:
            category = "playback"
            priority = "normal"
        elif "progress" in lowered or "save" in lowered:
            category = "sync"
            priority = "normal"
        else:
            category = "other"
            priority = "normal"

        return TriageDecision(
            category=category,
            priority=priority,
            summary=incident[:120],
            requires_human_review=True,
        )
