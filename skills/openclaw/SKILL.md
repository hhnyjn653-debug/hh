---
name: openclaw
description: Privacy-first OpenClaw orchestration for linking and coordinating compute skills across different devices, operating systems, phones, tablets, and trust domains. Use when Codex needs to design, review, implement, or operate a cross-system compute federation where an OpenClaw control brain decomposes tasks, dispatches work to Windows, macOS, Linux, Android, iOS/iPadOS, mobile, edge, GPU, CPU, or cloud workers, and coordinates those workers through collaborative execution plans while enforcing privacy, zero-trust security, auditability, tenant isolation, and least-privilege execution.
---

# OpenClaw

## Mission

Build OpenClaw as a privacy-first orchestration brain that can discover trusted compute nodes, understand their capabilities, split work into safe tasks, dispatch those tasks across heterogeneous operating systems and devices, and coordinate the workers as a collaborative compute fabric for end-to-end task operation, including phones and tablets.

Treat privacy and safety as release blockers. Never claim a system is “absolutely safe” unless the claim is scoped to a formally proven property. Instead, design for zero-trust operation, measurable controls, red-team validation, and fail-closed behavior.

## Operating Principles

1. **Data minimization first**: move computation to data whenever possible; avoid moving private data to the scheduler.
2. **Zero trust by default**: authenticate every node, user, request, artifact, and result.
3. **Least privilege execution**: issue short-lived, task-scoped credentials and sandbox every worker.
4. **Local privacy boundary**: classify data before scheduling; keep secrets and sensitive datasets on approved nodes only.
5. **Encrypted everywhere**: require mutual TLS in transit and envelope encryption at rest.
6. **Human-governed risk**: require explicit review for new trust domains, privileged capabilities, or sensitive data flows.
7. **Fail closed**: deny work when identity, policy, attestation, consent, or logging is missing.

## Architecture Pattern

Use this model when designing or reviewing OpenClaw systems:

```text
User / App
  -> OpenClaw Brain: planning, policy checks, task graph, scheduling, coordination
  -> Policy & Trust Layer: identity, consent, authorization, data classification
  -> Capability Registry: OS, hardware, accelerators, mobile posture, installed skills, health
  -> Coordination Engine: dependencies, barriers, leases, retries, quorum, progress
  -> Secure Dispatch: signed task manifests, mTLS, short-lived credentials
  -> Worker Nodes: sandboxed executors on different systems/devices, including mobile agents
  -> Result Verifier: partial-result validation, aggregation, provenance, reproducibility sampling
  -> Audit Ledger: immutable security, privacy, and execution evidence
```

Keep the OpenClaw Brain as a coordinator, not a data hoarder. It should store metadata, policies, task plans, and audit records; private payloads should remain encrypted or local unless policy explicitly allows transfer.

## Workflow

### 1. Classify the request

Before planning work, identify:

- data sensitivity: public, internal, confidential, regulated, secret
- compute requirements: CPU, GPU, NPU, RAM, storage, battery, network, OS, mobile permission set, skill/runtime
- trust boundary: same owner, same org, partner, public cloud, untrusted edge
- privacy mode: local-only, federated, encrypted payload, synthetic/sample data
- verification requirement: deterministic replay, quorum results, partial-result checksums, signed outputs

If the request touches confidential, regulated, biometric, medical, financial, credentials, or personal data, select the strictest privacy mode unless the user provides an approved policy.

### 2. Discover and attest nodes

Accept a node only when it provides:

- stable node identity with hardware- or platform-backed keys when available
- OS, runtime, accelerator, network, battery/charging state for mobile, and skill capability manifest
- security posture: patch level, sandbox support, disk encryption, EDR/AV state where applicable
- remote attestation or compensating controls for high-risk workloads
- owner, region, data residency, device class, and allowed workload labels

Reject or quarantine nodes with stale posture, unknown owner, missing identity, or policy conflicts.

### 3. Build a safe task graph

Split work into minimal, independent tasks. For each task, define:

- allowed input sources and output destinations
- required capabilities and forbidden capabilities
- maximum data sensitivity the worker may access
- sandbox profile and resource limits
- network egress policy
- credential scope and lifetime
- verification method
- coordination contract: dependencies, ordering, synchronization barriers, merge strategy, timeout, retry policy, and rollback behavior

Never give a worker broad access “because it is convenient.”

### 4. Coordinate collaborative execution

OpenClaw must not only pool compute; it must actively coordinate workers so the full task operates correctly. For each workflow, define:

