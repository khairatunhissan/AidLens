import os
import json
from typing import Dict, List, Any
import streamlit as st
from openai import OpenAI


def _get_client() -> OpenAI:
    api_key = None

    try:
        api_key = st.secrets.get("GROQ_API_KEY")
    except Exception:
        api_key = None

    if not api_key:
        api_key = os.environ.get("GROQ_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is not set. Add it in Streamlit Cloud Secrets or set it locally as an environment variable."
        )

    return OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=api_key,
    )


def _clamp_int(value: int, low: int, high: int) -> int:
    return max(low, min(high, int(value)))


def build_explanation_prompt(
    data: Dict, recommended_aid: int, enrollment: int, fairness_delta: int
) -> str:
    return f"""
You are helping explain a financial-aid recommendation in a human-centered AI interface.

Applicant data:
- GPA: {data['gpa']}
- Family income: {data['family_income']}
- Financial need: {data['financial_need']}
- Requested aid: {data['requested_aid']}
- Residency: {data['residency']}
- Intended major: {data['major']}
- Predicted enrollment probability: {data['predicted_enrollment_probability']}%
- Extracurricular strength: {data['extracurricular_score']}/5
- Gender: {data['gender']}
- Race/Ethnicity: {data['race']}
- First-generation: {data['first_gen']}

System outputs:
- Recommended aid: ${recommended_aid}
- Predicted enrollment: {enrollment}%
- Fairness comparison difference: ${fairness_delta}

Return valid JSON with exactly these keys:
{{
  "explanation": "...",
  "fairness_text": "..."
}}

Rules:
- Keep both fields short and clear.
- Use neutral and transparent language.
- Do not claim certainty.
- Mention the most influential non-sensitive factors in the explanation.
- In fairness_text, interpret whether the fairness difference is small or noticeable.
"""


def build_feature_importance_prompt(data: Dict, use_sensitive: bool) -> str:
    if use_sensitive:
        feature_list = [
            "Financial need",
            "GPA",
            "Requested aid",
            "Residency",
            "Activities",
            "First-generation status",
            "Gender",
            "Race/Ethnicity",
        ]
        feature_rule = (
            "You may consider both non-sensitive and sensitive features because this is the stability comparison version."
        )
    else:
        feature_list = [
            "Financial need",
            "GPA",
            "Requested aid",
            "Residency",
            "Activities",
        ]
        feature_rule = (
            "Do not use sensitive features in this version. Only use the listed non-sensitive features."
        )

    return f"""
You are assigning feature importance for a financial-aid recommendation prototype.

Applicant data:
- GPA: {data['gpa']}
- Family income: {data['family_income']}
- Financial need: {data['financial_need']}
- Requested aid: {data['requested_aid']}
- Residency: {data['residency']}
- Intended major: {data['major']}
- Predicted Enrollment Probability: {data['predicted_enrollment_probability']}%
- Extracurricular strength: {data['extracurricular_score']}/5
- Gender: {data['gender']}
- Race/Ethnicity: {data['race']}
- First-generation: {data['first_gen']}

Features to assign importance to:
{json.dumps(feature_list)}

Rules:
- Return raw JSON only.
- Do not use markdown.
- Do not use code fences.
- Do not add explanation text.
- Use exactly these feature names as keys.
- Assign integer importance values that sum to 100.
- Higher value means more influence on aid recommendation for this specific applicant.
- Make the weights applicant-specific, not generic.
- Consider the actual applicant profile while distributing the weights.
- Prioritize financial need and academic strength when appropriate.
- {feature_rule}

Return format:
{{
  "feature_importance": {{
    "Financial need": 0,
    "GPA": 0,
    "Requested aid": 0,
    "Residency": 0,
    "Activities": 0
  }}
}}

If sensitive features are included, also include:
- "First-generation status"
- "Gender"
- "Race/Ethnicity"
"""


