# Threat Model — Research Workspace

## 1. Purpose and scope

This threat model identifies security risks in the Research Workspace application before feature implementation. The application allows users to create research records, process their own records, retrieve processing results, and allow an administrator to view aggregate system statistics.

The system uses three independent Python services that communicate through explicit HTTP interfaces.

## 2. Architecture and trust boundaries

### Components

1. **Application API — Port 5000**
   - Authenticates users.
   - Issues and validates time-limited authentication tokens.
   - Enforces application-level role and access rules.
   - Coordinates requests to the other services.

2. **Resource Service — Port 5001**
   - Owns research records and processing results.
   - Checks authentication, record ownership, and permissions independently.
   - Rejects unauthorized requests even if the Application API is bypassed.

3. **Processing Service — Port 5002**
   - Processes records when an authorized request is received.
   - Uses a separately installable helper package.
   - Requests record access and result storage through the Resource Service interface.

### Data-flow diagram

```text
                 Untrusted client
                       |
                       | HTTPS in deployment
                       | Login / API requests
                       v
              +--------------------+
              |  Application API   |
              |     Port 5000      |
              | Authentication     |
              | Role checks        |
              +--------------------+
                   |           |
        Authorized |           | Admin statistics
        processing |           | request
        request    |           |
                   v           v
          +----------------+  +----------------+
          |   Processing   |  |    Resource    |
          |    Service     |  |    Service     |
          |    Port 5002   |  |    Port 5001   |
          |                |  | Record storage |
          | Helper package |  | Ownership and  |
          +----------------+  | access checks  |
                   |          +----------------+
                   |                  ^
                   | Fetch authorized |
                   | record / save result
                   +------------------+
```

The diagram represents logical communication paths. The actual implementation must define the exact HTTP endpoints and request formats.

### Trust boundaries

- **TB1 — Client to Application API:** Client input and supplied credentials are untrusted.
- **TB2 — Application API to internal services:** Requests must not be trusted solely because they originate from another service.
- **TB3 — Processing Service to Resource Service:** Record retrieval and result storage require authorization and validation.
- **TB4 — Service to stored data:** Records and results must remain associated with the correct owner and processing job.
- **TB5 — Application to helper dependency:** The helper package is a separate dependency and must be installed from a declared, controlled source.

## 3. Assets and security objectives

| Asset | Security objective | Main risk |
|---|---|---|
| User credentials | Confidentiality | Credential disclosure |
| Authentication tokens | Confidentiality and integrity | Token theft or forgery |
| User identities and roles | Integrity | Privilege escalation |
| Research records | Confidentiality and integrity | Unauthorized access or modification |
| Processing results | Confidentiality and integrity | Cross-user result disclosure |
| Administrator statistics | Restricted access | Unauthorized administrative access |
| Helper package | Integrity | Malicious or altered dependency |
| Test and security reports | Integrity and availability | Missing or misleading CI evidence |

## 4. STRIDE threat analysis

STRIDE categorizes threats as Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, and Elevation of Privilege.

| Threat category | Example threat | Affected component or asset | Planned mitigation |
|---|---|---|---|
| Spoofing | An attacker uses another user's identity or a forged token. | Application API, tokens | Validate token authenticity, expiry, and identity on every protected request. |
| Tampering | A user changes a record ID, owner ID, or processing parameters to manipulate another user's data. | Resource Service, records | Validate input and ownership; do not trust client-supplied owner IDs. |
| Repudiation | A user denies submitting a processing request or an administrator denies accessing statistics. | All services | Record security-relevant events with timestamps, actor identity, operation, and outcome; avoid logging passwords or tokens. |
| Information Disclosure | Alice retrieves Bob's records or results by guessing an identifier. | Resource Service, records and results | Enforce ownership checks at the Resource Service and test cross-user access attempts. |
| Denial of Service | Repeated expensive processing requests exhaust server resources. | Processing Service | Apply request limits, input-size limits, processing timeouts, and controlled error handling. |
| Elevation of Privilege | An ordinary user calls an administrator-only endpoint or bypasses API role checks. | Application API, Resource Service | Enforce role checks server-side and deny by default; protect internal interfaces independently. |

These are planned controls. Their effectiveness must be verified through implementation and tests rather than assumed.

## 5. Initial abuse cases

### UC-01 — Access another user's record

**Attacker goal:** Read a record belonging to another user.

**Attack path:** Alice authenticates, guesses or obtains Bob's record ID, and requests that record.

**Expected result:** The Resource Service rejects the request because Alice is not the record owner. Knowing an identifier is not sufficient authority.

**Evidence:** A functional authorization test verifies that Alice cannot retrieve Bob's record.

### UC-02 — Retrieve another user's processing result

**Attacker goal:** Read a result associated with another user's record.

**Attack path:** Alice submits a guessed result or job ID.

**Expected result:** The service verifies the association between the authenticated user, the source record, and the result. Unauthorized access is denied.

**Evidence:** A test verifies that Alice cannot retrieve Bob's result.

### UC-03 — Bypass administrator authorization

**Attacker goal:** View aggregate system statistics without administrator privileges.

**Attack path:** An ordinary user directly calls the administrator endpoint.

**Expected result:** The request is denied regardless of whether the user uses the normal interface.

**Evidence:** An authorization test confirms that an ordinary user receives a denial response.

### UC-04 — Abuse a service boundary

**Attacker goal:** Bypass Application API checks by contacting an internal service directly.

**Attack path:** An attacker sends a request directly to the Resource Service or Processing Service without valid authority.

**Expected result:** Internal services independently validate the authority required for their operation and reject unauthorized requests.

**Evidence:** Integration tests call internal interfaces with missing, invalid, or insufficient authorization.

## 6. Security design principles

### Least privilege

Each service and role receives only the permissions needed for its responsibilities. Ordinary users can access their own records and results. Administrator access is limited to the defined administrative operation. Service credentials and permissions must also be restricted.

### Complete mediation

Every protected operation is checked whenever access is requested. The Resource Service verifies ownership itself instead of relying exclusively on the Application API. Processing and result retrieval also require authorization checks.

### Fail-safe defaults

Requests are denied when identity, ownership, role, or authorization cannot be established. Missing, invalid, expired, or insufficient credentials must not grant access. Errors must not disclose sensitive record contents or credentials.

## 7. Verification plan

The following evidence will be collected during implementation and testing:

- Successful login for seeded ordinary and administrator accounts.
- Denial of missing, invalid, and expired authentication tokens.
- Successful access to a user's own records and processing results.
- Denial of cross-user record and result access.
- Denial of administrator operations to ordinary users.
- Denial of unauthorized direct requests to internal services.
- Static-analysis and dependency-analysis results in Jenkins.
- Saved functional and authorization test reports.
- CI gate failure when a defined security blocker is detected.

## 8. Assumptions and limitations

The application will use synthetic records and seeded test accounts. The initial prototype is intended for a controlled development and demonstration environment, not immediate public deployment.

HTTPS is required for production deployment. A local prototype may use HTTP between local services during development, but this does not provide transport confidentiality. Production deployment also requires secure secret management, restricted service exposure, dependency pinning and verification, appropriate logging, and operational monitoring.

The exact vulnerabilities intentionally introduced for the assignment will be documented separately in the implementation and final report. Each must be mapped to the relevant threat, test, and remediation. This threat model describes expected protections; it does not claim that those protections have already been implemented or tested.
