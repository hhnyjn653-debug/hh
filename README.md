# hhwork

This repository contains an OpenClaw skill for designing a privacy-first compute federation and coordinated task execution across different devices, operating systems, phones/tablets, and trust domains.

## OpenClaw Skill

The skill lives in [`skills/openclaw`](skills/openclaw). It describes how an OpenClaw orchestration brain should safely discover compute nodes, verify trust, split work into minimal tasks, dispatch work across heterogeneous systems including mobile devices, coordinate workers during task operation, and verify partial and final results without centralizing private data unnecessarily.

Key materials:

- [`skills/openclaw/SKILL.md`](skills/openclaw/SKILL.md): main workflow and operating principles.
- [`skills/openclaw/references/security-checklist.md`](skills/openclaw/references/security-checklist.md): security, privacy, audit, and release-gate checklist.
- [`skills/openclaw/references/manifests.md`](skills/openclaw/references/manifests.md): node, task, and result manifest templates.

## Privacy Note

OpenClaw is designed to be privacy-first and fail-closed, but no real distributed system can honestly promise unconditional absolute privacy in every environment. The skill therefore requires explicit threat modeling, zero-trust controls, data minimization, encryption, sandboxing, auditability, and validation before deployment.