def build_numeric_policy_prompt(data: Dict, use_sensitive: bool) -> str:
    scope_line = (
        "You may consider both non-sensitive and sensitive features because this is the fairness-comparison version."
        if use_sensitive
        else
        "Do not use sensitive features in this version. Use only non-sensitive features."
    )

    return f"""
You are generating numeric policy parameters for a financial-aid recommendation prototype.

Applicant data:
- GPA: {data['gpa']}
- Family income: {data['family_income']}
- Financial need: {data['financial_need']}
- Requested aid: {data['requested_aid']}
- Residency: {data['residency']}
- Intended major: {data['major']}
- Predicted enrollment probability: {data['predicted_enrollment_probability']}%
- Extracurricular strength: {data['extracurricular_score']}/5
- Gender: {data['gender']}
- Race/Ethnicity: {data['race']}
- First-generation: {data['first_gen']}

Return raw JSON only with exactly these keys:
{{
  "base_award": 0,
  "max_extra_award": 0,
  "aid_adjustment": 0,
  "enrollment_adjustment": 0
}}

Rules:
- Do not use markdown.
- Do not use code fences.
- base_award must be an integer from 1500 to 4000.
- max_extra_award must be an integer from 6000 to 11000.
- aid_adjustment must be an integer from -1500 to 1500.
- enrollment_adjustment must be an integer from -8 to 8.
- Make the values applicant-specific.
- Favor higher base_award or max_extra_award for stronger need and stronger academic signal when appropriate.
- Keep enrollment_adjustment small and conservative.
- {scope_line}
"""


def build_decision_support_prompt(
    data: Dict,
    recommended_aid: int,
    enrollment: int,
    remaining_need: int,
    top_features: List[str],
    fairness_delta: int,
) -> str:
    return f"""
You are helping write decision-support text for a human-centered financial-aid prototype.

Applicant data:
- GPA: {data['gpa']}
- Family income: {data['family_income']}
- Financial need: {data['financial_need']}
- Requested aid: {data['requested_aid']}
- Residency: {data['residency']}
- Intended major: {data['major']}
- Predicted enrollment probability: {data['predicted_enrollment_probability']}%
- Extracurricular strength: {data['extracurricular_score']}/5

Computed outputs:
- Recommended aid: ${recommended_aid}
- Final enrollment estimate: {enrollment}%
- Remaining need: ${remaining_need}
- Top non-sensitive factors: {", ".join(top_features) if top_features else "Not available"}
- Fairness delta: ${fairness_delta}

Return valid JSON with exactly these keys:
{{
  "enrollment_text": "...",
  "summary_lines": ["...", "...", "...", "..."],
  "review_note": "..."
}}

Rules:
- Return raw JSON only.
- Do not use markdown.
- Do not use code fences.
- enrollment_text must be a short phrase like:
  "Very likely to enroll", "Likely to enroll", "Moderate enrollment likelihood", or "Lower enrollment likelihood".
- summary_lines must contain exactly 4 short bullet-style strings.
- review_note must be 1 short sentence for a human reviewer.
- Do not mention sensitive features in summary_lines or review_note.
- Use neutral and transparent language.
- Do not claim certainty.
"""


def _strip_code_fences(text: str) -> str:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()

        if lines:
            lines = lines[1:]

        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]

        cleaned = "\n".join(lines).strip()

    return cleaned


def get_feature_importance(data: Dict, use_sensitive: bool) -> Dict[str, int]:
    client = _get_client()
    prompt = build_feature_importance_prompt(data, use_sensitive)

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "You are a careful assistant that returns raw JSON only.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )

    output_text = response.choices[0].message.content.strip()
    cleaned_text = _strip_code_fences(output_text)

    try:
        parsed = json.loads(cleaned_text)
        feature_importance = parsed["feature_importance"]

        cleaned = {str(k): int(v) for k, v in feature_importance.items()}
        total = sum(cleaned.values())

        if total <= 0:
            raise ValueError("Feature importance total must be positive.")

        normalized = {
            key: int(round(value * 100 / total))
            for key, value in cleaned.items()
        }

        drift = 100 - sum(normalized.values())
        if drift != 0:
            first_key = next(iter(normalized))
            normalized[first_key] += drift

        return normalized

    except Exception as e:
        raise RuntimeError(
            f"Failed to parse feature importance JSON from model output.\nRaw output:\n{output_text}"
        ) from e


