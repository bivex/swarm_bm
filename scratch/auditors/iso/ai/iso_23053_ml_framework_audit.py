#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║  ISO/IEC 23053:2022 — Framework for AI Systems Using ML — Auditor            ║
║                                                                               ║
║  Based on normative structure of ISO/IEC 23053:2022:                         ║
║  Clause 6: Machine learning system                                            ║
║    6.2 Task (regression/classification/clustering/anomaly/dim-reduction)      ║
║    6.3 Model (training data, parameters, retraining, drift)                   ║
║    6.4 Data (training/validation/test/production split — MUST be disjoint)    ║
║    6.5 Tools (data prep, ML algorithms, optimisation, evaluation metrics)     ║
║  Clause 7: Machine learning approaches                                        ║
║    7.2 Supervised / 7.3 Unsupervised / 7.4–7.5 Semi/Self-supervised          ║
║    7.6 Reinforcement / 7.7 Transfer learning                                  ║
║  Clause 8: Machine learning pipeline                                          ║
║    8.2 Data acquisition / 8.3 Data preparation / 8.4 Modelling               ║
║    8.5 Verification and validation / 8.6 Model deployment / 8.7 Operation     ║
║  Cross-cutting: risk management, security & privacy, accountability,          ║
║    transparency, safety, resilience, robustness, fairness (Fig 12)            ║
╚═══════════════════════════════════════════════════════════════════════════════╝

Usage:
    python3 scratch/auditors/iso/ai/iso_23053_ml_framework_audit.py /path/to/project [ProjectName]
