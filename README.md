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
---

# Framework Modules

HERMES is implemented as a collection of independent research modules. Each module performs a well-defined task in the workflow fuzzing pipeline and communicates through structured intermediate artifacts.

This modular architecture simplifies experimentation, extension, and comparative evaluation.

---

# 1. Crawler

## Purpose

The crawler explores the target web application and discovers navigable pages, forms, and workflow entry points.

Rather than performing random exploration, the crawler records information useful for later semantic reasoning.

### Responsibilities

- Discover reachable pages
- Enumerate links
- Detect interactive elements
- Capture forms
- Record navigation paths
- Produce crawler reports

### Output

The crawler generates structured observations that become the input for state graph construction.

---

# 2. State Graph Builder

## Purpose

The state graph builder converts crawler observations into a directed graph representing application states and transitions.

Each node represents an application state.

Each edge represents an executable workflow transition.

### Responsibilities

- Build directed graph
- Remove duplicate states
- Connect transitions
- Preserve navigation order
- Export graph representation

### Output

A reusable workflow graph describing the application's navigational structure.

---

# 3. Semantic Discovery

## Purpose

URLs alone do not describe business behavior.

Semantic Discovery identifies meaningful operations by analyzing page content, actions, and navigation context.

Instead of producing:

```
GET /checkout
```

HERMES identifies:

```
Checkout
```

Likewise,

```
POST /login
```

becomes

```
User Authentication
```

### Example Operations

- Login
- Logout
- Checkout
- Wallet Top-up
- View Orders
- View Profile
- Product Browsing
- Cart Management

---

# 4. Workflow Generator

## Purpose

The workflow generator combines semantic operations into executable business workflows.

Example workflow:

```
Login

↓

Browse Products

↓

Add Item

↓

Checkout

↓

View Orders
```

These workflows become the baseline used during scientific evaluation.

### Responsibilities

- Generate workflows
- Remove duplicates
- Preserve prerequisites
- Validate execution order
- Export workflow definitions

---

# 5. Workflow Prioritization

## Purpose

Large applications may contain hundreds of workflows.

Executing every workflow is inefficient.

The prioritization engine ranks workflows according to execution value.

Example ranking criteria include:

- workflow length
- state transitions
- semantic diversity
- operation uniqueness
- execution cost

Higher-ranked workflows are evaluated first.

---

# 6. Generic Mutation Engine

## Purpose

The generic mutation engine creates structural variations of baseline workflows.

These mutations intentionally modify workflow structure while preserving executable semantics whenever possible.

Current mutation strategies include:

### Step Removal

Removes one workflow operation.

Example

```
Login

↓

Checkout
```

↓

```
Checkout
```

---

### Step Insertion

Adds a workflow operation.

Example

```
Login

↓

Checkout
```

↓

```
Login

↓

Logout

↓

Checkout
```

---

### Adjacent Swap

Swaps neighboring workflow steps.

---

### Non-Adjacent Swap

Reorders distant workflow operations.

---

### Prerequisite Removal

Removes operations that establish required state.

Example

```
Wallet Top-up

↓

Checkout
```

↓

```
Checkout
```

These mutations are useful for robustness analysis.

---

# 7. Hypothesis-driven Mutation Engine

## Purpose

Unlike generic mutations, hypothesis mutations target specific business logic assumptions.

Each mutation represents a concrete research hypothesis.

Examples include:

### H001

Checkout succeeds without authentication.

---

### H002

Wallet balance can be duplicated.

---

### H003

Order history is accessible without login.

---

Each hypothesis is executed independently and compared against the baseline workflow.

---

# 8. Execution Engine

## Purpose

The execution engine performs automated workflow execution using Playwright.

Each workflow is executed multiple times to reduce non-deterministic effects.

Execution metadata includes:

- duration
- success status
- failures
- completed steps
- execution logs

The engine exports structured JSON reports for every workflow execution.

---

# 9. Behavior Comparator

## Purpose

The comparator evaluates behavioral differences between baseline and mutated executions.

Comparison dimensions include:

- workflow success
- execution time
- state divergence
- semantic outcome
- anomaly detection

The comparator determines whether the observed behavior supports or rejects the evaluated hypothesis.

---

# 10. Scientific Evaluation Pipeline

## Purpose

The evaluation pipeline aggregates all execution results into publication-ready artifacts.

Automatically generated outputs include:

- JSON reports
- experiment summaries
- workflow statistics
- mutation summaries
- CSV tables
- LaTeX tables
- publication figures

No manual processing is required.

---

# End-to-End Pipeline

The complete framework operates according to the following sequence.

```
Crawler
      │
      ▼
State Graph Builder
      │
      ▼
Semantic Discovery
      │
      ▼
Workflow Generation
      │
      ▼
Workflow Prioritization
      │
      ▼
Generic Mutation Engine
      │
      ▼
Hypothesis Mutation Engine
      │
      ▼
Playwright Execution
      │
      ▼
Behavior Comparator
      │
      ▼
Scientific Evaluation
      │
      ▼
Tables • Figures • Reports
```

