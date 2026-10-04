"""
Bellcourt Health Administrators - Clinical Policy & Governance Authority Resolver
Component: Option B (Agentic RAG Clinical Copilot - Policy Resolution Engine)
Author: Forward Deployed Engineer (FDE)

Enforces Bellcourt GOV-01 Hierarchy of Authority:
1. Federal & State Regulations / CMS-0057-F
2. Riverbend Delegation Addendum & Employer Summary Plan Descriptions (SPDs)
3. Committee-Approved Medical Policies (Versioned by Date of Service)
4. Rejection of Conflicting Operational Memos (e.g. UM-MEMO-2025-19)
"""

import os
import re
from typing import Dict, Any, List, Optional, Tuple


class PolicyResolver:
    """
    Deterministic Legal & Clinical Authority Resolver.
    Resolves the exact governing policy version and plan document provisions,
    eliminating OUTDATED_POLICY_VERSION, MEMO_CONFLICT, and CLIENT_RULE_MISSED errors.
    """

    # Service code to Policy mapping and version effective dates
    SERVICE_POLICY_MAP = {
        'BHA-IMG-0721': {
            'policy_id': 'MP-101',
            'name': 'Advanced Imaging: MRI of the Lumbar Spine',
            'versions': [
                {'version': 'v1', 'effective_start': '2024-01-01', 'effective_end': '2025-12-31', 'criteria_threshold_weeks': 6},
                {'version': 'v2', 'effective_start': '2026-01-01', 'effective_end': '9999-12-31', 'criteria_threshold_weeks': 4}
            ]
        },
        'BHA-SURG-4310': {
            'policy_id': 'MP-102',
            'name': 'Bariatric (Weight-Loss) Surgery',
            'versions': [
                {'version': 'v1', 'effective_start': '2024-01-01', 'effective_end': '2025-06-30', 'requires_6mo_program': True},
                {'version': 'v2', 'effective_start': '2025-07-01', 'effective_end': '9999-12-31', 'requires_6mo_program': False}
            ]
        },
        'BHA-DME-2103': {
            'policy_id': 'MP-103',
            'name': 'Continuous Glucose Monitors (CGM)',
            'versions': [
                {'version': 'v1', 'effective_start': '2024-01-01', 'effective_end': '2025-12-31', 'expanded_insulin': False},
                {'version': 'v2', 'effective_start': '2026-01-01', 'effective_end': '9999-12-31', 'expanded_insulin': True}
            ]
        },
        'BHA-DX-9581': {
            'policy_id': 'MP-104',
            'name': 'Attended In-Laboratory Polysomnography (Sleep Study)',
            'versions': [{'version': 'v1', 'effective_start': '2024-01-01', 'effective_end': '9999-12-31'}]
        },
        'BHA-SURG-2988': {
            'policy_id': 'MP-105',
            'name': 'Arthroscopic Knee Surgery',
            'versions': [{'version': 'v1', 'effective_start': '2024-01-01', 'effective_end': '9999-12-31'}]
        },
        'BHA-SURG-2744': {
            'policy_id': 'MP-106',
            'name': 'Total Knee Arthroplasty (TKA)',
            'versions': [
                {'version': 'v1', 'effective_start': '2024-01-01', 'effective_end': '2025-12-31'},
                {'version': 'v2', 'effective_start': '2026-01-01', 'effective_end': '9999-12-31', 'requires_optimization_note': True}
            ]
        },
        'BHA-LAB-8162': {
            'policy_id': 'MP-107',
            'name': 'Genetic Testing for Hereditary Breast and Ovarian Cancer (BRCA1/2)',
            'versions': [{'version': 'v1', 'effective_start': '2024-01-01', 'effective_end': '9999-12-31'}]
        },
        'BHA-SURG-1582': {
            'policy_id': 'MP-108',
            'name': 'Blepharoplasty (Upper Eyelid Surgery)',
            'versions': [{'version': 'v1', 'effective_start': '2024-01-01', 'effective_end': '9999-12-31'}]
        },
        'BHA-SURG-3052': {
            'policy_id': 'MP-109',
            'name': 'Septoplasty',
            'versions': [{'version': 'v1', 'effective_start': '2024-01-01', 'effective_end': '9999-12-31'}]
        },
        'BHA-SURG-6350': {
            'policy_id': 'MP-110',
            'name': 'Spinal Cord Stimulator (SCS) Trial',
            'versions': [
                {'version': 'v1', 'effective_start': '2024-01-01', 'effective_end': '2025-09-30'},
                {'version': 'v2', 'effective_start': '2025-10-01', 'effective_end': '9999-12-31'}
            ]
        },
        'BHA-VASC-3647': {
            'policy_id': 'MP-111',
            'name': 'Endovenous Ablation of Varicose Veins',
            'versions': [{'version': 'v1', 'effective_start': '2024-01-01', 'effective_end': '9999-12-31'}]
        },
        'BHA-THER-1830': {
            'policy_id': 'MP-112',
            'name': 'Hyperbaric Oxygen Therapy (HBOT)',
            'versions': [{'version': 'v1', 'effective_start': '2024-01-01', 'effective_end': '9999-12-31'}]
        },
        'BHA-RAD-5205': {
            'policy_id': 'MP-113',
            'name': 'Proton Beam Radiation Therapy',
            'versions': [{'version': 'v1', 'effective_start': '2024-01-01', 'effective_end': '9999-12-31'}]
        },
        'BHA-REH-9711': {
            'policy_id': 'MP-114',
            'name': 'Outpatient Physical Therapy Beyond the Initial 12 Visits',
            'versions': [{'version': 'v1', 'effective_start': '2024-01-01', 'effective_end': '9999-12-31'}]
        },
        'BHA-IMG-7519': {
            'policy_id': 'MP-115',
            'name': 'Coronary CT Angiography (CCTA)',
            'versions': [{'version': 'v1', 'effective_start': '2024-01-01', 'effective_end': '9999-12-31'}]
        },
        'BHA-HH-0550': {
            'policy_id': 'MP-116',
            'name': 'Home Health Services',
            'versions': [{'version': 'v1', 'effective_start': '2024-01-01', 'effective_end': '9999-12-31'}]
        },
        'BHA-DME-0601': {
            'policy_id': 'MP-118',
            'name': 'CPAP Continued Coverage (After the Initial 90 Days)',
            'versions': [{'version': 'v1', 'effective_start': '2024-01-01', 'effective_end': '9999-12-31'}]
        }
    }

    # Employer SPD Physical Therapy Annual Visit Limits (SPD Section 4.2)
    PT_VISIT_LIMITS = {
        'HARLAN': 30,
        'BRIGHT': 20,
        'KESTREL': 25,
        'JUNIPER': 24,
        'OSTR': 30,
        'SORREL': 20
    }

    # Designated Centers of Excellence for Brightwater Unified School District (SPD-BRIGHT Section 5.3)
    BRIGHT_BARIATRIC_COE = [
        "front range bariatric institute",
        "summit metabolic surgery center"
    ]

    @classmethod
    def resolve_governing_authority(
        cls,
        client_id: str,
        service_code: str,
        date_of_service: str,
        patient_age: Optional[int] = None,
        facility_name: Optional[str] = None,
        member_state: Optional[str] = None,
        clinical_notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes hierarchical authority resolution.
        Returns:
        {
          "governing_source": str (e.g. "MP-101 v2 Section 3 (Coverage Criteria)"),
          "policy_id": str,
          "version": str,
          "is_excluded_by_plan": bool,
          "exclusion_reason": Optional[str],
          "plan_override": Optional[str],
          "regulatory_requirements": list,
          "active_criteria_summary": str
        }
        """
        client_upper = (client_id or "").upper()
        reg_flags = []
        notes = clinical_notes or ""

        # Regulatory & Licensing requirements
        if client_upper == "RB-MA":
            if member_state == "AZ" or (date_of_service >= "2026-07-01" and member_state == "AZ"):
                reg_flags.append("ARIZONA_LICENSED_MD_REQUIRED: Denial must be personally reviewed and signed by an Arizona-licensed medical director (RIVERBEND-ADDENDUM §4).")
            if member_state == "TX":
                reg_flags.append("TEXAS_AI_DISCLOSURE: Notice must disclose the use of automated/AI-assisted tools (RIVERBEND-ADDENDUM §4).")

        # ---------------------------------------------------------
        # LEVEL 1: Riverbend Medicare Advantage Precedence
        # ---------------------------------------------------------
        if client_upper == "RB-MA":
            # Continuous Glucose Monitors (CGM) under Medicare rules
            if service_code == "BHA-DME-2103":
                return {
                    "governing_source": "RIVERBEND-ADDENDUM Section 2.1 (CGM: Medicare coverage criteria apply to MA members)",
                    "policy_id": "RIVERBEND-ADDENDUM",
                    "version": "2026",
                    "is_excluded_by_plan": False,
                    "exclusion_reason": None,
                    "plan_override": "Medicare Coverage Criteria (NCD/LCD) take precedence over Bellcourt policies.",
                    "regulatory_requirements": reg_flags,
                    "active_criteria_summary": "Diabetes mellitus AND either (a) insulin treatment of any type or frequency, or (b) documented problematic hypoglycemia. Applies to all dates of service."
                }

        # ---------------------------------------------------------
        # LEVEL 2: Employer Plan Document (SPD) Exclusions & Riders
        # ---------------------------------------------------------
        # 1. Physical Therapy Annual Visit Limits (SPD Section 4.2)
        if service_code == "BHA-REH-9711" and client_upper in cls.PT_VISIT_LIMITS:
            limit = cls.PT_VISIT_LIMITS[client_upper]
            m_used = re.search(r'([0-9]+)\s+PT\s+visits?\s+used', notes, re.I)
            m_req = re.search(r'requesting\s+([0-9]+)\s+additional', notes, re.I)
            used_visits = int(m_used.group(1)) if m_used else None
            req_visits = int(m_req.group(1)) if m_req else None

            # Check if this request exceeds the annual benefit limit
            # Exception: if progress note shows plateau/maintenance, medical necessity governs (MP-114)
            is_maintenance = bool(re.search(r'plateaued|maintenance', notes, re.I))

            if used_visits is not None and req_visits is not None and not is_maintenance:
                if (used_visits + req_visits > limit) or (used_visits >= limit):
                    return {
                        "governing_source": f"SPD-{client_upper} Section 4.2 (Schedule of Benefits: outpatient rehabilitation limited to {limit} visits per plan year)",
                        "policy_id": f"SPD-{client_upper}",
                        "version": "2026",
                        "is_excluded_by_plan": True,
                        "exclusion_reason": f"Physical therapy request ({used_visits} visits used + {req_visits} requested = {used_visits + req_visits}) exceeds the annual benefit limit of {limit} visits under SPD-{client_upper} Section 4.2.",
                        "plan_override": "Annual visit benefit cap under employer SPD.",
                        "regulatory_requirements": reg_flags,
                        "active_criteria_summary": f"Outpatient rehabilitation benefit cap: maximum {limit} visits per plan year."
                    }

        # 2. Harlan Freight Lines (SPD-HARLAN)
        if client_upper == "HARLAN":
            if service_code == "BHA-SURG-4310":
                return {
                    "governing_source": "SPD-HARLAN Section 6.4 (Bariatric surgery excluded)",
                    "policy_id": "SPD-HARLAN",
                    "version": "2026",
                    "is_excluded_by_plan": True,
                    "exclusion_reason": "Bariatric surgery is a non-covered benefit under the Harlan Freight Lines Employee Health Benefit Plan.",
                    "plan_override": "Plan exclusion supersedes clinical medical policy.",
                    "regulatory_requirements": reg_flags,
                    "active_criteria_summary": "Excluded benefit. No medical necessity review performed."
                }

        # 3. Brightwater Unified School District (SPD-BRIGHT)
        elif client_upper == "BRIGHT":
            # Bariatric surgery COE restriction
            if service_code == "BHA-SURG-4310":
                if facility_name:
                    facility_clean = facility_name.lower().strip()
                    is_coe = any(coe in facility_clean for coe in cls.BRIGHT_BARIATRIC_COE)
                    if not is_coe:
                        return {
                            "governing_source": "SPD-BRIGHT Section 5.3 (Bariatric surgery covered only at designated Center of Excellence)",
                            "policy_id": "SPD-BRIGHT",
                            "version": "2026",
                            "is_excluded_by_plan": True,
                            "exclusion_reason": f"Bariatric surgery planned at '{facility_name}', which is not a designated Center of Excellence (COE) under SPD-BRIGHT Section 5.3.",
                            "plan_override": "COE network restriction under employer SPD.",
                            "regulatory_requirements": reg_flags,
                            "active_criteria_summary": "Covered only at Front Range Bariatric Institute or Summit Metabolic Surgery Center."
                        }

            # Proton Beam Radiation Therapy age restriction
            if service_code == "BHA-RAD-5205":
                if patient_age is not None and patient_age >= 21:
                    return {
                        "governing_source": "SPD-BRIGHT Section 6.7 (Proton beam therapy excluded for members age 21 and older)",
                        "policy_id": "SPD-BRIGHT",
                        "version": "2026",
                        "is_excluded_by_plan": True,
                        "exclusion_reason": f"Member is {patient_age} years old. Proton beam radiation therapy is excluded under SPD-BRIGHT Section 6.7 for members age 21 and older.",
                        "plan_override": "Age limitation under employer SPD.",
                        "regulatory_requirements": reg_flags,
                        "active_criteria_summary": "Excluded except for pediatric members under age 21."
                    }

        # 4. Kestrel Precision Manufacturing (SPD-KESTREL Amendment No. 3)
        elif client_upper == "KESTREL":
            if service_code == "BHA-SURG-4310":
                if date_of_service >= "2026-01-01":
                    # Covered under Amendment 3!
                    pass

        # 5. Sorrel Hospitality Group (SPD-SORREL)
        elif client_upper == "SORREL":
            if service_code == "BHA-SURG-1582":
                pass

        # ---------------------------------------------------------
        # LEVEL 3: Active Medical Policy Selection by Date of Service
        # ---------------------------------------------------------
        svc_entry = cls.SERVICE_POLICY_MAP.get(service_code)
        if not svc_entry:
            return {
                "governing_source": "UNKNOWN_SERVICE_CODE",
                "policy_id": "UNKNOWN",
                "version": "UNKNOWN",
                "is_excluded_by_plan": False,
                "exclusion_reason": None,
                "plan_override": None,
                "regulatory_requirements": reg_flags,
                "active_criteria_summary": "Service code not found in Bellcourt medical policy catalog."
            }

        policy_id = svc_entry['policy_id']
        selected_version = "v1"
        for ver in svc_entry['versions']:
            start = ver['effective_start']
            end = ver['effective_end']
            if start <= date_of_service <= end:
                selected_version = ver['version']
                break

        governing_source = f"{policy_id} {selected_version} Section 3 (Coverage Criteria)"

        # Special Governance Rule: UM-MEMO-2025-19 rejection
        plan_override_note = None
        if service_code == "BHA-IMG-0721" and selected_version == "v2":
            plan_override_note = "Under GOV-01 Section 1, MP-101 v2 (4 weeks conservative therapy) governs. UM-MEMO-2025-19 (6 weeks) is an unapproved staff memo and cannot override committee policy."

        return {
            "governing_source": governing_source,
            "policy_id": policy_id,
            "version": selected_version,
            "is_excluded_by_plan": False,
            "exclusion_reason": None,
            "plan_override": plan_override_note,
            "regulatory_requirements": reg_flags,
            "active_criteria_summary": f"Governed by committee-approved policy {policy_id} {selected_version} effective on date of service {date_of_service}."
        }