- task graph dependencies and which workers can run in parallel
- synchronization barriers where partial outputs must be verified before downstream tasks start
- leases and heartbeats so stalled workers can be retried or replaced safely
- partial-result aggregation rules, including merge order, conflict resolution, and quorum thresholds
- backpressure rules for slow, mobile, battery-limited, or intermittently connected nodes
- checkpoint and rollback points for multi-step jobs
- handoff contracts that prevent one worker from seeing another worker's private data unless policy allows it

Prefer coordinator-mediated handoffs over direct worker-to-worker sharing. If direct collaboration is required, authorize it explicitly in policy and record it in the audit ledger.

### 5. Enforce policy before dispatch

Block dispatch unless all conditions pass:

- authenticated requester
- authorized purpose and consent where required
- approved data classification and locality
- compatible node trust level
- valid task signature
- available audit sink
- secrets available only through scoped secret broker

### 6. Execute with containment

Prefer containers, microVMs, OS sandboxes, mobile app sandboxes, or process isolation depending on platform. Always enforce:

- read-only task bundle when possible
- no ambient credentials
- bounded CPU/GPU/NPU/memory/battery/time quotas
- deny-by-default network egress
- encrypted scratch storage
- secure deletion or cryptographic erasure after completion

### 7. Verify results and provenance

Require workers to return:

- signed result envelope
- partial-result status for coordinated workflows
- input/output hashes or content-addressed references
- execution logs stripped of private payloads
- runtime and skill versions
- policy decision identifier

For high-integrity work, use replay, quorum execution, deterministic checks, or statistical validation. For collaborative workflows, verify each partial result before aggregation and verify the final merged result against the coordination plan.

## Mobile Node Requirements

Phones and tablets are first-class OpenClaw worker nodes, but schedule them conservatively because they are personal, battery-powered, frequently offline, and permission-constrained. Support Android and iOS/iPadOS through a dedicated mobile agent that:

- requires explicit user enrollment and visible opt-in/opt-out controls
- runs only approved skills inside the mobile OS app sandbox
- respects battery, charging, thermal, foreground/background, metered-network, and roaming policies
- declares CPU, GPU, NPU/Neural Engine, memory, storage, camera/microphone/location permissions, and supported runtimes
- forbids access to contacts, photos, location, microphone, camera, notifications, or local files unless the task manifest explicitly authorizes that permission and the user has consented
- defaults to local-only execution for personal data generated or stored on the phone
- pauses or revokes work immediately when the user disables the agent, the device locks if policy requires it, posture becomes stale, or network conditions violate policy

Never treat mobile devices as always-available servers. Use them for privacy-preserving local tasks, on-device inference, sensor-local processing with consent, opportunistic compute while charging, or federated learning/analytics that keeps raw mobile data on-device.

## Privacy Modes

Choose the strongest mode compatible with the task:

| Mode | Use when | Key controls |
| --- | --- | --- |
| Local-only | Private data must not leave one device/system | schedule only to owner-approved local node; no network egress |
| Federated compute | Multiple nodes train/analyze without sharing raw data | local processing, secure aggregation, differential privacy if needed |
| Encrypted payload | Data may move but must remain encrypted outside approved runtime | envelope encryption, KMS/HSM, attested runtime, no plaintext logs |
| Sanitized sample | Development/debugging | synthetic or redacted inputs only, no secrets |
| Public compute | Public data and non-sensitive outputs | standard auth, integrity, and cost controls |

## Security Checklist

Use `references/security-checklist.md` for detailed acceptance checks. At minimum, ensure:

- mTLS or equivalent node-to-brain authentication
- signed node capability manifests and signed task manifests
- policy engine that is independent from scheduler convenience logic
- short-lived credentials bound to task, node, requester, and purpose
- encrypted logs with private payload redaction
- worker sandboxing with deny-by-default network policy
- coordination plans with dependency barriers, retries, rollback points, and partial-result verification
- immutable audit trail for policy decisions, dispatch, execution, and result collection
- incident kill switch to revoke nodes, credentials, and running tasks

## Output Expectations

When helping with OpenClaw, produce:

- architecture diagrams, task flows, and coordination plans when relevant
- explicit trust boundaries and data-flow descriptions
- a node capability manifest shape
- a task manifest shape
- a coordination strategy for dependencies, parallelism, aggregation, retries, and rollback
- policy decisions and failure modes
- privacy and security checklist results
- concrete implementation steps for the target OS/device mix, including Android and iOS/iPadOS where relevant

Do not output designs that centralize private data in the OpenClaw Brain unless the user explicitly asks and the design includes a risk warning and compensating controls.