def get_llm_numeric_policy(data: Dict, use_sensitive: bool) -> Dict[str, int]:
    client = _get_client()
    prompt = build_numeric_policy_prompt(data, use_sensitive)

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "You are a careful assistant that returns raw JSON only.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )

    output_text = response.choices[0].message.content.strip()
    cleaned_text = _strip_code_fences(output_text)

    try:
        parsed = json.loads(cleaned_text)

        return {
            "base_award": _clamp_int(parsed.get("base_award", 2500), 1500, 4000),
            "max_extra_award": _clamp_int(parsed.get("max_extra_award", 9000), 6000, 11000),
            "aid_adjustment": _clamp_int(parsed.get("aid_adjustment", 0), -1500, 1500),
            "enrollment_adjustment": _clamp_int(parsed.get("enrollment_adjustment", 0), -8, 8),
            "raw_output": output_text,
            "prompt": prompt,
        }

    except Exception:
        return {
            "base_award": 2500,
            "max_extra_award": 9000,
            "aid_adjustment": 0,
            "enrollment_adjustment": 0,
            "raw_output": output_text,
            "prompt": prompt,
        }


def get_llm_explanation(
    data: Dict, recommended_aid: int, enrollment: int, fairness_delta: int
) -> Dict[str, str]:
    client = _get_client()
    prompt = build_explanation_prompt(data, recommended_aid, enrollment, fairness_delta)

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "You are a careful AI assistant for a human-centered financial aid interface.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
    )

    output_text = response.choices[0].message.content.strip()
    cleaned_text = _strip_code_fences(output_text)

    try:
        parsed = json.loads(cleaned_text)
        explanation = parsed.get("explanation", "").strip()
        fairness_text = parsed.get("fairness_text", "").strip()

        if not explanation or not fairness_text:
            raise ValueError("Missing expected JSON keys.")

        return {
            "explanation": explanation,
            "fairness_text": fairness_text,
            "raw_output": output_text,
        }

    except Exception:
        return {
            "explanation": output_text,
            "fairness_text": "The model returned text, but not in the exact JSON format requested.",
            "raw_output": output_text,
        }


def get_llm_decision_support(
    data: Dict,
    recommended_aid: int,
    enrollment: int,
    remaining_need: int,
    top_features: List[str],
    fairness_delta: int,
) -> Dict[str, Any]:
    client = _get_client()
    prompt = build_decision_support_prompt(
        data,
        recommended_aid,
        enrollment,
        remaining_need,
        top_features,
        fairness_delta,
    )

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "You are a careful assistant that returns raw JSON only.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
    )

    output_text = response.choices[0].message.content.strip()
    cleaned_text = _strip_code_fences(output_text)

    try:
        parsed = json.loads(cleaned_text)

        enrollment_text = str(parsed.get("enrollment_text", "")).strip()
        summary_lines = parsed.get("summary_lines", [])
        review_note = str(parsed.get("review_note", "")).strip()

        if not isinstance(summary_lines, list):
            raise ValueError("summary_lines must be a list.")

        summary_lines = [str(x).strip() for x in summary_lines if str(x).strip()]

        return {
            "enrollment_text": enrollment_text,
            "summary_lines": summary_lines,
            "review_note": review_note,
            "raw_output": output_text,
            "prompt": prompt,
        }

    except Exception:
        return {
            "enrollment_text": "",
            "summary_lines": [],
            "review_note": "",
            "raw_output": output_text,
            "prompt": prompt,
        }