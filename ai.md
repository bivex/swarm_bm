# 🤖 Comprehensive ISO/IEC International Standards Roadmap for Artificial Intelligence (AI) & ML Engineering

> **Official Technical Committee**: `ISO/IEC JTC 1/SC 42 (Artificial Intelligence)` & `ISO/IEC JTC 1/SC 7 (Software & Systems Engineering)`  
> **Reference Framework**: Oviedo et al., *ISO/IEC quality standards for AI engineering*, Elsevier Computer Science Review 54 (2024) 100681  
> **Total Production AI Auditors in Suite**: **10 Automated BM25 + AST Audit Scripts** in [`scratch/auditors/iso/ai/`](file:///Volumes/External/Code/swarm_bm/scratch/auditors/iso/ai/)  
> **Primary Classification**: **ICS 35.020, 03.120.20, 35.080**

---

## 🏛️ 1. AI Governance & Management Systems (AIMS)

| ISO Standard | Title & Edition | Key Governance & Audit Focus | Auditor Script Path |
|---|---|---|---|
| 🤖 **ISO/IEC 42001:2023** | *Artificial Intelligence — Management System (AIMS)* | **Flagship World Standard** for establishing, implementing, and continually improving AI management systems (AIMS). | [`scratch/auditors/iso/ai/iso_42001_ai_audit.py`](file:///Volumes/External/Code/swarm_bm/scratch/auditors/iso/ai/iso_42001_ai_audit.py) |
| 🔍 **BS ISO/IEC 42006:2025** | *Requirements for bodies providing audit and certification of AIMS* | Accreditation requirements for certification bodies, Stage 1/2 audits, and Annex A audit time calculations. | [`scratch/auditors/iso/ai/iso_42006_aims_certification_audit.py`](file:///Volumes/External/Code/swarm_bm/scratch/auditors/iso/ai/iso_42006_aims_certification_audit.py) |
| 💼 **ISO/IEC 38507:2022** | *Governance implications of the use of AI by organizations* | Board of Directors oversight, human accountability for AI decisions, AI Data Use policies, and Risk Appetite. | [`scratch/auditors/iso/ai/iso_38507_ai_governance_audit.py`](file:///Volumes/External/Code/swarm_bm/scratch/auditors/iso/ai/iso_38507_ai_governance_audit.py) |
| ⚖️ **ISO/IEC 42005:2025** | *AI system impact assessment (AIIA)* | Structured methodology for assessing societal, ethical, privacy, and safety impacts of AI deployment. | Audited via ISO 42001 Suite |

---

## 🧠 2. Machine Learning, Concepts & Life Cycle Engineering

| ISO Standard | Title & Edition | Key Architecture & Life Cycle Focus | Auditor Script Path |
|---|---|---|---|
| ⚙️ **ISO/IEC 23053:2022** | *Framework for AI Systems Using Machine Learning (ML)* | Architectural framework for ML tasks (Regression, Classification, Clustering), dataset splits, and loss functions. | [`scratch/auditors/iso/ai/iso_23053_ml_framework_audit.py`](file:///Volumes/External/Code/swarm_bm/scratch/auditors/iso/ai/iso_23053_ml_framework_audit.py) |
| 📖 **ISO/IEC 22989:2022** | *AI Concepts and Terminology* | Foundational terminology, 4 dataset partitions (Training, Validation, Test, Prod), and AI Stakeholder roles. | [`scratch/auditors/iso/ai/iso_22989_ai_concepts_audit.py`](file:///Volumes/External/Code/swarm_bm/scratch/auditors/iso/ai/iso_22989_ai_concepts_audit.py) |
| 🔄 **ISO/IEC 5338:2023** | *AI System Life Cycle Processes* | Integration with ISO 12207/15288: Knowledge Acquisition, AI Data Engineering, and Continuous Validation. | [`scratch/auditors/iso/ai/iso_5338_ai_lifecycle_audit.py`](file:///Volumes/External/Code/swarm_bm/scratch/auditors/iso/ai/iso_5338_ai_lifecycle_audit.py) |
| 🏅 **ISO/IEC 25059:2023** | *SQuaRE — Quality model for AI systems* | AI System Quality Model: User Controllability, Neural Network Robustness, Intervenability, and Explainability. | [`scratch/auditors/iso/ai/iso_25059_ai_quality_model_audit.py`](file:///Volumes/External/Code/swarm_bm/scratch/auditors/iso/ai/iso_25059_ai_quality_model_audit.py) |

---

## 🛡️ 3. AI Risk Management, Safety & Trustworthiness

| ISO Standard | Title & Edition | Safety & Risk Focus | Auditor Script Path |
|---|---|---|---|
| 📊 **ISO/IEC 23894:2023** | *Guidance on risk management for AI* | AI risk identification, RAG hallucination grounding, prompt injection defense, bias check, and HITL guardrails. | [`scratch/auditors/iso/ai/iso_23894_ai_risk_audit.py`](file:///Volumes/External/Code/swarm_bm/scratch/auditors/iso/ai/iso_23894_ai_risk_audit.py) |
| 🔬 **ISO/IEC 24029-1/2:2023** | *Assessment of neural network robustness* | Formal mathematical verification and statistical methods for assessing deep neural network robustness. | Audited via ISO 25059 Suite |
| 👁️ **ISO/IEC 6254:2024** | *Explainability & Interpretability of ML models* | Feature attribution methods (SHAP, LIME, Attention Maps) and explanation needs taxonomy. | Audited via ISO 25059 Suite |
| ⚖️ **ISO/IEC 24027:2021** | *Bias in AI systems and AI-aided decision making* | Equalized odds, demographic parity, and confusion matrix measurement of algorithmic bias. | Audited via ISO 5259 / ISO 23894 |

---

## 🗃️ 4. ML & AI Training Data Quality (Complete Official ISO/IEC 5259 Series)

| ISO Standard | Title & Edition | Training Data & Dataset Focus | Auditor Script Path |
|---|---|---|---|
| 📑 **ISO/IEC 5259-1:2024** | *Part 1: Overview, terminology, and examples* | Data Roles (Originator, Holder, User), Cryptographic Data Provenance, and 6 DLC life cycle stages. | [`scratch/auditors/iso/ai/iso_5259_data_quality_audit.py`](file:///Volumes/External/Code/swarm_bm/scratch/auditors/iso/ai/iso_5259_data_quality_audit.py) |
| 📊 **ISO/IEC 5259-2:2024** | *Part 2: Data quality measures* | 4 Annex C Perspectives (Maintainability, Validity, Reliability, Fidelity), 15 QM metrics, and Anti-Overfitting. | [`scratch/auditors/iso/ai/iso_5259_2_data_quality_measures_audit.py`](file:///Volumes/External/Code/swarm_bm/scratch/auditors/iso/ai/iso_5259_2_data_quality_measures_audit.py) |
| 🏛️ **ISO/IEC 5259-3:2024** | *Part 3: Data quality management requirements* | DQMLC 8 stages, Quality Gates, Change Request Impact Analysis, and Supply Chain DIA Contracts. | [`scratch/auditors/iso/ai/iso_5259_3_management_audit.py`](file:///Volumes/External/Code/swarm_bm/scratch/auditors/iso/ai/iso_5259_3_management_audit.py) |
| ⚙️ **ISO/IEC 5259-4:2024** | *Part 4: Data quality process framework (DQPF)* | Imputation, Scaling, Multi-Modal Augmentation, De-identification (ISO 27559), Categorical Encoding, and Labelling CV. | [`scratch/auditors/iso/ai/iso_5259_4_process_framework_audit.py`](file:///Volumes/External/Code/swarm_bm/scratch/auditors/iso/ai/iso_5259_4_process_framework_audit.py) |
| 🛡️ **ISO/IEC 5259-5:2025** | *Part 5: Data quality governance framework* | Governance Roles (CDO, Data Owner, Steward), Data Quality Committee setup, and Risk Treatment (ISO 23894). | [`scratch/auditors/iso/ai/iso_5259_5_governance_audit.py`](file:///Volumes/External/Code/swarm_bm/scratch/auditors/iso/ai/iso_5259_5_governance_audit.py) |

---

## ⚡ CLI Audit Execution Commands

Run individual AI auditors or the complete 10-auditor ISO AI Engineering suite against any repository (e.g. `/tmp/pipecat_ai_audit`):

```bash
# 1. Complete ISO/IEC 5259 Data Quality Series (Parts 1 - 5)
PYTHONPATH=.:bm25_server_FS_for-AI-asking python3 scratch/auditors/iso/ai/iso_5259_data_quality_audit.py /tmp/pipecat_ai_audit "PipecatAI"
PYTHONPATH=.:bm25_server_FS_for-AI-asking python3 scratch/auditors/iso/ai/iso_5259_2_data_quality_measures_audit.py /tmp/pipecat_ai_audit "PipecatAI"
PYTHONPATH=.:bm25_server_FS_for-AI-asking python3 scratch/auditors/iso/ai/iso_5259_3_management_audit.py /tmp/pipecat_ai_audit "PipecatAI"
PYTHONPATH=.:bm25_server_FS_for-AI-asking python3 scratch/auditors/iso/ai/iso_5259_4_process_framework_audit.py /tmp/pipecat_ai_audit "PipecatAI"
PYTHONPATH=.:bm25_server_FS_for-AI-asking python3 scratch/auditors/iso/ai/iso_5259_5_governance_audit.py /tmp/pipecat_ai_audit "PipecatAI"

# 2. AI Management & Governance Standards (ISO 42001, ISO 42006, ISO 38507, ISO 23894)
PYTHONPATH=.:bm25_server_FS_for-AI-asking python3 scratch/auditors/iso/ai/iso_42001_ai_audit.py /tmp/pipecat_ai_audit "PipecatAI"
PYTHONPATH=.:bm25_server_FS_for-AI-asking python3 scratch/auditors/iso/ai/iso_42006_aims_certification_audit.py /tmp/pipecat_ai_audit "PipecatAI"
PYTHONPATH=.:bm25_server_FS_for-AI-asking python3 scratch/auditors/iso/ai/iso_38507_ai_governance_audit.py /tmp/pipecat_ai_audit "PipecatAI"
PYTHONPATH=.:bm25_server_FS_for-AI-asking python3 scratch/auditors/iso/ai/iso_23894_ai_risk_audit.py /tmp/pipecat_ai_audit "PipecatAI"

# 3. AI Architecture, Concepts & Quality Standards (ISO 23053, ISO 22989, ISO 5338, ISO 25059)
PYTHONPATH=.:bm25_server_FS_for-AI-asking python3 scratch/auditors/iso/ai/iso_23053_ml_framework_audit.py /tmp/pipecat_ai_audit "PipecatAI"
PYTHONPATH=.:bm25_server_FS_for-AI-asking python3 scratch/auditors/iso/ai/iso_22989_ai_concepts_audit.py /tmp/pipecat_ai_audit "PipecatAI"
PYTHONPATH=.:bm25_server_FS_for-AI-asking python3 scratch/auditors/iso/ai/iso_5338_ai_lifecycle_audit.py /tmp/pipecat_ai_audit "PipecatAI"
PYTHONPATH=.:bm25_server_FS_for-AI-asking python3 scratch/auditors/iso/ai/iso_25059_ai_quality_model_audit.py /tmp/pipecat_ai_audit "PipecatAI"
```

---
*ISO/IEC International Standards Roadmap for AI Engineering · Updated August 2026*
