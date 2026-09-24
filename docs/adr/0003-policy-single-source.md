# ADR-0003 — Policy numbers live in the spec, mirrored into the code

**Status:** accepted

## Decision
Limits and fees are data in `specs/policy.yaml`. The lending domain loads a
vendored, byte-identical copy; `make mirror` fails when they differ.

## Why
The numbers are business decisions. Keeping them next to the rules that use
them means a policy change is reviewed as a spec change, and the code cannot
drift into "the real limit is whatever the constant says".
