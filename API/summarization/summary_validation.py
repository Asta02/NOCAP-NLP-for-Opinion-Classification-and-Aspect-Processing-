"""Deterministic quality validation for topic_summaries.csv."""

from pathlib import Path
import logging
import re
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"
VALIDATION_DATA_DIR = BASE_DIR / "data" / "validation"

INPUT_FILE = PROCESSED_DATA_DIR / "topic_summaries.csv"
VALIDATION_REPORT_FILE = VALIDATION_DATA_DIR / "summary_validation_report.csv"
FLAGGED_SUMMARIES_FILE = VALIDATION_DATA_DIR / "flagged_topic_summaries.csv"
VALIDATED_FILE = PROCESSED_DATA_DIR / "topic_summaries_validated.csv"
VALIDATION_SUMMARY_FILE = VALIDATION_DATA_DIR / "summary_validation_summary.csv"

SUMMARY_COLUMNS = [
    "overall_summary", "positive_summary",
    "neutral_summary", "negative_summary",
]
REQUIRED_COLUMNS = [
    "topic_id", "topic_category", "document_count",
    "positive_count", "neutral_count", "negative_count",
    *SUMMARY_COLUMNS,
]

MIN_SUMMARY_WORDS = 20
MAX_SUMMARY_WORDS = 250
MIN_REVIEWS_FOR_SENTIMENT_SUMMARY = 5

RECOMMENDATION_PATTERNS = [
    r"\bshould\b", r"\bmust\b", r"\bneeds? to\b",
    r"\bto improve\b", r"\bcould improve\b",
    r"\bwould improve\b", r"\brecommend(?:ed|ation|ations)?\b",
    r"\bmanagement should\b", r"\bhr should\b",
    r"\bcompanies should\b", r"\borganizations should\b",
    r"\bthe company should\b", r"\bimplement(?:ing)? measures\b",
    r"\bfoster(?:ing)? better\b",
]
HEADING_PATTERNS = [
    r"recurring feedback\s*:",
    r"recurring employee feedback\s*:",
    r"key recurring themes?\s*:",
    r"key themes?\s*:",
    r"main themes?\s*:",
    r"recommendations?\s*:",
]
META_PATTERNS = [
    r"\bthis final summary\b",
    r"\bthis summary captures\b",
    r"\bthis analysis suggests\b",
    r"\bbased on this analysis\b",
    r"\bprovided partial summaries\b",
    r"\boriginal partial\b",
]

POSITIVE_CLAIMS = [
    r"\bpredominantly positive\b",
    r"\boverall sentiment (?:is|remains|leans) positive\b",
    r"\bpositive aspects outweigh\b",
    r"\bgenerally positive\b",
]
NEGATIVE_CLAIMS = [
    r"\bpredominantly negative\b",
    r"\boverall sentiment (?:is|remains|leans) negative\b",
    r"\bnegative aspects outweigh\b",
    r"\bgenerally negative\b",
    r"\boverall sense of dissatisfaction\b",
]


def normalize_text(value: object) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip()
    if text.lower() in {"nan", "none", "null"}:
        return ""
    return re.sub(r"\s+", " ", text).strip()


def contains(text: str, patterns: list[str]) -> bool:
    return any(re.search(p, text, re.I) for p in patterns)


def looks_truncated(text: str) -> bool:
    if not text:
        return False
    text = text.rstrip()
    if text.endswith((",", ";", ":")):
        return True
    if re.search(r"[-–—:#*]\s*$", text):
        return True
    # Strong incomplete-ending signals seen in generated output.
    return bool(re.search(
        r"\b(?:the|a|an|and|or|to|of|for|with|while|which|that|"
        r"as|in|on|by|from|company|organization|work)\s*$",
        text, re.I
    ))


def validate_columns(df: pd.DataFrame) -> None:
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError("Missing required columns: " + ", ".join(missing))


def validate_row(row: pd.Series) -> dict[str, object]:
    issues: list[str] = []

    total = int(row["document_count"])
    pos = int(row["positive_count"])
    neu = int(row["neutral_count"])
    neg = int(row["negative_count"])

    if pos + neu + neg != total:
        issues.append("counts:sentiment_total_mismatch")

    expected = {
        "positive_summary": pos,
        "neutral_summary": neu,
        "negative_summary": neg,
    }
    for col, count in expected.items():
        if count >= MIN_REVIEWS_FOR_SENTIMENT_SUMMARY and not normalize_text(row[col]):
            issues.append(f"{col}:missing_expected_summary")

    word_counts = {}
    for col in SUMMARY_COLUMNS:
        text = normalize_text(row[col])
        wc = len(text.split()) if text else 0
        word_counts[f"{col}_word_count"] = wc

        if not text:
            issues.append(f"{col}:empty")
            continue
        if wc < MIN_SUMMARY_WORDS:
            issues.append(f"{col}:too_short")
        if wc > MAX_SUMMARY_WORDS:
            issues.append(f"{col}:too_long")
        if looks_truncated(text):
            issues.append(f"{col}:possible_truncation")
        if contains(text, RECOMMENDATION_PATTERNS):
            issues.append(f"{col}:recommendation_language")
        if contains(text, HEADING_PATTERNS):
            issues.append(f"{col}:unwanted_heading")
        if contains(text, META_PATTERNS):
            issues.append(f"{col}:generation_meta_text")
        if "#" in text:
            issues.append(f"{col}:hashtag")
        if re.search(r"(?:^|\s)[-*]\s+\*{0,2}[A-Za-z]", text):
            issues.append(f"{col}:list_or_markdown_format")

    overall = normalize_text(row["overall_summary"])
    pos_ratio = pos / max(total, 1)
    neg_ratio = neg / max(total, 1)

    # Conservative contradiction rule: only flag strong majority mismatch.
    if pos_ratio >= 0.60 and neg_ratio <= 0.30 and contains(overall, NEGATIVE_CLAIMS):
        issues.append("overall_summary:possible_negative_contradiction")
    if neg_ratio >= 0.60 and pos_ratio <= 0.30 and contains(overall, POSITIVE_CLAIMS):
        issues.append("overall_summary:possible_positive_contradiction")

    issues = list(dict.fromkeys(issues))

    return {
        "topic_id": int(row["topic_id"]),
        "topic_category": row["topic_category"],
        "document_count": total,
        "positive_ratio": round(pos_ratio, 4),
        "neutral_ratio": round(neu / max(total, 1), 4),
        "negative_ratio": round(neg_ratio, 4),
        **word_counts,
        "issue_count": len(issues),
        "validation_status": "PASS" if not issues else "REVIEW",
        "issues": "; ".join(issues),
    }


