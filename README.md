<div align="center">

# HERMES

### Hypothesis-driven Exploration through Reasoning for Modeling and Executing Semantic Workflows

**An Autonomous Stateful Web Workflow Fuzzing Framework**

![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)
![Playwright](https://img.shields.io/badge/Playwright-Latest-green.svg)
![Flask](https://img.shields.io/badge/Flask-HERMES--Bench-red.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Research](https://img.shields.io/badge/Research-Prototype-success.svg)
![Evaluation](https://img.shields.io/badge/Evaluation-370%20Workflow%20Executions-blueviolet.svg)

</div>

---

# Overview

HERMES (**Hypothesis-driven Exploration through Reasoning for Modeling and Executing Semantic Workflows**) is an autonomous framework for **stateful web workflow fuzzing**.

Unlike conventional web fuzzers that primarily mutate requests, parameters, or payloads, HERMES discovers semantic workflows, constructs workflow state graphs, generates workflow-context mutations, executes mutated workflows automatically, and compares behavioral outcomes to identify state-dependent business logic anomalies.

The framework introduces **workflow-context mutation** as a complementary fuzzing strategy for evaluating stateful web applications whose behavior depends on execution history rather than isolated requests.

---

# Project Statistics

| Metric | Value |
|---------|------:|
| Programming Language | Python 3.12+ |
| Framework Status | Complete |
| Benchmark | HERMES-Bench |
| Automated Workflow Executions | 370 |
| License | MIT |

---

# Motivation

Modern web applications rely heavily on application state.

Examples include:

- User authentication
- Shopping carts
- Wallet balances
- Checkout workflows
- Order history
- Session history
- Permission chains
- Business logic dependencies

Traditional web fuzzers mainly mutate:

- HTTP requests
- Parameters
- Payloads
- URLs

While effective for input validation, these techniques often overlook faults that emerge only after specific workflow histories.

HERMES addresses this limitation by treating **the workflow itself as the fuzzing target**, enabling systematic exploration of state-dependent behaviors.

---

# Research Contributions

HERMES provides the following capabilities:

- Automatic workflow discovery
- Stateful graph construction
- Semantic operation discovery
- Workflow generation
- Workflow prioritization
- Generic workflow mutation
- Hypothesis-driven workflow mutation
- Automated Playwright execution
- Behavioral comparison
- Scientific evaluation pipeline
- Reproducible experimental results

---

# Framework Architecture

> Replace the filename below with your actual architecture figure.

```markdown
![HERMES Framework Architecture](docs/figures/fig1_architecture.png)
```

The framework follows a modular pipeline consisting of:

```
Crawler
    │
    ▼
State Graph Builder
    │
    ▼
Semantic Operation Discovery
    │
    ▼
Workflow Generator
    │
    ▼
Workflow Prioritization
    │
    ▼
Workflow Mutation Engine
    │
    ▼
Execution Engine
    │
    ▼
Behavior Comparator
    │
    ▼
Scientific Evaluation
```

Each component is modular, independently testable, and designed to facilitate future research extensions.

---

# Repository Status

| Component | Status |
|-----------|--------|
| Framework | ✅ Complete |
| HERMES-Bench | ✅ Complete |
| Workflow Discovery | ✅ Complete |
| Mutation Engine | ✅ Complete |
| Execution Engine | ✅ Complete |
| Scientific Evaluation | ✅ Complete |
| Automated Tests | ✅ Complete |
| Research Artifact | ✅ Ready |

---

# Evaluation Summary

The current implementation has been evaluated using **HERMES-Bench**, a purpose-built benchmark for stateful workflow fuzzing.

The evaluation consists of baseline workflow execution, generic workflow mutations, and hypothesis-driven workflow mutations.

| Experiment | Executions |
|------------|-----------:|
| Baseline Workflows | 25 |
| Generic Workflow Mutations | 320 |
| Hypothesis-driven Workflow Mutations | 25 |
| **Total Workflow Executions** | **370** |

The evaluation pipeline automatically generates:

- JSON execution reports
- CSV result summaries
- LaTeX tables
- Publication-ready figures
- Statistical summaries
- Scientific evaluation reports

---

# Scientific Evaluation Pipeline

> Replace the filename below with your actual evaluation pipeline figure.

```markdown
![Scientific Evaluation Pipeline](docs/figures/fig2_evaluation_pipeline.png)
```

The evaluation pipeline automatically executes complete workflow experiments, collects execution results, compares behavioral outcomes, and produces reproducible research artifacts suitable for publication.

---

# Repository Structure

```
hermes-framework/
│
├── src/                    # Core framework implementation
├── tests/                  # Unit and integration tests
├── scripts/                # Helper and execution scripts
├── evaluation/             # Scientific evaluation pipeline
├── docs/
│   └── figures/            # Paper and README figures
├── configs/                # Experiment configuration files
├── requirements.txt
├── pyproject.toml
├── LICENSE
└── README.md
```

---

# Installation

Clone the repository.

```bash
git clone https://github.com/SDET-Hamad-KMughal/hermes-framework.git
cd hermes-framework
```

Create a virtual environment.

```bash
python -m venv venv
```

Activate the environment.

Windows

```bash
venv\Scripts\activate
```

Linux / macOS

```bash
source venv/bin/activate
```

Install the required dependencies.

```bash
pip install -r requirements.txt
```

Install Playwright browsers.

```bash
playwright install
```

Verify the installation.

```bash
pytest -q
```

All tests should complete successfully.

---

# Quick Start

Run the complete scientific evaluation.

```bash
python scripts/run_scientific_evaluation.py \
    --config evaluation/configs/experiment.json
```

The framework automatically performs:

1. Workflow discovery
2. State graph construction
3. Semantic operation identification
4. Workflow generation
5. Workflow mutation
6. Automated execution
7. Behavioral comparison
8. Result aggregation

Generated outputs include:

- Raw execution reports
- Aggregated metrics
- CSV summaries
- LaTeX tables
- Publication-ready figures

All outputs are written automatically to the `evaluation/` directory.

---

# Output Directory

After execution, generated artifacts are organized as follows:

```
evaluation/
│
├── reports/
├── figures/
├── tables/
├── logs/
└── summary.json
```

This directory contains all experimental outputs required to reproduce the reported evaluation.

---

# HERMES-Bench

HERMES is evaluated using **HERMES-Bench**, a purpose-built benchmark designed specifically for stateful workflow fuzzing research.

Unlike traditional web testing benchmarks, HERMES-Bench models realistic business workflows with persistent application state, enabling systematic evaluation of workflow-context mutations.

Implemented functionality includes:

- User Registration
- User Authentication
- Product Catalog
- Shopping Cart
- Wallet Management
- Checkout
- Order History
- Administrative Dashboard

The benchmark also includes **seeded business-logic anomalies** for validating workflow mutation strategies.

---

# Benchmark Workflows

Representative workflows include:

| Workflow | Description |
|----------|-------------|
| User Login | Authenticate a registered user |
| Wallet Top-up | Increase account balance |
| Browse Catalog | Explore available products |
| Add to Cart | Add products to shopping cart |
| Checkout | Complete a purchase |
| View Orders | Access purchase history |
| Logout | Terminate authenticated session |

These workflows form the baseline used throughout the experimental evaluation.

---

# Mutation Strategies

HERMES currently supports two complementary mutation strategies.

## Generic Workflow Mutations

Generic mutations explore alternative workflow executions without relying on domain-specific knowledge.

Implemented operators include:

- Step insertion
- Step deletion
- Adjacent swap
- Non-adjacent swap
- Workflow reordering
- Prerequisite removal

---

## Hypothesis-driven Workflow Mutations

Hypothesis-driven mutations validate security and business-logic assumptions by intentionally modifying workflow history.

Representative examples include:

- Checkout without authentication
- Checkout with insufficient balance
- Duplicate wallet top-up
- Unauthorized order history access
- Missing prerequisite operations
- Invalid workflow sequencing

Each mutated workflow is executed independently and compared against the corresponding baseline execution.

---

# Reproducibility

HERMES emphasizes reproducible software engineering research.

Running the evaluation pipeline automatically reproduces:

- Workflow execution reports
- JSON outputs
- CSV summaries
- LaTeX tables
- Publication-ready figures
- Experimental metrics

All reported experimental results are generated automatically by the framework.

---

# Citation

If you use HERMES in your research, please cite:

```bibtex
@misc{hermes2026,
  title={HERMES: Hypothesis-driven Exploration through Reasoning for Modeling and Executing Semantic Workflows},
  author={Hamad Sajad Mughal},
  year={2026},
  note={Conference Research Artifact}
}
```

This citation will be updated following the official conference publication.

---

# Future Work

Planned extensions include:

- Additional benchmark applications
- New workflow mutation operators
- LLM-assisted semantic workflow reasoning
- Distributed workflow execution
- Cross-application workflow analysis
- Large-scale empirical evaluation

---

# License

This project is released under the **MIT License**.

See the `LICENSE` file for complete licensing information.

---

# Acknowledgements

HERMES was developed as part of ongoing research in autonomous software testing and stateful web workflow fuzzing.

The framework is intended to support future research in:

- Stateful Web Fuzzing
- Business Logic Testing
- Semantic Workflow Analysis
- Software Testing and Verification
- Web Security Evaluation

---

# Repository Status

| Component | Status |
|-----------|--------|
| Framework | ✅ Complete |
| HERMES-Bench | ✅ Complete |
| Workflow Discovery | ✅ Complete |
| Mutation Engine | ✅ Complete |
| Execution Engine | ✅ Complete |
| Scientific Evaluation | ✅ Complete |
| Conference Artifact | ✅ Ready |

---

<div align="center">

## HERMES

**Hypothesis-driven Exploration through Reasoning for Modeling and Executing Semantic Workflows**

*Advancing stateful web workflow fuzzing through semantic workflow mutation and reproducible scientific evaluation.*

© 2026 Hammad Sajjad Mughal

</div>