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