def clean_formatting(value: object) -> str:
    text = normalize_text(value)
    if not text:
        return ""
    # Only remove obvious format/meta tails; do not rewrite semantic content.
    text = re.sub(
        r"\s*---\s*\*{0,2}Note:\*{0,2}.*$", "", text, flags=re.I
    )
    text = re.sub(
        r"\b(?:Recurring Employee Feedback|Recurring Feedback|"
        r"Key Recurring Themes?|Key Themes?|Main Themes?)\s*:.*$",
        "", text, flags=re.I
    )
    text = re.sub(r"(?<!\w)#[A-Za-z][\w-]*", "", text)
    return re.sub(r"\s+", " ", text).strip()


def run_validation(input_path: Path = INPUT_FILE) -> tuple[pd.DataFrame, pd.DataFrame]:
    logging.info("Loading %s", input_path)
    if not input_path.exists():
        raise FileNotFoundError(f"File not found: {input_path}")

    df = pd.read_csv(input_path)
    validate_columns(df)

    report = pd.DataFrame(
        validate_row(row) for _, row in df.iterrows()
    )

    # Exact duplicate overall summaries.
    normalized = df["overall_summary"].map(normalize_text).str.lower()
    dup_ids = set(df.loc[normalized.ne("") & normalized.duplicated(False), "topic_id"].astype(int))
    for topic_id in dup_ids:
        mask = report["topic_id"] == topic_id
        old = report.loc[mask, "issues"].iloc[0]
        issue = "overall_summary:duplicate_summary"
        report.loc[mask, "issues"] = f"{old}; {issue}" if old else issue
        report.loc[mask, "issue_count"] += 1
        report.loc[mask, "validation_status"] = "REVIEW"

    validated = df.copy()
    for col in SUMMARY_COLUMNS:
        validated[col] = validated[col].map(clean_formatting)

    validated = validated.merge(
        report[["topic_id", "validation_status", "issue_count", "issues"]],
        on="topic_id", how="left"
    )

    VALIDATION_DATA_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

    report.to_csv(VALIDATION_REPORT_FILE, index=False, encoding="utf-8-sig")

    flagged_ids = set(
        report.loc[report["validation_status"] == "REVIEW", "topic_id"].astype(int)
    )
    df[df["topic_id"].astype(int).isin(flagged_ids)].to_csv(
        FLAGGED_SUMMARIES_FILE, index=False, encoding="utf-8-sig"
    )
    validated.to_csv(VALIDATED_FILE, index=False, encoding="utf-8-sig")

    total = len(report)
    passed = int((report["validation_status"] == "PASS").sum())
    summary = pd.DataFrame([
        {"metric": "total_topics", "value": total},
        {"metric": "passed_topics", "value": passed},
        {"metric": "flagged_topics", "value": total - passed},
        {"metric": "pass_rate", "value": round(passed / total, 4) if total else 0},
        {"metric": "total_issues", "value": int(report["issue_count"].sum())},
    ])
    summary.to_csv(VALIDATION_SUMMARY_FILE, index=False, encoding="utf-8-sig")

    print("\n" + "=" * 60)
    print("TOPIC SUMMARY VALIDATION")
    print("=" * 60)
    print(f"Total topics : {total}")
    print(f"PASS         : {passed}")
    print(f"REVIEW       : {total - passed}")
    if total:
        print(f"Pass rate    : {passed / total:.2%}")

    exploded = (
        report.loc[report["issues"].ne(""), "issues"]
        .str.split("; ").explode()
    )
    print("\nMost common issues:")
    print(exploded.value_counts().head(15).to_string() if not exploded.empty else "None")

    print("\nFlagged topics:")
    flagged_report = report[report["validation_status"] == "REVIEW"]
    if flagged_report.empty:
        print("None")
    else:
        print(flagged_report[
            ["topic_id", "topic_category", "issue_count", "issues"]
        ].head(30).to_string(index=False))

    logging.info("Validation report: %s", VALIDATION_REPORT_FILE)
    logging.info("Flagged summaries: %s", FLAGGED_SUMMARIES_FILE)
    logging.info("Validated dataset: %s", VALIDATED_FILE)

    return validated, report


def main() -> None:
    run_validation()


if __name__ == "__main__":
    main()
