# Microservice Incident Intelligence & Root Cause Analysis Platform

An explainable microservice incident analysis platform for identifying probable root-cause services in distributed microservice environments.

## Project Overview

Modern microservice applications consist of multiple interconnected services, where a failure in one service can propagate through dependent services and produce symptoms across the system. Identifying the originating failure from these downstream symptoms can therefore be challenging.

This project aims to develop a graph- and telemetry-based Root Cause Analysis (RCA) platform that analyzes service dependencies and multi-source observability data to identify and rank probable root-cause services during microservice incidents.

## Current Foundation

The project is currently being developed using the RCAEval benchmark as the primary evaluation environment.

Current project setup includes:

- Python virtual environment for isolated dependency management
- Structured project architecture for source code, tests, notebooks, and data
- RCAEval RE2 benchmark downloaded locally for experimentation and evaluation
- Git-based version control
- Initial data and application development environment

## Planned Core Components

- Telemetry ingestion and preprocessing
- Service dependency graph construction
- Temporal and anomaly-based incident analysis
- Root-cause candidate identification and ranking
- Explainable RCA results
- REST API for incident analysis
- Benchmark-based evaluation

## Technology Stack

- Python
- FastAPI
- Pandas
- NetworkX
- REST APIs
- RCAEval benchmark

## Dataset

The project uses the RCAEval RE2 benchmark for controlled microservice failure scenarios involving systems such as Online Boutique, Sock Shop, and Train Ticket.

The raw dataset is intentionally excluded from version control because of its size.

## Project Status

Actively under development.

The current repository contains the project foundation, development environment, dataset setup, and initial architecture. Core RCA functionality is being implemented incrementally.

## Planned Architecture

```text
Microservice Telemetry
        │
        ▼
Data Processing & Correlation
        │
        ▼
Service Dependency Graph
        │
        ▼
Incident / Anomaly Analysis
        │
        ▼
Root-Cause Candidate Ranking
        │
        ▼
Explainable RCA Result
        │
        ▼
REST API

### Important

This README is intentionally written as **"under development"**.

It doesn't falsely claim that the RCA engine, API, graph analysis, or evaluation results already exist. Once we implement each component, we'll update the README accordingly.

