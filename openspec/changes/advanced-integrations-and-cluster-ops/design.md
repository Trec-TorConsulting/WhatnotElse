## Context

This change finishes all remaining requirements from the master specification document (`openspec/project.md`), ensuring that WhatnotElse is complete from code to cluster orchestration.

## Goals / Non-Goals

**Goals:**
- Provide GraphQL client scaffolding for Whatnot Developer API.
- Provide Twilio SMS order notification sender.
- Provide Gemini-based auction price optimizer.
- Provide production-grade `site-init-job.yaml`, `mariadb-backup-cronjob.yaml`, and `pdb.yaml` in `k8s/`.
- Export standard user roles.

**Non-Goals:**
- Storing real Twilio or Whatnot production tokens in git (all secrets injected via Kubernetes Secret).
