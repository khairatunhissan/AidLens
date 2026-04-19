from typing import Dict


def fairness_summary(aid_with: int, aid_without: int) -> Dict:
    diff = aid_with - aid_without

    if abs(diff) <= 300:
        return {
            "label": "stable",
            "title": "Outcome remains mostly stable without sensitive attributes",
            "text": "Removing sensitive attributes changes the recommendation only slightly, suggesting relative stability.",
        }

    return {
        "label": "warning",
        "title": "Outcome changes noticeably when sensitive attributes are included",
        "text": "This comparison suggests the recommendation may be sensitive to demographic inputs and should be reviewed carefully.",
    }