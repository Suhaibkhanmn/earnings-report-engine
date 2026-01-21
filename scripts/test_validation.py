import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.llm.validate import evaluate_report

# Sample report for testing
sample_report = {
    "ticker": "GOOG",
    "quarter": "2025_Q3",
    "prev_quarter": "2025_Q2",
    "summary": {
        "high_level": "Alphabet delivered strong Q3 results.",
        "tone": "positive"
    },
    "guidance": [
        {
            "claim": "CapEx guidance raised to $91-93B",
            "direction_vs_prev": "up",
            "evidence_current": "We now expect CapEx to be in the range of $91 billion to $93 billion (document_id: abc, chunk_id: xyz)",
            "evidence_prev": "previous estimate of $85 billion"
        }
    ],
    "growth_drivers": [
        {
            "claim": "AI driving revenue growth",
            "evidence": "AI is driving real business results (document_id: abc, chunk_id: xyz)"
        }
    ],
    "risks": [
        {
            "claim": "Depreciation headwind",
            "is_new": False,
            "evidence_current": "depreciation increased significantly (document_id: abc, chunk_id: xyz)",
            "evidence_first_mention": "mentioned in previous calls"
        }
    ],
    "margin_dynamics": [
        {
            "claim": "Operating margin improved",
            "evidence": "operating margin was 33.9% excluding EC fine (document_id: abc, chunk_id: xyz)"
        }
    ],
    "qa_pressure_points": [
        {
            "theme": "AI monetization",
            "analyst_name": "John Doe",
            "evidence_question": "How is AI monetizing? (document_id: abc, chunk_id: xyz)",
            "evidence_answer": "We see monetization at approximately the same rate (document_id: abc, chunk_id: xyz)"
        }
    ]
}

if __name__ == "__main__":
    print("Testing report validation...")
    evaluation = evaluate_report(sample_report)
    
    print(f"\nValid: {evaluation['is_valid']}")
    print(f"Overall Score: {evaluation['overall_score']:.1%}")
    print(f"\nEvidence Coverage: {evaluation['evidence_coverage']['evidence_coverage_rate']:.1%}")
    print(f"Citation Rate: {evaluation['citation_quality']['citation_rate']:.1%}")
    
    if evaluation['recommendations']:
        print("\nRecommendations:")
        for rec in evaluation['recommendations']:
            print(f"  - {rec}")
