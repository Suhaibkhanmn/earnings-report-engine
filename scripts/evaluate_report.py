import sys
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import requests
from backend.app.llm.validate import evaluate_report


def evaluate_report_api(ticker: str, quarter: str, prev_quarter: str | None = None, api_url: str = "http://localhost:8001"):
    """
    Call the evaluation endpoint and display results.
    """
    payload = {
        "ticker": ticker,
        "quarter": quarter,
    }
    if prev_quarter:
        payload["prev_quarter"] = prev_quarter

    response = requests.post(f"{api_url}/evaluation/report", json=payload)
    
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        print(response.text)
        return

    data = response.json()
    evaluation = data["evaluation"]

    print("\n" + "=" * 80)
    print("REPORT EVALUATION RESULTS")
    print("=" * 80)
    
    print(f"\nOverall Score: {evaluation['overall_score']:.1%}")
    print(f"Valid Structure: {'Yes' if evaluation['is_valid'] else 'No'}")
    
    if evaluation["structure_errors"]:
        print(f"\nStructure Errors ({len(evaluation['structure_errors'])}):")
        for error in evaluation["structure_errors"]:
            print(f"   - {error}")
    
    evidence = evaluation["evidence_coverage"]
    print(f"\nEvidence Coverage:")
    print(f"   Total Claims: {evidence['total_claims']}")
    print(f"   Claims with Evidence: {evidence['claims_with_evidence']}")
    print(f"   Claims without Evidence: {evidence['claims_without_evidence']}")
    print(f"   Coverage Rate: {evidence['evidence_coverage_rate']:.1%}")
    
    if evidence["claims_without_evidence"] > 0:
        print(f"\nClaims Missing Evidence:")
        for detail in evidence["details"][:5]:  # Show first 5
            print(f"   - [{detail['section']}] {detail['claim']}")
        if len(evidence["details"]) > 5:
            print(f"   ... and {len(evidence['details']) - 5} more")
    
    citations = evaluation["citation_quality"]
    print(f"\nCitation Quality:")
    print(f"   Total Evidence Fields: {citations['total_evidence_fields']}")
    print(f"   With Citations: {citations['evidence_with_citations']}")
    print(f"   Without Citations: {citations['evidence_without_citations']}")
    print(f"   Citation Rate: {citations['citation_rate']:.1%}")
    
    if evaluation["recommendations"]:
        print(f"\nRecommendations:")
        for rec in evaluation["recommendations"]:
            print(f"   - {rec}")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python scripts/evaluate_report.py <ticker> <quarter> [prev_quarter]")
        print("Example: python scripts/evaluate_report.py GOOG 2025_Q3 2025_Q2")
        sys.exit(1)
    
    ticker = sys.argv[1]
    quarter = sys.argv[2]
    prev_quarter = sys.argv[3] if len(sys.argv) > 3 else None
    
    evaluate_report_api(ticker, quarter, prev_quarter)
