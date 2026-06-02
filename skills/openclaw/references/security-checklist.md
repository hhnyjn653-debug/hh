# OpenClaw Security and Privacy Checklist

Use this checklist before enabling an OpenClaw compute federation across devices, operating systems, or trust domains.

## Identity and Trust

- [ ] Every user, service, worker node, task manifest, artifact, and result has a verifiable identity.
- [ ] Worker nodes use hardware-backed or platform-backed keys where available.
- [ ] Node enrollment requires owner approval and records owner, region, device type, operating system, mobile/desktop/server class, and allowed workload labels.
- [ ] Remote attestation is required for confidential or regulated workloads, or a documented compensating control is approved.
- [ ] Trust level is recomputed continuously from posture, patch level, behavior, and revocation status.

## Authorization and Policy

- [ ] Policy enforcement is deny-by-default.
- [ ] Scheduler cannot override policy decisions without a signed break-glass event.
- [ ] Tasks are authorized by requester, purpose, dataset, node trust level, data region, and capability.
- [ ] Credentials are short-lived and bound to the exact task, node, requester, and purpose.
- [ ] Sensitive workflows require explicit consent or an approved legal/business basis; mobile workflows require visible user opt-in and revocation.

## Data Privacy

- [ ] Data is classified before scheduling.
- [ ] Raw private data remains local unless policy explicitly allows transfer; phone-originated personal data defaults to local-only.
- [ ] Logs, metrics, traces, and error reports are scrubbed of secrets and private payloads.
- [ ] Federated learning or analytics uses secure aggregation and differential privacy when model updates can leak data.
- [ ] Scratch data is encrypted and destroyed through secure deletion or cryptographic erasure.
- [ ] Backups and retained artifacts follow the same data classification rules as primary data.

## Secure Transport and Storage

- [ ] Brain-to-node and node-to-node communication uses mTLS or an equivalent authenticated encrypted channel.
- [ ] Data at rest uses envelope encryption with centrally governed key rotation.
- [ ] Key material never appears in task manifests, logs, or environment dumps.
- [ ] Secrets are delivered by a secret broker with just-in-time access and audit logging.

## Worker Isolation

- [ ] Workers run in containers, microVMs, OS sandboxes, mobile app sandboxes, or another documented isolation boundary.
- [ ] Network egress is denied by default and opened only to approved destinations.
- [ ] File system access is restricted to declared input, output, and scratch paths.
- [ ] CPU, GPU, NPU, memory, disk, battery, thermal impact, and execution time are bounded.
- [ ] Privileged host access is forbidden unless specifically approved and logged; mobile sensors, contacts, photos, files, camera, microphone, and location require task-scoped permission and consent.

## Coordination Safety

- [ ] Multi-worker jobs have a signed coordination plan with explicit dependencies, barriers, leases, retries, aggregation rules, and rollback points.
- [ ] Partial results are verified before downstream workers can consume them.
- [ ] Worker-to-worker handoffs are coordinator-mediated by default, and any direct transfer is policy-approved and audited.
- [ ] Mobile, slow, or intermittent workers have backpressure, timeout, and replacement rules.
- [ ] Aggregation rules prevent one worker from learning another worker's private payload unless policy explicitly allows it.

## Integrity and Verification

- [ ] Task manifests are signed and include input hashes, allowed outputs, policy decision ID, and expiry.
- [ ] Results are signed by worker identity and include provenance metadata.
- [ ] High-integrity tasks use replay, quorum execution, deterministic validation, or statistical checks.
- [ ] Artifact hashes are verified before downstream use.

## Audit and Incident Response

- [ ] Policy decisions, dispatch events, node posture changes, credential issuance, and result collection are logged immutably.
- [ ] Audit records avoid private payloads and include enough metadata for investigation.
- [ ] Operators can revoke a node, requester, credential, dataset, or running task immediately.
- [ ] Incident runbooks cover compromised node, leaked credential, malicious task, policy bypass, and data exfiltration.
- [ ] Regular red-team and privacy review findings feed back into policy and scheduling rules.

## Release Gate

Do not launch or expand OpenClaw federation unless all critical checklist items are satisfied or an accountable owner signs a time-bounded exception with compensating controls.
