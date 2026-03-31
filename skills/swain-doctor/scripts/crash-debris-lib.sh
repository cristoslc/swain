#!/usr/bin/env bash
# crash-debris-lib.sh — standalone crash debris detection functions (SPEC-182)
#
# Each function takes a project root path as $1 and prints findings
# to stdout as tab-separated lines: TYPE\tSTATUS\tDETAIL
#
# STATUS values: found, clean
# When STATUS=found, DETAIL contains human-readable description
#
# These functions are sourceable by both the pre-runtime script
# (SPEC-180) and swain-doctor (SPEC-192).

: # placeholder