"""
from __future__ import annotations

import re
import sys
import time
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

root_dir = next(p for p in Path(__file__).resolve().parents if (p / "bm25_server_FS_for-AI-asking").exists())
sys.path.insert(0, str(root_dir))
sys.path.insert(0, str(root_dir / "bm25_server_FS_for-AI-asking"))

from swarm_mcp.infrastructure.index_store_adapter import IndexStoreAdapter


@dataclass
class ML23053Check:
    """A normative element from ISO/IEC 23053:2022 ML Framework."""
    clause_id: str      # e.g. "6.2.3", "8.3"
    clause_ref: str     # Short descriptive title
    normative_text: str # Key concept from normative clause
    category: str       # TASK / MODEL / DATA / TOOLS / APPROACH / PIPELINE / CROSS_CUTTING
    weight: int         # 1–4
    search_terms: list[str]
    evidence_files: list[str] = field(default_factory=list)
    found: bool = False
    confidence: str = "NONE"


ML_CHECKS: list[ML23053Check] = [

    # ── Clause 6.2: Task ─────────────────────────────────────────────────────
    ML23053Check(
        clause_id="6.2.1",
        clause_ref="ML Task definition",
        normative_text=(
            "An ML task setup involves defining the problem, the data format and the features. "
            "One or more ML tasks can be defined for an ML application. "
            "Instead of solving a problem using a specific function implemented in software code, "
            "the defined problem is solved by applying a trained ML model to production data."
        ),
        category="TASK", weight=3,
        search_terms=["task", "problem_definition", "input_format", "output_format",
                      "features", "prediction", "inference"],
    ),
    ML23053Check(
        clause_id="6.2.2",
        clause_ref="Regression task",
        normative_text=(
            "Regression tasks comprise predicting a continuous variable by learning a function "
            "that best fits a set of training data. Use cases: predicting numerical values "
            "of a real-world process based on previous measurements."
        ),
        category="TASK", weight=2,
        search_terms=["regression", "predict", "continuous", "linear_regression", "mse", "mae",
                      "mean_absolute_error", "mean_squared_error"],
    ),
    ML23053Check(
        clause_id="6.2.3",
        clause_ref="Classification task",
        normative_text=(
            "Classification tasks comprise predicting the assignment of an instance of input data "
            "to a defined category or class. Can be binary, multi-class or multilabel."
        ),
        category="TASK", weight=2,
        search_terms=["classification", "classifier", "class", "label", "binary",
                      "multi_class", "softmax", "sigmoid", "cross_entropy"],
    ),
    ML23053Check(
        clause_id="6.2.4",
        clause_ref="Clustering task",
        normative_text=(
            "Clustering tasks comprise grouping input data instances. Classes are not predefined "
            "but determined as part of the clustering process. Can be used for outlier detection."
        ),
        category="TASK", weight=1,
        search_terms=["clustering", "kmeans", "k_means", "cluster", "unsupervised",
                      "centroid", "DBSCAN"],
    ),
    ML23053Check(
        clause_id="6.2.5",
        clause_ref="Anomaly detection task",
        normative_text=(
            "Anomaly detection comprises identifying input data instances that do not conform "
            "to an expected pattern. Useful for detecting fraud or unusual activities. "
            "The ML model predicts whether an input data instance is typical for a given distribution."
        ),
        category="TASK", weight=2,
        search_terms=["anomaly", "outlier", "anomaly_detection", "fraud_detection",
                      "out_of_distribution", "novelty"],
    ),
    ML23053Check(
        clause_id="6.2.6",
        clause_ref="Dimensionality reduction task",
        normative_text=(
            "Dimensionality reduction consists of reducing the number of attributes per sample "
            "while retaining most of the useful information. Mitigates computation costs. "
            "Methods are unsupervised, supervised or semi-supervised."
        ),
        category="TASK", weight=1,
        search_terms=["dimensionality_reduction", "pca", "principal_component", "embedding",
                      "feature_selection", "autoencoder"],
    ),
    ML23053Check(
        clause_id="6.2.7",
        clause_ref="Other ML tasks (speech recognition, synthesis, translation…)",
        normative_text=(
            "Other tasks include: semantic segmentation of text or images, machine translation, "
            "speech recognition or synthesis, object localisation and image generation. "
            "Structured prediction: output is a structured object rather than single value."
        ),
        category="TASK", weight=2,
        search_terms=["speech_recognition", "text_to_speech", "tts", "synthesis", "translation",
                      "nlp", "object_detection", "generation", "seq2seq"],
    ),

    # ── Clause 6.3: Model ─────────────────────────────────────────────────────
    ML23053Check(
        clause_id="6.3",
        clause_ref="ML Model (training, generalization, retraining, drift)",
        normative_text=(
            "ML model: mathematical construct that generates inference/prediction based on input data. "
            "The model is populated (trained) to represent relevant statistical properties of training data. "
            "Retraining: necessary due to data drift (accuracy decays over time as production data distribution "
            "changes) or concept drift (decision boundary appears to move). "
            "Continuous learning: model performance is continuously evolving from on-going training with production data."
        ),
        category="MODEL", weight=4,
        search_terms=["model", "train", "training", "checkpoint", "weights", "parameters",
                      "inference", "predict", "retraining", "fine_tuning", "model.onnx",
                      "model.pt", "model.bin"],
    ),

    # ── Clause 6.4: Data (training / validation / test / production) ──────────
    ML23053Check(
        clause_id="6.4a",
        clause_ref="Training dataset",
        normative_text=(
            "Training dataset: used to estimate the parameters of candidate models. "
            "For reliable application, training, validation and test data NEED TO BE DISJOINT. "
            "Training data can be labelled, partially labelled, or unlabelled (depending on ML approach)."
        ),
        category="DATA", weight=4,
        search_terms=["training_data", "train_data", "training_set", "train.csv",
                      "train.json", "train.txt", "training"],
    ),
    ML23053Check(
        clause_id="6.4b",
        clause_ref="Validation dataset",
        normative_text=(
            "Validation dataset (also known as development dataset): used to select the best model "
            "according to a performance criterion; used to tune hyperparameters. "
            "Validation and test data are both used with statistical performance measures."
        ),
        category="DATA", weight=3,
        search_terms=["validation_data", "valid_data", "dev_data", "validation_set",
                      "val.csv", "val.json", "hyperparameter_tuning"],
    ),
    ML23053Check(
        clause_id="6.4c",
        clause_ref="Test dataset",
        normative_text=(
            "Test dataset: used to check the generalisation capacity of a model and determines "
            "its performance on future data. For faithful evaluation, test data needs a distribution "
            "as similar as possible to production data."
        ),
        category="DATA", weight=3,
        search_terms=["test_data", "test_set", "test.csv", "test.json", "evaluation_data",
                      "holdout", "generalisation"],
    ),
    ML23053Check(
        clause_id="6.4d",
        clause_ref="Production data (distribution monitoring)",
        normative_text=(
            "Production data: comprised of operational data to be used by the model for prediction. "
            "Distribution of production data can differ from training/validation/test data. "
            "Over time, production data distribution can drift — requires retraining."
        ),
        category="DATA", weight=4,
        search_terms=["production", "inference_data", "online_data", "serving", "production_data",
                      "live_data", "stream"],
    ),

    # ── Clause 6.5.2: Data preparation ────────────────────────────────────────
    ML23053Check(
        clause_id="6.5.2",
        clause_ref="Data preparation (filtering, normalization, de-identification)",
        normative_text=(
            "Data preparation tools: filtering, normalization, de-identification. "
            "Common preparation: statistical exploration, cleaning (correcting/missing entries), "
            "imputation, normalization, scaling, labelling of target variables, encoding."
        ),
        category="TOOLS", weight=3,
        search_terms=["preprocessing", "normalization", "normalize", "cleaning", "imputation",
                      "scaling", "standardize", "encode", "filter", "augment"],
    ),

    # ── Clause 6.5.3: ML Algorithms ───────────────────────────────────────────
    ML23053Check(
        clause_id="6.5.3.2",
        clause_ref="Neural network (NN/DNN/CNN/RNN/LSTM/GAN/Transformer)",
        normative_text=(
            "Neural networks: FFNN, RNN (LSTM, GRU), CNN, structured perceptron, "
            "deep Boltzmann machine, capsule network (CapsNet), GAN. "
            "Deep learning: NNs with many hidden layers. Hyperparameters: number of layers, "
            "width, activation function. Hyperparameter tuning via random search on validation data."
        ),
        category="TOOLS", weight=4,
        search_terms=["neural_network", "deep_learning", "cnn", "rnn", "lstm", "transformer",
                      "attention", "bert", "gpt", "layers", "hidden_layer",
                      "activation", "relu", "softmax", "pytorch", "tensorflow"],
    ),
    ML23053Check(
        clause_id="6.5.3.3",
        clause_ref="Bayesian network",
        normative_text=(
            "Bayesian networks: graphical models for generating predictions on dependencies "
            "between variables. Useful in medical diagnosis; address incomplete data and "
            "mitigate overfitting. Use directed acyclic graphs."
        ),
        category="TOOLS", weight=1,
        search_terms=["bayesian", "bayes", "probabilistic", "directed_acyclic", "dag",
                      "naive_bayes"],
    ),
    ML23053Check(
        clause_id="6.5.3.5",
        clause_ref="Support vector machine (SVM)",
        normative_text=(
            "SVM: ML method widely used for classification and regression. Defines a hyperplane "
            "to separate data into two classes with maximal distance (maximum-margin). "
            "Kernel functions map data to higher-dimensional space."
        ),
        category="TOOLS", weight=1,
        search_terms=["svm", "support_vector", "kernel", "hyperplane", "margin"],
    ),
    ML23053Check(
        clause_id="6.5.3.6",
        clause_ref="Decision tree",
        normative_text=(
            "Decision trees: tree structure of decisions to encode possible outcomes. "
            "Used for classification and regression. Leaf nodes represent final decisions. "
            "Nodes ordered by strength of predictor."
        ),
        category="TOOLS", weight=1,
        search_terms=["decision_tree", "random_forest", "gradient_boosting", "xgboost",
                      "lightgbm", "tree"],
    ),

    # ── Clause 6.5.4: Optimisation methods ────────────────────────────────────
    ML23053Check(
        clause_id="6.5.4",
        clause_ref="ML optimisation (gradient descent, SGD, adaptive learning rate)",
        normative_text=(
            "ML optimisation methods: used to fit an ML model to ML data. Challenge: find optimal "
            "parameters to minimise a given loss function. Gradient descent (SGD, momentum, AdaGrad, "
            "Adam). Regularization: reduces overfitting by penalising complex models (L1/L2)."
        ),
        category="TOOLS", weight=3,
        search_terms=["optimizer", "sgd", "adam", "learning_rate", "loss", "gradient",
                      "regularization", "dropout", "weight_decay", "lr_scheduler"],
    ),

    # ── Clause 6.5.5: Evaluation metrics ──────────────────────────────────────
    ML23053Check(
        clause_id="6.5.5",
        clause_ref="ML evaluation metrics (precision/recall/F1/AUC/MAE/confusion matrix)",
        normative_text=(
            "Evaluation metrics determine ML task suitability. Classification: accuracy, ROC, "
            "confusion matrix, precision, recall, F1 score, AUC. "
            "Regression: MAE, RMSE, relative absolute error, R². "
            "Clustering: avg distance to cluster centre. Multiple metrics required for adequate expression."
        ),
        category="TOOLS", weight=4,
        search_terms=["precision", "recall", "f1", "f1_score", "accuracy", "auc", "roc",
                      "confusion_matrix", "mae", "mse", "rmse", "evaluation", "metric",
                      "wer", "cer", "mos"],  # WER/CER/MOS relevant for TTS/ASR
    ),

    # ── Clause 7.2: Supervised ML approach ────────────────────────────────────
    ML23053Check(
        clause_id="7.2",
        clause_ref="Supervised ML (labelled training data, classification/regression)",
        normative_text=(
            "In supervised ML, models are trained using labelled data (samples with inputs mapped "
            "to correct outputs). Stages: algorithm selection, train the model, tune hyperparameters, "
            "test the model, exercise the model to make predictions."
        ),
        category="APPROACH", weight=3,
        search_terms=["supervised", "labeled", "labelled", "ground_truth", "annotation",
                      "target", "label"],
    ),
    ML23053Check(
        clause_id="7.3",
        clause_ref="Unsupervised ML (unlabelled data, clustering, dimensionality reduction)",
        normative_text=(
            "In unsupervised ML, models map inputs to outputs without being trained on labelled data. "
            "Examples: K-means clustering, PCA dimensionality reduction. "
            "Often results in knowledge discovery."
        ),
        category="APPROACH", weight=2,
        search_terms=["unsupervised", "unlabeled", "unlabelled", "clustering", "pca",
                      "autoencoder", "vae"],
    ),
    ML23053Check(
        clause_id="7.6",
        clause_ref="Reinforcement ML (agent, reward, MDP, policy)",
        normative_text=(
            "Reinforcement ML: model is initialised at a state, an action is taken, a reward is "
            "determined, and model is advanced to new state attempting to maximise reward. "
            "Training: agent learns through trial and error. Modelled as Markov decision process (MDP)."
        ),
        category="APPROACH", weight=1,
        search_terms=["reinforcement", "reward", "agent", "policy", "rl", "q_learning",
                      "ppo", "gym", "environment"],
    ),
    ML23053Check(
        clause_id="7.7",
        clause_ref="Transfer learning (pre-trained model, fine-tuning)",
        normative_text=(
            "Transfer learning: storing and abstracting knowledge from solving one problem and "
            "applying it to a different, loosely related problem. "
            "Fine-tuning technique: a pre-trained model is repurposed and further trained for new problem."
        ),
        category="APPROACH", weight=3,
        search_terms=["transfer_learning", "fine_tuning", "finetune", "pretrained",
                      "pre_trained", "foundation_model", "base_model",
                      "from_pretrained", "checkpoint"],
    ),

    # ── Clause 8: ML Pipeline ─────────────────────────────────────────────────
    ML23053Check(
        clause_id="8.1",
        clause_ref="ML Pipeline — task definition and pipeline structure",
        normative_text=(
            "To reach a particular application goal using ML, an ML model is created, evaluated and "
            "put into use. Before entering the pipeline, it is necessary to define the task. "
            "Cross-cutting throughout the entire pipeline: risk management and governance; "
            "security and privacy; accountability, transparency and explainability; "
            "safety, resilience, robustness and fairness."
        ),
        category="PIPELINE", weight=4,
        search_terms=["pipeline", "workflow", "ml_pipeline", "train.py", "run.sh",
                      "main.py", "config.yaml", "config.json", "Makefile", "Dockerfile"],
    ),
    ML23053Check(
        clause_id="8.2",
        clause_ref="Data acquisition (data stores, streams, sources)",
        normative_text=(
            "Data acquisition: obtaining data from data stores and data streams. "
            "Should define: categories of data needed, quantity, sources "
            "(internal, purchased, shared, open data, synthetic), characteristics, "
            "subject demographics, data rights, provenance."
        ),
        category="PIPELINE", weight=3,
        search_terms=["data_acquisition", "download", "wget", "dataset", "data_loader",
                      "data_source", "data_pipeline", "fetch_data", "stream"],
    ),
    ML23053Check(
        clause_id="8.3",
        clause_ref="Data preparation (wrangling, cleaning, imputation, normalization, splitting, labelling)",
        normative_text=(
            "Data preparation includes: exploring, data wrangling, cleaning, imputation, "
            "normalization and scaling, dataset composition, data splitting (train/val/test), "
            "labelling, and other transforms. "
            "Machine learning algorithms can be intolerant of missing or incorrect entries, "
            "non-normal distributions and widely varying scales."
        ),
        category="PIPELINE", weight=4,
        search_terms=["preprocessing", "data_prep", "cleaning", "split", "augmentation",
                      "normalize", "impute", "wrangling", "transform", "tokenize",
                      "tokenizer", "feature_extraction"],
    ),
    ML23053Check(
        clause_id="8.4",
        clause_ref="Modelling (feature engineering, algorithm selection, model training, model selection)",
        normative_text=(
            "Modelling stage includes: feature engineering, algorithm selection, model training, "
            "model selection (hyperparameter tuning). "
            "The choice of the ML algorithm is often insufficient — hyperparameters SHALL also be chosen. "
            "One practical approach: random search guided by constraint function on validation dataset."
        ),
        category="PIPELINE", weight=4,
        search_terms=["model_training", "train.py", "feature_engineering", "hyperparameter",
                      "model_selection", "cross_validation", "grid_search", "random_search",
                      "epochs", "batch_size"],
    ),
    ML23053Check(
        clause_id="8.5",
        clause_ref="Verification and validation (model evaluation, system validation)",
        normative_text=(
            "Verification and validation: model evaluation (using evaluation metrics on test data) "
            "and system validation. The aim of test data is to verify that the trained model will "
            "perform well on production data. Overfitted models: significant difference between "
            "training errors and test/validation errors."
        ),
        category="PIPELINE", weight=4,
        search_terms=["evaluate", "evaluation", "test", "benchmark", "validation",
                      "performance", "accuracy", "f1", "wer", "test_suite", "pytest"],
    ),
    ML23053Check(
        clause_id="8.6",
        clause_ref="Model deployment (packaging, runtime environment, optimisation)",
        normative_text=(
            "Model deployment: packaging, runtime environment, optimisation. "
            "AI systems can be developed in various environments and deployed in others. "
            "Consider: components deployed separately (software and model), "
            "release criteria met prior to deployment."
        ),
        category="PIPELINE", weight=3,
        search_terms=["deployment", "serving", "inference_server", "onnx", "torchscript",
                      "docker", "kubernetes", "container", "packaging", "export",
                      "quantization", "pruning", "model_server"],
    ),
    ML23053Check(
        clause_id="8.7",
        clause_ref="Operation (maintain, repair, update, monitoring — including drift)",
        normative_text=(
            "Operation: maintain, repair, update, monitoring. "
            "Deployed AI systems evolve: production data and output data used to retrain model. "
            "Performance of some AI systems can change even without continuous learning (data drift, "
            "concept drift in production data) — monitoring can identify need for retraining."
        ),
        category="PIPELINE", weight=4,
        search_terms=["monitoring", "maintenance", "update", "retraining", "drift",
                      "alerting", "logging", "CI", "continuous_deployment", "rollback"],
    ),

    # ── Cross-cutting (Figure 12) ─────────────────────────────────────────────
    ML23053Check(
        clause_id="xc.risk",
        clause_ref="Risk management and governance (cross-cutting entire pipeline)",
        normative_text=(
            "Risk management and governance applies across the entire ML pipeline (Figure 12). "
            "Data quality can be a risk source: if incomplete or reflects societal bias, "
            "the model performance will reflect this."
        ),
        category="CROSS_CUTTING", weight=4,
        search_terms=["risk", "governance", "risk_management", "compliance", "responsible_ai",
                      "safety_check", "bias_check"],
    ),
    ML23053Check(
        clause_id="xc.security",
        clause_ref="Security and privacy (cross-cutting: data poisoning, model stealing, inversion)",
        normative_text=(
            "Security and privacy applies across the entire ML pipeline. "
            "Security threats specific to ML: data poisoning, model stealing, model inversion attacks. "
            "Privacy: de-identification, PII handling in training data."
        ),
        category="CROSS_CUTTING", weight=4,
        search_terms=["security", "privacy", "pii", "gdpr", "de_identification",
                      "encryption", "access_control", "adversarial"],
    ),
    ML23053Check(
        clause_id="xc.transparency",
        clause_ref="Accountability, transparency and explainability (cross-cutting)",
        normative_text=(
            "Accountability, transparency and explainability apply across the entire ML pipeline. "
            "Transparency: data provenance, ability to provide explanation of how data are used "
            "for determining the AI system's output."
        ),
        category="CROSS_CUTTING", weight=3,
        search_terms=["explainability", "xai", "shap", "lime", "interpretability",
                      "transparency", "explain", "provenance"],
    ),
    ML23053Check(
        clause_id="xc.safety",
        clause_ref="Safety, resilience, robustness and fairness (cross-cutting)",
        normative_text=(
            "Safety, resilience, robustness and fairness apply across the entire ML pipeline. "
            "Robustness: ability of the system to have comparable performance on new data as "
            "on training data. Fairness: ML systems will replicate, amplify and expedite existing "
            "faults and inequities."
        ),
        category="CROSS_CUTTING", weight=4,
        search_terms=["fairness", "bias", "robustness", "safety", "resilience",
                      "adversarial_robustness", "equitable", "demographic_parity"],
    ),
]


def scan_23053(root: Path, idx: IndexStoreAdapter) -> list[ML23053Check]:
    """Scan codebase for ISO/IEC 23053:2022 ML framework elements."""
    for check in ML_CHECKS:
        hits: set[str] = set()
        match_count = 0

        for term in check.search_terms:
            try:
                results = idx.search_code(term, limit=5)
                for r in results:
                    if r.path and not any(x in r.path for x in
                                          ("node_modules", ".git", "vendor", "__pycache__")):
                        hits.add(r.path)
                        match_count += 1
            except Exception:
                pass

        check.evidence_files = sorted(list(hits))[:5]
        check.found = len(check.evidence_files) > 0

        if match_count >= len(check.search_terms) * 0.5:
            check.confidence = "HIGH"
        elif match_count >= 2:
            check.confidence = "MEDIUM"
        elif match_count >= 1:
            check.confidence = "LOW"
        else:
            check.confidence = "NONE"

    return ML_CHECKS


def calculate_score(checks: list[ML23053Check]) -> tuple[int, str, str]:
    total_weight = sum(c.weight for c in checks)
    achieved = 0.0
    for c in checks:
        if c.confidence == "HIGH":
            achieved += c.weight * 1.0
        elif c.confidence == "MEDIUM":
            achieved += c.weight * 0.6
        elif c.confidence == "LOW":
            achieved += c.weight * 0.3

    score = int((achieved / total_weight) * 100) if total_weight > 0 else 0

    if score >= 75:
        grade = "A  (Well-aligned with ISO 23053 ML Framework)"
        status = "🟢 HIGH CONFORMANCE — ML pipeline stages and cross-cutting concerns evidenced"
    elif score >= 50:
        grade = "B  (Partial ML Framework)"
        status = "🟡 PARTIAL — Core ML pipeline present, gaps in cross-cutting concerns"
    elif score >= 25:
        grade = "C  (Basic ML Elements)"
        status = "🟠 LOW — Some ML elements found, framework systematisation lacking"
    else:
        grade = "F  (No ML Framework Evidence)"
        status = "🔴 CRITICAL — No evidence of structured ML pipeline or framework"

    return score, grade, status


def print_report(project: str, root: Path, checks: list[ML23053Check],
                 stats: dict, elapsed: float, report_path: Path) -> None:
    score, grade, status = calculate_score(checks)
    conf_icon = {"HIGH": "✅", "MEDIUM": "🟡", "LOW": "⚠️", "NONE": "❌"}
    found_count = sum(1 for c in checks if c.found)

    by_cat: dict[str, list[ML23053Check]] = {}
    for c in checks:
        by_cat.setdefault(c.category, []).append(c)

    lines = [
        f"# 🧠 ISO/IEC 23053:2022 ML Framework Audit — {project}",
        f"> `{root}` · {stats.get('total_files', 0):,} files · {elapsed:.2f}s · {date.today()}",
        "",
        "## 📊 ML Framework Compliance Summary",
        "",
        "| Metric | Value |",
        "|---|---|",
        f"| **ISO 23053 Framework Score** | **{score} / 100** |",
        f"| **Grade** | **{grade}** |",
        f"| **Status** | **{status}** |",
        f"| Total Files Scanned | {stats.get('total_files', 0):,} |",
        f"| Elements with Evidence | {found_count} / {len(checks)} |",
        "",
        "> **Standard**: ISO/IEC 23053:2022 — Framework for Artificial Intelligence (AI) Systems Using Machine Learning (ML).",
        "> **Clauses audited**: 6 (ML System: Task/Model/Data/Tools), 7 (ML Approaches), 8 (ML Pipeline), Cross-cutting concerns (Figure 12).",
        "",
    ]

    cat_titles = {
        "TASK": "§6.2 ML Tasks (Regression / Classification / Clustering / Anomaly / Dim-Reduction)",
        "MODEL": "§6.3 ML Model (Training / Drift / Retraining)",
        "DATA": "§6.4 Data (Train / Validation / Test / Production — disjoint requirement)",
        "TOOLS": "§6.5 Tools (Data Prep / Algorithms / Optimisation / Evaluation Metrics)",
        "APPROACH": "§7 ML Approaches (Supervised / Unsupervised / Reinforcement / Transfer)",
        "PIPELINE": "§8 ML Pipeline (Acquisition / Preparation / Modelling / V&V / Deployment / Operation)",
        "CROSS_CUTTING": "Figure 12 Cross-Cutting Concerns (Risk / Security / Transparency / Safety)",
    }

    for cat, cat_checks in by_cat.items():
        title = cat_titles.get(cat, cat)
        lines += [
            f"## 🔍 {title}",
            "",
            "| Clause | Element | Confidence | Evidence |",
            "|---|---|---|---|",
        ]
        for c in cat_checks:
            icon = conf_icon[c.confidence]
            ev = ", ".join(f"`{e}`" for e in c.evidence_files[:2]) if c.evidence_files else "—"
            lines.append(
                f"| `{c.clause_id}` | {c.clause_ref} | {icon} {c.confidence} | {ev} |"
            )
        lines.append("")

    # Gaps
    gaps = [c for c in checks if c.confidence in ("NONE", "LOW")]
    if gaps:
        lines += [
            "## ⚠️ Significant Gaps vs ISO/IEC 23053:2022",
            "",
            "Elements with no or low evidence:",
            "",
        ]
        for g in gaps:
            lines.append(
                f"- **{g.clause_id}** {g.clause_ref} (weight={g.weight}): "
                f"{g.normative_text[:100]}…"
            )
        lines.append("")

    lines += [
        "## 🛠 ISO 23053 Alignment Recommendations",
        "",
        "### §6.2 — Explicitly declare your ML Task type",
        "- State in README/model card: which ML task (classification, regression, synthesis, etc.)",
        "- TTS systems perform **§6.2.7 Other tasks (speech synthesis)** — declare this explicitly",
        "",
        "### §6.4 — Data partition documentation",
        "- Document the train/validation/test/production split strategy",
        "- Verify disjoint-ness of train, validation and test datasets",
        "- Monitor production data distribution for drift (§6.3, §8.7)",
        "",
        "### §6.5.5 — Evaluation metrics aligned to task",
        "- For TTS/speech synthesis: use **WER, CER, MOS, naturalness scores**",
        "- For classification: precision, recall, F1, AUC (§6.5.5.3–6.5.5.5)",
        "- Multiple metrics are required; single metric (e.g. accuracy) is insufficient (§6.5.5.1)",
        "",
        "### §8.3 — Data preparation documentation",
        "- Document all preprocessing steps (normalization, encoding, augmentation)",
        "- Document data cleaning procedures and imputation methods",
        "",
        "### §8.5 — V&V",
        "- Define release criteria: minimum acceptable performance thresholds on test data",
        "- Test data distribution should match production data distribution",
        "",
        "### Figure 12 Cross-cutting",
        "- **Security**: address data poisoning, model stealing, model inversion threats",
        "- **Fairness**: audit training data for demographic bias before model training",
        "- **Transparency**: provide data provenance and explainability documentation",
        "",
        "---",
        f"*ISO/IEC 23053:2022 ML Framework Auditor · {date.today()}*",
    ]

    report_path.write_text("\n".join(lines), encoding="utf-8")

    SEP = "═" * 78
    print(f"\n{SEP}")
    print(f"  ISO/IEC 23053:2022 ML FRAMEWORK AUDIT: {project}")
    print(SEP)
    print(f"  Files indexed               : {stats.get('total_files', 0):,}")
    print(f"  ML Framework Score          : {score} / 100")
    print(f"  Grade                       : {grade}")
    print(f"  Elements with Evidence      : {found_count} / {len(checks)}")
    print(f"  Audit Duration              : {elapsed:.3f}s")
    print(f"  Report                      : {report_path}")
    print(f"{SEP}\n")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 iso_23053_ml_framework_audit.py /path/to/project [ProjectName]")
        sys.exit(1)

    project_path = Path(sys.argv[1]).expanduser().resolve()
    if not project_path.exists():
        print(f"❌ Path not found: {project_path}")
        sys.exit(1)

    project_name = sys.argv[2] if len(sys.argv) > 2 else project_path.name

    app_data = Path.home() / ".gemini" / "antigravity-cli" / "brain" / "b1a8b172-4960-462a-bad1-43d8b7e774ad"
    app_data.mkdir(parents=True, exist_ok=True)

    safe_name = re.sub(r"[^a-z0-9_]", "_", project_name.lower())
    report_path = app_data / f"iso_23053_{safe_name}.md"

    t0 = time.perf_counter()
    idx = IndexStoreAdapter()
    stats = idx.rebuild(project_path)
    checks = scan_23053(project_path, idx)
    elapsed = time.perf_counter() - t0

    print_report(project_name, project_path, checks, stats, elapsed, report_path)


if __name__ == "__main__":
    main()
