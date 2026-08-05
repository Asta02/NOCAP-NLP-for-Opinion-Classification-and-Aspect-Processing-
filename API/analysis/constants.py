"""
=========================================================
Analysis Constants
=========================================================

Author  : Athar Winda
Project : NLP for Opinion Classification and Aspect Processing

Description
-----------
Shared constants used throughout the analysis package.
"""

from __future__ import annotations

# =====================================================
# ASPECT KEYWORDS
# =====================================================

ASPECT_KEYWORDS: dict[str, set[str]] = {

    "Salary": {
        "salary",
        "salaries",
        "pay",
        "pays",
        "wage",
        "wages",
        "bonus",
        "bonuses",
        "compensation",
        "income",
        "paycheck",
    },

    "Benefits": {
        "benefit",
        "benefits",
        "insurance",
        "medical",
        "healthcare",
        "allowance",
        "allowances",
        "vacation",
        "leave",
        "pension",
    },

    "Management": {
        "manager",
        "managers",
        "management",
        "leader",
        "leaders",
        "leadership",
        "supervisor",
        "supervisors",
        "boss",
        "bosses",
    },

    "Work-Life Balance": {
        "work-life",
        "work life",
        "balance",
        "overtime",
        "flexible",
        "flexibility",
        "remote",
        "hybrid",
    },

    "Culture": {
        "culture",
        "environment",
        "team",
        "teams",
        "coworker",
        "coworkers",
        "colleague",
        "colleagues",
        "atmosphere",
        "people",
    },

    "Career Growth": {
        "career",
        "promotion",
        "promotions",
        "growth",
        "learning",
        "training",
        "mentor",
        "mentoring",
        "development",
    },

    "Workload": {
        "workload",
        "task",
        "tasks",
        "pressure",
        "stress",
        "deadline",
        "deadlines",
    },

    "Technology": {
        "technology",
        "technologies",
        "system",
        "systems",
        "software",
        "hardware",
        "tool",
        "tools",
        "application",
        "applications",
    },
}

# =====================================================
# CLAUSE SEPARATORS
# =====================================================

CLAUSE_SPLIT_PATTERN = (
    r"\bbut\b|"
    r"\bhowever\b|"
    r"\balthough\b|"
    r"\bthough\b|"
    r"[.!?]"
)

# =====================================================
# DEFAULT SETTINGS
# =====================================================

DEFAULT_CONTEXT_WINDOW = 3