"""GenAI Explanation Service.

Converts structured ML outputs (risk score + feature contributions) into a
readable decision-brief sentence for officials. GenAI is used ONLY for
natural-language narration — never to invent numbers, diagnose patients, or
assert causal relationships.

If IBM watsonx credentials are configured (settings.GENAI_PROVIDER ==
"watsonx"), this module can be wired to call it; otherwise it transparently
falls back to a deterministic, template-based narrative built entirely from
the structured inputs, so the demo works with zero external dependencies.
"""
from dataclasses import dataclass
from backend.config import settings


@dataclass
class ExplanationInput:
    village_name: str
    predicted_risk: float
    risk_category: str
    is_paradox: bool
    paradox_note: str | None
    top_factors: list[tuple[str, float]]  # (factor_name, contribution_pct)


@dataclass
class ExplanationOutput:
    headline: str
    narrative: str
    generated_by: str


def _template_narrative(x: ExplanationInput) -> str:
    sentence = (
        f"{x.village_name} is currently classified as {x.risk_category.lower()} risk "
        f"(model-predicted risk score {x.predicted_risk:.0f}/100)."
    )
    if x.top_factors:
        factor_phrases = ", ".join(f"{name} ({pct:.0f}%)" for name, pct in x.top_factors[:3])
        sentence += f" The strongest contributing indicators are {factor_phrases}."
    else:
        sentence += " No single indicator stands out as a dominant risk driver in the current model."
    if x.is_paradox and x.paradox_note:
        sentence += (
            " Existing infrastructure appears relatively adequate, suggesting that targeted "
            "service-delivery, staffing and outreach interventions may be more appropriate than "
            "immediate infrastructure expansion."
        )
    sentence += (
        " This is a decision-support interpretation based on available indicators, not a medical "
        "diagnosis or a proven causal conclusion, and should be validated in the field before action is taken."
    )
    return sentence


def generate_explanation(x: ExplanationInput) -> ExplanationOutput:
    if settings.GENAI_PROVIDER == "watsonx" and settings.WATSONX_API_KEY:
        # Placeholder for a real watsonx.ai call: the structured `x` payload above
        # (risk score + ranked contributing factors + paradox flag) is exactly what
        # would be sent as context to the model, with a system prompt instructing it
        # to summarize only — never invent statistics or causal claims. Falling back
        # to the deterministic template keeps the demo fully functional without
        # requiring live credentials.
        try:
            narrative = _template_narrative(x)  # TODO: replace with watsonx.ai completion call
            return ExplanationOutput(
                headline=f"{x.risk_category} risk — {x.village_name}",
                narrative=narrative,
                generated_by="watsonx (fallback template — no live call configured)",
            )
        except Exception:
            pass

    return ExplanationOutput(
        headline=f"{x.risk_category} risk — {x.village_name}",
        narrative=_template_narrative(x),
        generated_by="template",
    )
