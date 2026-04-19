from typing import Dict, List, Tuple, Optional
from logic.ai_explainer import get_feature_importance


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def get_enrollment_label(enrollment_pct: int) -> str:
    if enrollment_pct >= 80:
        return "Very likely to enroll"
    elif enrollment_pct >= 60:
        return "Likely to enroll"
    elif enrollment_pct >= 40:
        return "Moderate enrollment likelihood"
    else:
        return "Lower enrollment likelihood"


def compute_recommendation(
    data: Dict,
    use_sensitive: bool = False,
    numeric_policy: Optional[Dict[str, int]] = None,
) -> Tuple[int, int, str, int, List[str], Dict[str, int]]:
    gpa = float(data["gpa"])
    need = float(data["financial_need"])
    requested = float(data["requested_aid"])
    residency = data["residency"]
    enroll_prob = float(data["predicted_enrollment_probability"])
    activity = float(data["extracurricular_score"])
    first_gen = data["first_gen"]
    gender = data["gender"]
    race = data["race"]

    numeric_policy = numeric_policy or {}
    base_award = int(numeric_policy.get("base_award", 2500))
    max_extra_award = int(numeric_policy.get("max_extra_award", 9000))
    aid_adjustment = int(numeric_policy.get("aid_adjustment", 0))
    enrollment_adjustment = int(numeric_policy.get("enrollment_adjustment", 0))

    # Normalize base feature values to 0-1
    feature_values = {
        "Financial need": clamp(need / 20000, 0, 1),
        "GPA": clamp(gpa / 4.0, 0, 1),
        "Requested aid": clamp(requested / 15000, 0, 1),
        "Residency": 1.0 if residency == "In-state" else 0.65,
        "Activities": clamp(activity / 5.0, 0, 1),
    }

    if use_sensitive:
        feature_values.update(
            {
                "First-generation status": 1.0 if first_gen == "Yes" else 0.0,
                "Gender": 1.0 if gender == "Female" else 0.5,
                "Race/Ethnicity": (
                    1.0
                    if race in [
                        "Black or African American",
                        "Hispanic or Latino",
                        "Native American",
                    ]
                    else 0.5
                ),
            }
        )

    contributions = get_feature_importance(data, use_sensitive=use_sensitive)

    score = 0.0
    for feature, importance in contributions.items():
        value = feature_values.get(feature, 0.0)
        score += (importance / 100.0) * value

    score = clamp(score, 0, 1)

    raw_aid = base_award + score * max_extra_award + aid_adjustment
    raw_aid = max(0, raw_aid)

    recommended_aid = min(raw_aid, requested, need)
    recommended_aid = int(round(recommended_aid / 100.0) * 100)

    final_enrollment = int(
        round(
            clamp(
                0.70 * enroll_prob
                + 0.20 * (clamp(gpa / 4.0, 0, 1) * 100)
                + 0.10 * (clamp(activity / 5.0, 0, 1) * 100)
                + enrollment_adjustment,
                0,
                100,
            )
        )
    )

    enrollment_label = get_enrollment_label(final_enrollment)

    remaining_need = max(0, int(need - recommended_aid))

    sorted_features = sorted(contributions.items(), key=lambda x: x[1], reverse=True)
    top_features = [name for name, _ in sorted_features[:3]]

    summary_lines = [
        f"Top factor: {top_features[0]}" if len(top_features) > 0 else "Top factor unavailable",
        f"Second factor: {top_features[1]}" if len(top_features) > 1 else "Second factor unavailable",
        f"Aid recommended: ${recommended_aid:,}",
        f"LLM base award: ${base_award:,}",
    ]

    if remaining_need == 0:
        summary_lines.append("Aid meets budget need")
    else:
        summary_lines.append(f"Aid is less than budget need by ${remaining_need:,}")

    return (
        recommended_aid,
        final_enrollment,
        enrollment_label,
        remaining_need,
        summary_lines,
        contributions,
    )