from __future__ import annotations

from typing import Any


def validate_report_structure(report: dict[str, Any]) -> list[str]:
    """
    Validates that the report follows the expected schema structure.
    Returns a list of validation errors (empty if valid).
    """
    errors: list[str] = []

    required_fields = ["ticker", "quarter", "summary", "guidance", "growth_drivers", "risks", "margin_dynamics", "qa_pressure_points"]
    for field in required_fields:
        if field not in report:
            errors.append(f"Missing required field: {field}")

    if "summary" in report:
        summary = report["summary"]
        if not isinstance(summary, dict):
            errors.append("Summary must be a dictionary")
        else:
            if "high_level" not in summary:
                errors.append("Summary missing 'high_level' field")
            if "tone" not in summary:
                errors.append("Summary missing 'tone' field")
            elif summary["tone"] not in ["neutral", "positive", "negative"]:
                errors.append(f"Invalid tone value: {summary['tone']}")

    list_fields = ["guidance", "growth_drivers", "risks", "margin_dynamics", "qa_pressure_points"]
    for field in list_fields:
        if field in report:
            if not isinstance(report[field], list):
                errors.append(f"{field} must be a list")
            else:
                for idx, item in enumerate(report[field]):
                    if not isinstance(item, dict):
                        errors.append(f"{field}[{idx}] must be a dictionary")

    return errors


def validate_evidence_coverage(report: dict[str, Any]) -> dict[str, Any]:
    """
    Checks that claims have evidence quotes.
    Returns metrics about evidence coverage.
    """
    metrics = {
        "total_claims": 0,
        "claims_with_evidence": 0,
        "claims_without_evidence": 0,
        "evidence_coverage_rate": 0.0,
        "details": [],
    }

    def check_evidence(item: dict[str, Any], claim_field: str, evidence_fields: list[str], section_name: str) -> None:
        claim = item.get(claim_field, "")
        if not claim or claim.strip() == "":
            return

        metrics["total_claims"] += 1
        has_evidence = False

        for evidence_field in evidence_fields:
            evidence = item.get(evidence_field)
            if evidence and isinstance(evidence, str) and evidence.strip() and evidence.strip().lower() != "unknown":
                has_evidence = True
                break

        if has_evidence:
            metrics["claims_with_evidence"] += 1
        else:
            metrics["claims_without_evidence"] += 1
            metrics["details"].append({
                "section": section_name,
                "claim": claim[:100] + "..." if len(claim) > 100 else claim,
                "missing_evidence_fields": evidence_fields,
            })

    if "guidance" in report and isinstance(report["guidance"], list):
        for item in report["guidance"]:
            check_evidence(item, "claim", ["evidence_current", "evidence_prev"], "guidance")

    if "growth_drivers" in report and isinstance(report["growth_drivers"], list):
        for item in report["growth_drivers"]:
            check_evidence(item, "claim", ["evidence"], "growth_drivers")

    if "risks" in report and isinstance(report["risks"], list):
        for item in report["risks"]:
            check_evidence(item, "claim", ["evidence_current", "evidence_first_mention"], "risks")

    if "margin_dynamics" in report and isinstance(report["margin_dynamics"], list):
        for item in report["margin_dynamics"]:
            check_evidence(item, "claim", ["evidence"], "margin_dynamics")

    if "qa_pressure_points" in report and isinstance(report["qa_pressure_points"], list):
        for item in report["qa_pressure_points"]:
            check_evidence(item, "theme", ["evidence_question", "evidence_answer"], "qa_pressure_points")

    if metrics["total_claims"] > 0:
        metrics["evidence_coverage_rate"] = metrics["claims_with_evidence"] / metrics["total_claims"]

    return metrics


def validate_citation_format(report: dict[str, Any]) -> dict[str, Any]:
    """
    Checks if evidence quotes contain citation references (document_id, chunk_id).
    Returns metrics about citation quality.
    """
    metrics = {
        "total_evidence_fields": 0,
        "evidence_with_citations": 0,
        "evidence_without_citations": 0,
        "citation_rate": 0.0,
    }

    def check_citations(item: dict[str, Any], evidence_fields: list[str]) -> None:
        for field in evidence_fields:
            evidence = item.get(field)
            if evidence and isinstance(evidence, str) and evidence.strip() and evidence.strip().lower() != "unknown":
                metrics["total_evidence_fields"] += 1
                if "document_id" in evidence.lower() or "chunk_id" in evidence.lower():
                    metrics["evidence_with_citations"] += 1
                else:
                    metrics["evidence_without_citations"] += 1

    if "guidance" in report and isinstance(report["guidance"], list):
        for item in report["guidance"]:
            check_citations(item, ["evidence_current", "evidence_prev"])

    if "growth_drivers" in report and isinstance(report["growth_drivers"], list):
        for item in report["growth_drivers"]:
            check_citations(item, ["evidence"])

    if "risks" in report and isinstance(report["risks"], list):
        for item in report["risks"]:
            check_citations(item, ["evidence_current", "evidence_first_mention"])

    if "margin_dynamics" in report and isinstance(report["margin_dynamics"], list):
        for item in report["margin_dynamics"]:
            check_citations(item, ["evidence"])

    if "qa_pressure_points" in report and isinstance(report["qa_pressure_points"], list):
        for item in report["qa_pressure_points"]:
            check_citations(item, ["evidence_question", "evidence_answer"])

    if metrics["total_evidence_fields"] > 0:
        metrics["citation_rate"] = metrics["evidence_with_citations"] / metrics["total_evidence_fields"]

    return metrics


def evaluate_report(report: dict[str, Any]) -> dict[str, Any]:
    """
    Comprehensive evaluation of a report.
    Returns evaluation results with scores and issues.
    """
    structure_errors = validate_report_structure(report)
    evidence_metrics = validate_evidence_coverage(report)
    citation_metrics = validate_citation_format(report)

    evaluation = {
        "is_valid": len(structure_errors) == 0,
        "structure_errors": structure_errors,
        "evidence_coverage": evidence_metrics,
        "citation_quality": citation_metrics,
        "overall_score": 0.0,
        "recommendations": [],
    }

    if not evaluation["is_valid"]:
        evaluation["recommendations"].append("Fix schema structure errors before proceeding")

    if evidence_metrics["total_claims"] > 0:
        coverage_rate = evidence_metrics["evidence_coverage_rate"]
        if coverage_rate < 0.9:
            evaluation["recommendations"].append(
                f"Low evidence coverage ({coverage_rate:.1%}). Ensure all claims have supporting quotes."
            )
        if evidence_metrics["claims_without_evidence"] > 0:
            evaluation["recommendations"].append(
                f"{evidence_metrics['claims_without_evidence']} claims missing evidence quotes"
            )

    if citation_metrics["total_evidence_fields"] > 0:
        citation_rate = citation_metrics["citation_rate"]
        if citation_rate < 0.5:
            evaluation["recommendations"].append(
                f"Low citation rate ({citation_rate:.1%}). Evidence should include document/chunk references."
            )

    overall_score = 0.0
    if evaluation["is_valid"]:
        overall_score += 0.3
    if evidence_metrics["total_claims"] > 0:
        overall_score += 0.4 * evidence_metrics["evidence_coverage_rate"]
    if citation_metrics["total_evidence_fields"] > 0:
        overall_score += 0.3 * citation_metrics["citation_rate"]

    evaluation["overall_score"] = overall_score

    return evaluation