---

# Design Principles

The framework was developed according to the following principles.

- Modular implementation
- Reproducible experiments
- Fully automated evaluation
- Publication-ready outputs
- Framework extensibility
- Separation of benchmark and framework
- Independent module testing
- Research-oriented architecture

These principles enable HERMES to serve both as a research artifact and as a foundation for future workflow fuzzing studies.

---
---

# Scientific Evaluation

The HERMES evaluation pipeline is designed to provide a fully reproducible assessment of workflow fuzzing effectiveness.

Every experiment follows the same sequence:

1. Execute baseline workflows.
2. Generate workflow mutations.
3. Execute mutated workflows.
4. Compare behavioral outcomes.
5. Aggregate execution statistics.
6. Generate publication artifacts.

No manual intervention is required after the evaluation begins.

---

# Evaluation Workflow

```
Baseline Workflow
        │
        ▼
Execute Baseline
        │
        ▼
Generate Mutations
        │
        ▼
Execute Mutations
        │
        ▼
Behavior Comparison
        │
        ▼
Anomaly Detection
        │
        ▼
Metric Aggregation
        │
        ▼
Tables and Figures
```

---

# Baseline Evaluation

Baseline workflows represent the expected behavior of the application.

Each workflow is executed multiple times to establish consistent reference behavior.

Typical baseline workflows include:

- Login
- Wallet Top-up
- Checkout
- View Orders
- Logout

The baseline execution establishes:

- expected success status
- expected workflow duration
- expected state transitions
- expected business outcome

All mutations are compared against this baseline.

---

# Generic Mutation Evaluation

Generic mutations modify workflow structure without targeting a specific vulnerability.

Examples include:

- Removing workflow steps
- Swapping workflow steps
- Inserting additional operations
- Removing prerequisite actions

These mutations evaluate the robustness of workflow execution under structural changes.

---

# Hypothesis-driven Evaluation

Hypothesis-driven mutations are designed to test explicit security assumptions.

Current hypotheses include:

| ID | Security Hypothesis |
|----|---------------------|
| H001 | Checkout should require authentication |
| H002 | Wallet credit should not be duplicated |
| H003 | Order history should require authentication |

Each hypothesis is executed independently and compared against the corresponding baseline workflow.

---

# Behavioral Comparison

After execution, baseline and mutated workflows are compared.

Comparison dimensions include:

| Metric | Description |
|---------|-------------|
| Success Status | Did both executions complete successfully? |
| Execution Duration | Was there a significant runtime difference? |
| Completed Steps | Were workflow steps skipped or added? |
| State Transition | Did navigation diverge from baseline? |
| Final Outcome | Did the business result change? |

Behavioral divergence may indicate a business logic anomaly.

---

# Ground Truth Validation

HERMES supports evaluation against a manually verified ground-truth dataset.

Ground truth enables measurement of anomaly detection quality using standard information retrieval metrics.

The framework reports:

- True Positives
- False Positives
- True Negatives
- False Negatives

From these values it computes:

- Precision
- Recall
- F1-score
- Accuracy

This enables objective comparison between workflow mutation strategies.

---

# Generated Evaluation Artifacts

A complete execution produces several categories of artifacts.

## Raw Reports

```
evaluation/raw/
```

Contains one JSON report for every workflow execution.

---

## Aggregated Reports

```
evaluation/aggregated/
```

Contains merged summaries and statistical outputs.

---

## CSV Tables

```
evaluation/tables/csv/
```

Spreadsheet-compatible experimental results.

---

## LaTeX Tables

```
evaluation/tables/latex/
```

Publication-ready tables for academic papers.

---

## Publication Figures

```
evaluation/figures/
```

Automatically generated visualizations suitable for inclusion in conference and journal publications.

---

# Reproducibility

Every artifact produced by HERMES is automatically regenerated from source code.

Running the evaluation pipeline again reproduces:

- Raw execution reports
- Statistical summaries
- CSV tables
- LaTeX tables
- Publication figures

No values are manually edited after execution.

This design ensures complete experimental reproducibility.

---

# Experimental Summary

The current evaluation consists of:

| Evaluation Category | Executions |
|---------------------|-----------:|
| Baseline Workflows | 25 |
| Generic Mutations | 320 |
| Hypothesis Mutations | 25 |
| **Total Workflow Executions** | **370** |

All executions were generated automatically by the HERMES evaluation framework.

---

# Research Significance

Traditional web fuzzers primarily mutate requests and input values.

HERMES extends this paradigm by mutating **workflow history** while preserving semantic intent.

This enables exploration of business logic vulnerabilities that depend on application state rather than isolated inputs.

The resulting framework provides a foundation for future research in:

- Stateful Web Fuzzing
- Business Logic Testing
- Workflow Mutation
- Semantic Software Testing
- Autonomous Security Evaluation

---
