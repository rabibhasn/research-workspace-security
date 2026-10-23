# Research Workspace Security

A multi-service Python application developed for **Software Security Assignment I** at Aarhus University. The project demonstrates common application security vulnerabilities, secure remediation techniques, automated testing, and security checks integrated into a Jenkins CI pipeline.

## Project Overview

The Research Workspace API allows authenticated users to create and access research records and request text processing. The application is divided into three Flask services and a reusable Python helper package.

The project uses two Git branches to demonstrate the security lifecycle:

- `main` — vulnerable baseline containing intentionally introduced security weaknesses.
- `fix/security-remediation` — implementation of security improvements and corresponding security tests.

This separation allows the vulnerable and remediated implementations to be compared through source code, test results, and automated security analysis.

## Architecture

| Component | Port | Responsibility |
|---|---:|---|
| API Service | 5000 | User authentication, bearer tokens, API endpoints, and service coordination |
| Resource Service | 5001 | Research record management, ownership checks, and administrative authorization |
| Processing Service | 5002 | Text processing and processing-result generation |
| Helper Package | N/A | Reusable Python text-processing functionality |

### Request Flow

1. A user authenticates through the API Service.
2. The API validates the user's credentials and issues a bearer token.
3. The API communicates with the Resource Service using internal service credentials and signed user context.
4. The Resource Service validates the request and enforces record ownership and authorization rules.
5. When processing is requested, the relevant record content is sent to the Processing Service.
6. The processing result is returned through the API Service.

## Security Objectives

The project focuses on the following security objectives:

- Authentication and secure password handling.
- Authorization and user-specific record ownership.
- Protection against insecure direct object references (IDOR/BOLA).
- Validation of identity and role information across service boundaries.
- Secure configuration of internal service credentials.
- Automated security testing and dependency auditing.
- Repeatable security checks through Jenkins.

## Vulnerabilities and Remediation

The vulnerable baseline contains five documented categories of security weaknesses.

| Vulnerability | Remediation |
|---|---|
| Hardcoded demonstration passwords | SQLite-backed user database and salted password hashing using `hashlib.scrypt` |
| Fallback internal service credentials | Require security-sensitive configuration through environment variables |
| Unauthorized ownership assignment | Derive record ownership from verified user context |
| Insecure direct object reference (IDOR/BOLA) | Enforce ownership checks before returning protected records |
| Unverified identity and role claims | Verify HMAC-signed user context before trusting identity information |

The remediation applies three principal security design principles:

- **Least privilege:** users receive access only to resources they are authorized to use.
- **Complete mediation:** authorization is checked when protected resources are accessed.
- **Fail-secure defaults:** missing or invalid security credentials result in rejection rather than permissive fallback behavior.

## Technology Stack

- Python
- Flask
- SQLite
- HTTP-based service communication
- `hashlib.scrypt` for password hashing
- HMAC-SHA256 for signed user context
- `pytest` for automated tests
- Bandit for Python static security analysis
- `pip-audit` for dependency vulnerability auditing
- OWASP ZAP for dynamic security testing
- Git and GitHub for version control
- Jenkins for continuous integration

## Project Structure

```text
research-workspace-security/
├── api_service/
│   ├── app.py
│   ├── database.py
│   └── init_db.py
├── resource_service/
│   └── app.py
├── processing_service/
│   └── app.py
├── helper_package/
│   └── research_helper/
│       ├── __init__.py
│       └── processor.py
├── tests/
│   ├── test_processor.py
│   └── test_resource_service.py
├── docs/
│   └── initial-plan.md
├── reports/
├── Jenkinsfile
└── README.md
```

The exact contents of documentation, test, and report directories may vary as the project evolves.

## Setup and Installation

### Prerequisites

Install the following software before running the project:

- Python 3.12 or another Python version supported by the project's dependencies.
- Git.
- PowerShell or another terminal.
- Jenkins, if running the CI pipeline locally.

The project has been developed and tested in a Windows environment. Confirm the Python version and dependency compatibility before using a different runtime.

### 1. Clone the Repository

```powershell
git clone https://github.com/rabibhasn/research-workspace-security.git
cd research-workspace-security
```

### 2. Select the Implementation

To inspect the vulnerable baseline:

```powershell
git switch main
```

To use the remediated implementation:

```powershell
git switch fix/security-remediation
```

### 3. Create a Virtual Environment

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell prevents activation, use the Python executable directly from the virtual environment.

### 4. Install Dependencies

Install the project's declared dependencies and the local helper package:

```powershell
python -m pip install -r requirements.txt
python -m pip install -e ./helper_package
```

Run these commands from the repository root. If the selected branch uses a different dependency file or package configuration, follow that branch's configuration.

### 5. Configure Security Secrets

Set the environment variables required by the selected services before starting them. The remediated implementation requires the relevant internal service credentials and user-context signing secret to be configured.

Do not commit real passwords, tokens, signing keys, or `.env` files to Git. Use the variable names expected by the service configuration and generate suitable secret values for local testing.

### 6. Initialize the User Database

On the remediated branch, initialize the user database using:

```powershell
python -m api_service.init_db
```

Follow the prompts to create the demonstration users and their passwords.

## Running the Services

Start each service in a separate terminal after activating the virtual environment and configuring the required environment variables.

| Service | Command | Port |
|---|---|---:|
| API Service | `python api_service/app.py` | 5000 |
| Resource Service | `python resource_service/app.py` | 5001 |
| Processing Service | `python processing_service/app.py` | 5002 |

Start the Resource and Processing Services before sending requests through the API Service. Ensure the service URLs and internal credentials match the configuration used by each component.

For local testing, the API Service is expected to be reachable at `http://127.0.0.1:5000`.

## Testing

The project includes automated tests for processing functionality and security-sensitive Resource Service behavior.

Run the test suite from the repository root:

```powershell
python -m pytest -v
```

The tests cover:

- Processing research text and calculating word and character counts.
- Allowing access to a user's own record.
- Rejecting access to another user's record.
- Rejecting requests without valid internal service credentials.
- Preventing unauthorized ownership assignment.
- Rejecting unsigned identity claims that attempt to assert administrator authority.

A previous remediation test run completed with **6 passing tests**. Run the tests again on the current checkout to verify its actual state.

## Security Analysis

### Bandit — Static Application Security Testing

Bandit analyzes Python source code for potentially insecure coding patterns.

Run Bandit against the Python services and helper package:

```powershell
python -m bandit -r api_service resource_service processing_service helper_package -f json -o reports/bandit-report.json
```

The JSON report can be reviewed to identify findings by severity, confidence, file, and location. A clean report means that Bandit did not identify findings covered by its configured checks; it does not prove the absence of all vulnerabilities.

### pip-audit — Dependency Security

Use `pip-audit` to check installed Python dependencies against known vulnerability data:

```powershell
python -m pip_audit
```

## Jenkins Continuous Integration

The project includes a `Jenkinsfile` for automated security and quality checks.

The intended CI workflow includes:

1. Checking out the selected Git branch.
2. Setting up the Python environment and dependencies.
3. Installing the local helper package.
4. Running the automated test suite.
5. Running Bandit static security analysis.
6. Running `pip-audit` for dependency vulnerability checks.
7. Saving security reports as build artifacts where configured.




