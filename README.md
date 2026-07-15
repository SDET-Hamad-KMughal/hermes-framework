# HERMES

<div align="center">

# HERMES
### Hypothesis-driven Exploration through Reasoning for Modeling and Executing Semantic Workflows

**An Autonomous Stateful Web Workflow Fuzzing Framework**

---

![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)
![Playwright](https://img.shields.io/badge/Playwright-Latest-green.svg)
![Flask](https://img.shields.io/badge/Flask-HERMES--Bench-red.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Research](https://img.shields.io/badge/Research-Prototype-success.svg)
![Evaluation](https://img.shields.io/badge/Evaluation-370%20Workflow%20Executions-blueviolet.svg)

</div>

---

# Overview

HERMES (**Hypothesis-driven Exploration through Reasoning for Modeling and Executing Semantic Workflows**) is a research framework for **stateful web workflow fuzzing**.

Unlike traditional web fuzzers that mutate HTTP requests or individual inputs, HERMES discovers complete business workflows, reasons about their semantic dependencies, generates workflow mutations, executes them automatically, and compares behavioral outcomes to detect state-dependent business logic anomalies.

The framework introduces a **hypothesis-driven workflow mutation strategy**, enabling security testing beyond conventional input mutation.

---

# Motivation

Modern web applications are highly stateful.

Critical functionality often depends on:

- authenticated sessions
- previous workflow history
- business rules
- inventory state
- financial balance
- authorization chains
- workflow ordering

Traditional fuzzers primarily explore:

- HTTP parameters
- request payloads
- form inputs
- URL mutations

They rarely reason about workflow history itself.

As a result, many business logic vulnerabilities remain undiscovered.

Examples include:

- checkout without authentication
- order history disclosure
- duplicated financial transactions
- missing prerequisite operations
- workflow reordering
- inconsistent authorization

HERMES addresses this gap by treating workflows themselves as the fuzzing target.

---

# Research Objective

The objective of HERMES is to automatically discover semantic workflows, generate hypothesis-driven mutations, execute mutated workflows, and detect state-dependent behavioral anomalies through systematic comparison.

Rather than asking

> "What happens if this input changes?"

HERMES asks

> "What happens if the workflow history changes while preserving semantic intent?"

---

# Key Contributions

HERMES introduces the following research contributions.

## 1. Semantic Workflow Discovery

Automatic identification of application operations and workflow dependencies.

---

## 2. State Graph Construction

Automatic construction of workflow state graphs from crawler observations.

---

## 3. Semantic Operation Discovery

Extraction of meaningful business operations from application behavior.

Examples include:

- Login
- Logout
- Wallet Top-up
- Checkout
- View Orders
- Profile Update

instead of merely recording URLs.

---

## 4. Workflow Generation

Automatic synthesis of executable business workflows from discovered semantic operations.

---

## 5. Workflow Prioritization

Ranking workflows according to structural importance, semantic complexity, state transitions, and execution characteristics.

---

## 6. Generic Workflow Mutation

Generation of workflow mutations using structural transformations such as:

- insertion
- deletion
- swapping
- prerequisite removal
- workflow shortening

---

## 7. Hypothesis-driven Mutation

Generation of mutations based on explicit security hypotheses.

Examples:

- authentication removal

- duplicate payment execution

- unauthorized order history access

- repeated checkout

- wallet manipulation

---

## 8. Stateful Workflow Execution

Automatic execution of generated workflows using Playwright.

---

## 9. Behavioral Comparison

Comparison of baseline and mutated executions using multiple behavioral dimensions.

Examples include:

- success status
- execution duration
- state divergence
- semantic outcome
- workflow completion

---

## 10. Scientific Evaluation Pipeline

Complete reproducible evaluation pipeline supporting:

- repeated executions
- CSV generation
- LaTeX table generation
- publication figures
- ground-truth evaluation

---

# Research Hypothesis

The central hypothesis of HERMES is:

> Mutating workflow history while preserving semantic intent exposes business logic vulnerabilities that cannot be discovered through traditional request-level fuzzing.

---

# HERMES Workflow

The overall execution pipeline is shown below.

```
                    Crawl Application
                           │
                           ▼
                 Build State Graph
                           │
                           ▼
              Discover Semantic Operations
                           │
                           ▼
               Generate Workflows
                           │
                           ▼
               Prioritize Workflows
                           │
                           ▼
           Generate Generic Mutations
                           │
                           ▼
      Generate Hypothesis Mutations
                           │
                           ▼
             Execute All Workflows
                           │
                           ▼
              Compare Behaviors
                           │
                           ▼
             Detect Divergences
                           │
                           ▼
           Scientific Evaluation
                           │
                           ▼
          Tables • Figures • Reports
```

---

# Framework Architecture

The framework is organized into independent research modules.

```
Crawler
    │
    ▼
State Graph Builder
    │
    ▼
Semantic Discovery Engine
    │
    ▼
Workflow Generator
    │
    ▼
Workflow Prioritizer
    │
    ▼
Mutation Engine
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

Each module is independently testable and can be reused for future research extensions.

---

# Current Implementation Status

| Module | Status |
|---------|--------|
| Crawler | ✅ Complete |
| State Graph Builder | ✅ Complete |
| Semantic Discovery | ✅ Complete |
| Workflow Generator | ✅ Complete |
| Workflow Prioritization | ✅ Complete |
| Generic Mutation Engine | ✅ Complete |
| Hypothesis Mutation Engine | ✅ Complete |
| Playwright Execution Engine | ✅ Complete |
| Behavior Comparator | ✅ Complete |
| Scientific Evaluation | ✅ Complete |
| Ground Truth Validation | ✅ Complete |
| HERMES-Bench | ✅ Complete |

---

# Evaluation Summary

The current implementation has been evaluated using HERMES-Bench.

Final evaluation consists of:

| Experiment | Executions |
|------------|-----------:|
| Baseline | 25 |
| Generic Mutations | 320 |
| Hypothesis Mutations | 25 |
| **Total** | **370** |

The framework automatically produces:

- JSON execution reports
- aggregated metrics
- CSV tables
- LaTeX tables
- publication-ready figures
- scientific summaries

---
---

# Repository Structure

The HERMES repository is organized as a modular research framework. Each component represents an independent stage of the workflow fuzzing pipeline, allowing researchers to extend or replace individual modules without affecting the overall architecture.

```
hermes-framework/
│
├── src/
│   └── hermes/
│       ├── crawler/
│       ├── state_graph/
│       ├── semantic/
│       ├── workflow/
│       ├── prioritization/
│       ├── mutation/
│       ├── execution/
│       ├── comparator/
│       ├── evaluation/
│       └── utils/
│
├── scripts/
│
├── evaluation/
│   ├── configs/
│   ├── raw/
│   ├── aggregated/
│   ├── tables/
│   │   ├── csv/
│   │   └── latex/
│   ├── figures/
│   └── archive/
│
├── tests/
│
├── docs/
│
├── requirements.txt
│
└── README.md
```

---

# Core Framework Modules

The framework is divided into independent research modules.

| Module | Purpose |
|---------|----------|
| Crawler | Discovers application pages and navigation paths |
| State Graph Builder | Builds workflow state transition graphs |
| Semantic Discovery | Identifies meaningful business operations |
| Workflow Generator | Synthesizes executable workflows |
| Workflow Prioritizer | Ranks workflows for execution |
| Generic Mutation Engine | Produces structural workflow mutations |
| Hypothesis Engine | Produces security-driven workflow mutations |
| Execution Engine | Executes workflows using Playwright |
| Behavior Comparator | Detects behavioral divergence |
| Scientific Evaluation | Produces evaluation reports and publication artifacts |

---

# Repository Components

## Source Code

The `src/` directory contains the complete HERMES implementation.

It includes:

- workflow discovery
- semantic reasoning
- mutation generation
- execution engine
- comparator
- evaluation modules

All framework logic resides inside this package.

---

## Scripts

The `scripts/` directory provides executable utilities for reproducing every experiment.

Typical scripts include:

- scientific evaluation
- table generation
- figure generation
- ground-truth evaluation
- benchmark execution

Researchers can reproduce the complete evaluation without modifying the framework source code.

---

## Evaluation

All experimental outputs are written into the `evaluation/` directory.

The directory is divided into multiple subfolders to separate raw executions from processed publication artifacts.

### evaluation/raw

Contains JSON reports for every workflow execution.

Each record includes execution metadata such as:

- workflow identifier
- mutation strategy
- execution status
- duration
- comparison outcome
- anomaly information

---

### evaluation/aggregated

Contains aggregated summaries derived from the raw execution reports.

Examples include:

- experiment summaries
- anomaly statistics
- workflow metrics
- mutation statistics
- ground-truth evaluation

---

### evaluation/tables

Automatically generated publication tables.

Two formats are supported.

#### CSV

Suitable for spreadsheet analysis.

#### LaTeX

Ready for direct inclusion in academic papers.

---

### evaluation/figures

Publication-quality figures generated directly from evaluation results.

Typical visualizations include:

- workflow distribution
- mutation strategy distribution
- anomaly rate
- execution summary
- comparison statistics

These figures can be inserted directly into research papers.

---

### evaluation/archive

Stores previous evaluation runs.

This prevents older experimental outputs from being overwritten while maintaining complete reproducibility.

---

## Tests

The `tests/` directory contains the automated validation suite for the framework.

Current implementation validates:

- crawler
- workflow generation
- semantic discovery
- mutation engine
- execution engine
- comparator
- evaluation pipeline
- ground-truth evaluation

The entire framework can be verified automatically using Pytest.

---

## Documentation

The `docs/` directory stores supplementary documentation, diagrams, design notes, and future extensions.

---

# Software Requirements

The framework has been developed and evaluated using the following software environment.

| Component | Version |
|-----------|---------|
| Python | 3.12+ |
| Playwright | Latest |
| Flask | Latest |
| SQLite | 3.x |
| Git | Latest |
| Pytest | Latest |

---

# Hardware Requirements

The experiments reported in this repository were executed on a standard desktop workstation.

Recommended minimum requirements are:

| Component | Recommendation |
|-----------|----------------|
| CPU | Quad-Core Processor |
| RAM | 8 GB |
| Storage | 2 GB Available |
| Operating System | Windows 11 / Linux |

No GPU is required.

---

# Installing HERMES

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

### Windows

```bash
venv\Scripts\activate
```

### Linux

```bash
source venv/bin/activate
```

Install dependencies.

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

A successful installation should complete without test failures.

---

# First Execution

Run the complete scientific evaluation.

```bash
python scripts/run_scientific_evaluation.py \
    --config evaluation/configs/experiment.json
```

This automatically generates:

- raw execution reports
- aggregated summaries
- publication tables
- scientific metrics

The generated outputs are stored under the `evaluation/` directory.

---
---

# Quick Start

This section demonstrates how to reproduce the complete HERMES evaluation from a clean repository checkout.

---

## Step 1 — Clone the Repository

```bash
git clone https://github.com/SDET-Hamad-KMughal/hermes-framework.git

cd hermes-framework
```

---

## Step 2 — Create a Virtual Environment

```bash
python -m venv venv
```

Activate the environment.

### Windows

```bash
venv\Scripts\activate
```

### Linux

```bash
source venv/bin/activate
```

---

## Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

Install Playwright browsers.

```bash
playwright install
```

---

## Step 4 — Verify Installation

Run the complete automated validation suite.

```bash
pytest -q
```

A successful installation should complete with all tests passing.

---

# Running the Complete Scientific Evaluation

The entire evaluation pipeline is executed using a single command.

```bash
python scripts/run_scientific_evaluation.py \
    --config evaluation/configs/experiment.json
```

The framework automatically executes:

1. Baseline workflows
2. Generic workflow mutations
3. Hypothesis-driven mutations
4. Behavioral comparison
5. Result aggregation

---

# Scientific Evaluation Pipeline

The evaluation follows the pipeline below.

```
Baseline Workflows
        │
        ▼
Generic Mutations
        │
        ▼
Hypothesis Mutations
        │
        ▼
Workflow Execution
        │
        ▼
Behavior Comparison
        │
        ▼
Evaluation Metrics
        │
        ▼
Tables
        │
        ▼
Figures
```

---

# Execution Output

The evaluation automatically produces several categories of artifacts.

## Raw Execution Reports

```
evaluation/raw/
```

Contains one JSON file for every workflow execution.

Each report records:

- workflow identifier
- mutation strategy
- execution duration
- execution status
- anomaly metadata
- comparison outcome

---

## Aggregated Reports

```
evaluation/aggregated/
```

Contains experiment summaries generated from all execution reports.

Examples include:

- experiment summary
- workflow statistics
- mutation statistics
- anomaly summary
- ground-truth metrics

---

## CSV Tables

```
evaluation/tables/csv/
```

Automatically generated spreadsheet-friendly tables suitable for statistical analysis.

---

## LaTeX Tables

```
evaluation/tables/latex/
```

Publication-ready tables that can be directly included in IEEE, ACM, Springer, or Elsevier papers.

---

## Publication Figures

```
evaluation/figures/
```

Automatically generated figures suitable for research publications.

Examples include:

- workflow distribution
- mutation distribution
- anomaly rate
- execution summary
- comparison metrics

---

# HERMES-Bench

The framework is evaluated using **HERMES-Bench**, a purpose-built benchmark designed for stateful workflow fuzzing research.

HERMES-Bench models realistic e-commerce behavior with authenticated user workflows and state-dependent business logic.

Implemented functionality includes:

- User registration
- User authentication
- Product catalog
- Shopping cart
- Checkout
- Wallet top-up
- Order history
- Administrative monitoring

Unlike synthetic benchmarks, HERMES-Bench preserves workflow dependencies between operations, making it suitable for evaluating state-aware workflow fuzzing techniques.

---

# Benchmark Workflows

The current benchmark contains representative business workflows including:

| Workflow | Description |
|----------|-------------|
| Login | Authenticate a registered user |
| Wallet Top-up | Increase account balance |
| Checkout | Purchase products |
| View Orders | Display historical orders |
| Logout | Terminate authenticated session |

These workflows serve as the baseline for workflow mutation experiments.

---

# Mutation Strategies

HERMES currently supports two complementary mutation categories.

## Generic Mutations

Structural workflow transformations including:

- Step insertion
- Step deletion
- Adjacent swap
- Non-adjacent swap
- Prerequisite removal

These mutations explore workflow robustness without targeting specific vulnerabilities.

---

## Hypothesis-driven Mutations

Security-oriented mutations derived from explicit hypotheses.

Examples include:

- Checkout without authentication
- Unauthorized order history access
- Duplicate wallet top-up
- Missing prerequisite operations
- Authentication bypass attempts

Each hypothesis is evaluated independently against the baseline workflow.

---

# Current Evaluation Statistics

The current implementation executes the following experiments.

| Evaluation Group | Executions |
|------------------|-----------:|
| Baseline Workflows | 25 |
| Generic Mutations | 320 |
| Hypothesis Mutations | 25 |
| **Total Executions** | **370** |

All executions are fully reproducible using the provided evaluation scripts.

---

# Reproducibility

Every result presented in this repository is generated directly from the implementation.

No tables, figures, or metrics are manually edited.

The framework automatically produces:

- JSON reports
- aggregated summaries
- CSV tables
- LaTeX tables
- publication figures
- scientific metrics

Running the evaluation from scratch regenerates all experimental artifacts, ensuring complete reproducibility.

---