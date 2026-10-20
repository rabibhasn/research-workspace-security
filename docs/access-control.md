
# Access-Control Matrix — Research Workspace

## Roles
- Ordinary user: may access their own records and results.
- Administrator: may access the restricted system-statistics operation.
- Unauthenticated client: may access only the login endpoint.

## Permission Matrix

| Operation | Unauthenticated | Alice | Bob | Admin |
|---|---|---|---|---|
| Login | Allow | Allow | Allow | Allow |
| Create own record | Deny | Allow | Allow | Deny by default |
| List own records | Deny | Allow | Allow | Deny by default |
| Read own record | Deny | Allow | Allow | Deny by default |
| Read another user's record | Deny | Deny | Deny | Deny by default |
| Process own record | Deny | Allow | Allow | Deny by default |
| Retrieve own processing result | Deny | Allow | Allow | Deny by default |
| Retrieve another user's result | Deny | Deny | Deny | Deny by default |
| View system statistics | Deny | Deny | Deny | Allow |

## Enforcement Rules

1. Every protected request requires a valid authentication token.
2. The Application API verifies the user's identity, role and token expiry.
3. The Resource Service independently verifies the authority and ownership
   associated with every protected resource operation.
4. The Processing Service accepts only authorized job requests and limits
   each job to its permitted record and output.
5. Processing results are associated with their owner and job identifier.
6. Administrative operations require an explicit administrator role.
7. Missing, invalid, expired or ambiguous authority results in denial.
8. Resource IDs and job IDs are identifiers, not proof of permission.

## Test Evidence

- Alice can create and read Alice's records.
- Bob can create and read Bob's records.
- Alice cannot read, process or retrieve Bob's resources or results.
- Bob cannot read, process or retrieve Alice's resources or results.
- Ordinary users cannot access system statistics.
- Admin can access system statistics.
- Missing, invalid and expired tokens are rejected.
