"""
Bellcourt Health Administrators - Clinical Copilot Review Pipeline
Executes Agentic RAG Clinical Decision Support across live open cases.
Integrates policy resolution, criteria checklist, and determination drafting.
"""

import os
import sys
import json
import logging
import pandas as pd

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from src.clinical_copilot import ClinicalCopilot

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ClinicalReviewRunner")


def main():
    output_dir = os.path.join(current_dir, "output")
    triaged_cases_path = os.path.join(output_dir, "triaged_cases.json")

    if not os.path.exists(triaged_cases_path):
        logger.error(f"Could not find triaged cases at {triaged_cases_path}. Run run_intake_triage.py first.")
        return

    with open(triaged_cases_path, "r") as fp:
        triaged_cases = json.load(fp)

    logger.info(f"Loaded {len(triaged_cases)} triaged cases.")
    copilot = ClinicalCopilot()

    completed_evaluations = []
    logger.info("Executing Clinical Copilot evaluation across open queue...")

    for c in triaged_cases:
        cid = c["case_id"]
        status = c.get("triage_status")

        # Skip cases that were rejected for terminated coverage or missing member ID
        if status in ["PENDED_INCOMPLETE_INFO", "REJECTED_COVERAGE_TERMINATED"]:
            c["clinical_copilot_evaluation"] = {
                "recommendation": "NOT_EVALUATED_ADMIN_DEFICIENCY",
                "governing_source": "N/A - Administrative Deficiency at Intake",
                "criteria_checklist": [],
                "clinical_rationale": f"Case halted at intake triage due to {status}.",
                "required_role": "INTAKE_COORDINATOR"
            }
        else:
            eval_res = copilot.evaluate_case(c)
            c["clinical_copilot_evaluation"] = eval_res
            completed_evaluations.append(eval_res)

        logger.info(f"Case {cid}: Recommendation = {c['clinical_copilot_evaluation']['recommendation']} | Source = {c['clinical_copilot_evaluation'].get('governing_source')}")

    # Save updated triaged cases with copilot evaluations embedded
    with open(triaged_cases_path, "w") as fp:
        json.dump(triaged_cases, fp, indent=2)
    logger.info(f"Updated triaged cases with clinical evaluations saved to {triaged_cases_path}")

    # Save standalone clinical copilot recommendations
    rec_path = os.path.join(output_dir, "clinical_copilot_recommendations.json")
    with open(rec_path, "w") as fp:
        json.dump(completed_evaluations, fp, indent=2)

    # Print Summary Table
    df = pd.DataFrame(completed_evaluations)
    print("\n" + "="*80)
    print("BELLCOURT CLINICAL COPILOT - EVALUATION SUMMARY")
    print("="*80)
    print(f"Total Cases Evaluated: {len(df)}")
    print("\nRecommendation Breakdown:")
    print(df["recommendation"].value_counts().to_string())
    print("\nRequired Sign-Off Role Breakdown:")
    print(df["required_role"].value_counts().to_string())
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
