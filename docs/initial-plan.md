
# Initial SSDLC Plan — Research Workspace Security

## Phase 1: Requirements and Design

### Scope
Build a Python research workspace with three independently
running services. Authenticated users can create, view and
process private research records. An administrator can perform
an additional restricted operation.

### Assets
- A1: User credentials and authentication tokens
- A2: Private research records
- A3: Processing jobs and their results
- A4: Administrative privileges
- A5: Helper package and dependency integrity

### Trust boundaries
- TB1: Client to Application API
- TB2: Application API to Resource Service
- TB3: Application API to Processing Service
- TB4: Processing Service to Resource Service
- TB5: Processing Service to installed helper package

### Initial threats
- Forged, missing or expired authentication tokens
- Cross-user access to private records
- Unauthorized administrative operations
- Processing jobs accessing records outside their authority
- A compromised helper package accessing unauthorized data

### Initial controls
- Authenticate users and validate token expiry.
- Enforce resource ownership at the Resource Service.
- Check roles for privileged operations.
- Bind processing jobs and results to their authorized owner.
- Restrict service permissions and validate helper-package inputs.
- Run static analysis, dependency checks and automated tests.

### Secure design principles
1. Least privilege: each component receives only necessary permissions.
2. Complete mediation: check authorization for every protected operation.
3. Fail-safe defaults: deny access if identity or authority cannot be established.

## Phase 2: Implementation and Build

- Implement three separately running Python services.
- Define explicit HTTP interfaces between services.
- Create an installable helper package and declare the dependency.
- Use synthetic data and seed Alice, Bob and an administrator.
- Keep dependencies declared and builds reproducible.
- Reject unexpected dependencies or unapproved build artifacts.

## Phase 3: Testing and Security Verification

- Test at least three functional features.
- Test authentication, role restrictions and resource ownership.
- Select three vulnerabilities from the course catalog.
- Investigate one additional vulnerability caused by service composition.
- Record reproduction steps, impact, remediation and evidence.
- Run Bandit, dependency analysis and automated security tests.
- Require tests to pass and defined security gates to succeed.

## Phase 4: Release, Deployment and Operation

- Configure Jenkins for pushes and pull requests.
- Run validation, static analysis, dependency checks and tests.
- Archive test results and security reports.
- Fail builds when defined release-blocking policies are violated.
- Document remaining risks, deployment controls and production requirements.

## Evidence and Traceability

For each important threat, record the security requirement,
implementation decision, test or other evidence, and gate decision.

Preserve the Git history, architecture, data-flow diagram,
access-control matrix, STRIDE analysis, test results,
security reports and Jenkins logs.

The optional controlled supply-chain attack will be considered
after the core architecture and security tests work.
