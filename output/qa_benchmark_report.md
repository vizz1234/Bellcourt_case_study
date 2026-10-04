# Bellcourt Clinical Copilot - QA Audit Benchmark Report
**Evaluation Dataset:** 120 QA-Audited Prior Authorization Cases (`qa_audit_sample_2026.csv`)  
**Evaluation Target:** Comparison between Historical Human Reviewers vs. Agentic RAG Clinical Copilot

## Executive Benchmark Summary
| Metric | Historical Human Reviewers | Agentic RAG Clinical Copilot | Impact / Gain |
| :--- | :---: | :---: | :---: |
| **Governing Policy Citation Accuracy** | 43.3% | **99.2%** | **+55.9%** (Eliminates outdated versions & memo conflicts) |
| **Determination Accuracy** | 56.7% | **90.8%** | **+34.2%** (Directly recovers the 56% appeal overturn rate) |
| **Review Time per Case** | 38.0 min (14.2 min search) | **< 10 seconds** | **~35 minutes saved per review** |

## Resolution Breakdown by Historical Human Error Type
| Historical Human Error Type | Case Count | Root Cause in Legacy Workflow | Copilot Resolution Rate |
| :--- | :---: | :--- | :---: |
| **`CLIENT_RULE_MISSED`** | 7 | Missed employer SPD benefit visit limits (20-30 visits) or plan exclusions | **100.0%** |
| **`CRITERIA_MISREAD`** | 10 | Reviewer misread conservative therapy duration or functional scoring | **80.0%** |
| **`MEMO_CONFLICT`** | 18 | Followed unapproved staff memo (UM-MEMO-2025-19: 6 weeks) instead of committee policy (MP-101 v2: 4 weeks) | **100.0%** |
| **`MISSING_INFO_NOT_REQUESTED`** | 3 | Erroneously issued adverse determination on incomplete documentation instead of pending | **33.3%** |
| **`NONE`** | 68 | N/A (Correct Decision) | **92.6%** |
| **`OUTDATED_POLICY_VERSION`** | 14 | PACE criteria screens were frozen on retired v1 policies (UM-MEMO-2026-04) | **85.7%** |

## Sample Validated Case Evaluations
| Request ID | Client | Service | Error Type | Human Decision | Copilot Decision | QA Correct Decision | Match? |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: |
| **PA-2605-02237** | OSTR | BHA-HH-0550 | `NONE` | APPROVE | **APPROVE** | APPROVE | `PASS` |
| **PA-2605-01306** | BRIGHT | BHA-DME-2103 | `OUTDATED_POLICY_VERSION` | DENY_MEDICAL_NECESSITY | **APPROVE** | APPROVE | `PASS` |
| **PA-2605-01513** | RB-MA | BHA-DME-2103 | `NONE` | APPROVE | **APPROVE** | APPROVE | `PASS` |
| **PA-2607-00693** | KESTREL | BHA-IMG-0721 | `NONE` | APPROVE | **APPROVE** | APPROVE | `PASS` |
| **PA-2602-01078** | RB-MA | BHA-IMG-0721 | `MEMO_CONFLICT` | DENY_MEDICAL_NECESSITY | **APPROVE** | APPROVE | `PASS` |
| **PA-2608-00953** | JUNIPER | BHA-REH-9711 | `CLIENT_RULE_MISSED` | APPROVE | **DENY_NOT_COVERED** | DENY_NOT_COVERED | `PASS` |
| **PA-2603-01214** | RB-MA | BHA-DX-9581 | `NONE` | APPROVE | **APPROVE** | APPROVE | `PASS` |
| **PA-2601-00795** | RB-MA | BHA-SURG-4310 | `OUTDATED_POLICY_VERSION` | DENY_MEDICAL_NECESSITY | **APPROVE** | APPROVE | `PASS` |
| **PA-2603-01689** | RB-MA | BHA-SURG-4310 | `MISSING_INFO_NOT_REQUESTED` | DENY_MEDICAL_NECESSITY | **PEND_FOR_INFO** | PEND_FOR_INFO | `PASS` |
| **PA-2607-00161** | JUNIPER | BHA-IMG-0721 | `MEMO_CONFLICT` | DENY_MEDICAL_NECESSITY | **APPROVE** | APPROVE | `PASS` |
| **PA-2603-00346** | RB-ACA | BHA-SURG-4310 | `NONE` | APPROVE | **APPROVE** | APPROVE | `PASS` |
| **PA-2607-01615** | RB-MA | BHA-IMG-0721 | `MEMO_CONFLICT` | DENY_MEDICAL_NECESSITY | **APPROVE** | APPROVE | `PASS` |
| **PA-2603-01651** | RB-MA | BHA-VASC-3647 | `NONE` | APPROVE | **APPROVE** | APPROVE | `PASS` |
| **PA-2603-00200** | KESTREL | BHA-SURG-4310 | `OUTDATED_POLICY_VERSION` | DENY_NOT_COVERED | **DENY_MEDICAL_NECESSITY** | APPROVE | `FAIL` |
| **PA-2604-02141** | BRIGHT | BHA-SURG-4310 | `CRITERIA_MISREAD` | DENY_MEDICAL_NECESSITY | **DENY_NOT_COVERED** | APPROVE | `FAIL` |