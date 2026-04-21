"""External tests for swain-helm.

These tests run from outside the container and verify containerized services.
The UAT and E2E tests are in ../uat/ and ../e2e/ and can be run against
external containers using SWAIN_HELM_EXTERNAL_TEST=1.

Smoke tests (test_smoke.py) are defined here and always run externally.
"""
