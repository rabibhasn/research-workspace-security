# Requirements Specification — Research Workspace Security

## 1. Project Scope

The Research Workspace is a small Python application that allows authenticated users to create, view, and process private research records. It uses three independently running services that communicate through HTTP interfaces.

The application uses synthetic data and seeded accounts. It is designed to investigate authentication, authorization across service boundaries, secure software composition, and automated security testing.

## 2. Functional Requirements

| ID | Requirement | Verification |
|---|---|---|
| FR-01 | The system shall authenticate seeded users using valid credentials. | Test valid and invalid login attempts. |
| FR-02 | The system shall issue time-limited authentication tokens after successful login. | Test token validity and expiration. |
| FR-03 | An ordinary user shall be able to create a research record associated with their identity. | Create a record and verify its owner. |
| FR-04 | An ordinary user shall be able to list and retrieve their own records. | Test successful access to owned records. |
| FR-05 | The system shall prevent ordinary users from accessing another user's records. | Attempt cross-user access using another user's record ID. |
| FR-06 | An authorized user shall be able to request processing of an accessible research record. | Submit a processing request and verify its result. |
| FR-07 | The Processing Service shall retrieve only records authorized for the requested job. | Test ownership enforcement across service boundaries. |
| FR-08 | The system shall associate each processing result with its authorized owner and job. | Test result ownership and retrieval. |
| FR-09 | The system shall prevent users from retrieving another user's processing results. | Attempt cross-user result retrieval. |
| FR-10 | An administrator shall be able to retrieve restricted aggregate system statistics. | Test administrator access and ordinary-user denial. |
| FR-11 | The Resource Service shall independently enforce authorization for protected resource operations. | Test direct service requests without valid authority. |
| FR-12 | The system shall reject missing, invalid, expired, or insufficient authorization credentials. | Run negative authentication and authorization tests. |

## 3. Non-Functional Requirements

| ID | Requirement | Verification |
|---|---|---|
| NFR-01 | The three application components shall run as separate processes. | Start each service independently and verify its HTTP interface. |
| NFR-02 | Components shall communicate through explicit service interfaces. | Inspect HTTP requests and service configuration. |
| NFR-03 | Services shall follow least privilege and receive only the authority needed for their responsibilities. | Review service credentials, permissions, and configuration. |
| NFR-04 | Authorization shall be enforced at the component that owns the protected resource. | Review Resource Service checks and related tests. |
| NFR-05 | Dependencies shall be explicitly declared and reproducibly installed. | Build in a fresh environment using the dependency manifest. |
| NFR-06 | The helper package shall be installed as a dependency rather than copied into the consuming service. | Inspect package structure and installation configuration. |
| NFR-07 | Automated tests and security analysis shall execute through Jenkins. | Inspect Jenkins build logs and archived reports. |
| NFR-08 | Defined security policy violations shall cause the CI pipeline to fail. | Introduce a controlled test violation and verify the gate decision. |
| NFR-09 | The application shall use synthetic data and seeded accounts for repeatable testing. | Run the seed procedure and verify expected test accounts. |
| NFR-10 | Security decisions and vulnerability experiments shall have traceable evidence. | Link requirements, commits, tests, reports, and gate results. |

## 4. Component Responsibilities

### Component 1 — Application API
- Authenticate seeded users and establish user identity.
- Validate token authenticity, validity period, and role.
- Coordinate requests to the Resource and Processing Services.
- Enforce restrictions on administrative operations.
- Return authorized results to clients.

### Component 2 — Resource Service
- Own and manage research records and processing results.
- Enforce record ownership and permissions on every protected operation.
- Validate service requests and their delegated authority.
- Restrict access to stored results by owner and job.

### Component 3 — Processing Service
- Accept authorized processing requests.
- Obtain only the record permitted for the requested job.
- Execute processing using the separately installed helper package.
- Submit results for storage under the appropriate ownership and job scope.
- Avoid accepting caller-supplied identities or resource IDs as proof of authorization.

## 5. Data Flow

1. A client submits credentials to the Application API.
2. The API authenticates the user and issues a time-limited token.
3. The client requests record creation, retrieval, or processing.
4. The API validates the token and forwards an appropriately scoped request to the relevant service.
5. The Resource Service verifies the authority and ownership required for the requested operation.
6. For processing, the Processing Service requests the authorized record, runs the helper package, and submits the result for storage.
7. The Resource Service enforces authorization when saving or retrieving results.
8. The API returns the result only after verifying that the requester is authorized to receive it.

## 6. Secure Design Principles

### Least Privilege
Each component shall receive only the permissions required for its tasks. Processing jobs shall be limited to their authorized records and outputs.

**Evidence:** Service permission review and tests for unauthorized record access.

### Complete Mediation
Every protected record, result, and administrative operation shall undergo an authorization check, including requests arriving from another internal service.

**Evidence:** Direct-service and cross-user authorization tests.

### Fail-Safe Defaults
The system shall deny access when credentials, ownership, job scope, or authorization cannot be established.

**Evidence:** Tests for missing tokens, invalid tokens, expired tokens, and unauthorized resource IDs.

## 7. Security Verification and Release Gates

The Jenkins pipeline shall:

1. Validate the project structure and declared dependencies.
2. Run Bandit static analysis and dependency vulnerability analysis.
3. Start a fresh test environment and execute functional and authorization tests.
4. Archive test results, analysis reports, and relevant logs.
5. Fail when defined security gates detect confirmed release-blocking violations.

The project shall document the selected catalog vulnerabilities, the additional composition vulnerability, their reproduction procedures, their impact, their remediation, and evidence that the final implementation enforces the required security guarantees.

## 8. Scope Limitations

The initial implementation excludes public registration, real payments, email delivery, graphical interfaces, and public production hosting. The application is an educational security prototype, not a production-ready service.

Production deployment would require additional review of secret management, transport security, service isolation, logging, monitoring, backup and recovery, rate limiting, and operational incident response.
