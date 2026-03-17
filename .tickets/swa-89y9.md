---
id: swa-89y9
status: closed
deps: []
links: []
created: 2026-03-17T18:11:24Z
type: task
priority: 1
assignee: cristos
parent: swa-vc4x
tags: [spec:SPEC-061]
---
# RED: Write tests for tracked .env file detection

Test git ls-files detection of tracked .env files, excluding .env.example.


## Notes

**2026-03-17T18:14:43Z**

RED complete: 10 tests for tracked .env detection written in test_doctor_security.py (TestTrackedEnvDetection class). Covers: .env, .env.local, .env.production detection; .env.example exclusion; empty list for clean repos; non-git directory graceful handling; WARN diagnostic severity; remediation guidance in message. All fail with ModuleNotFoundError.
