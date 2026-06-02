# OpenClaw Manifest Templates

These templates describe the minimum fields OpenClaw should use to safely connect heterogeneous compute nodes, including phones and tablets, dispatch work, and coordinate collaborative task execution.

## Node Capability Manifest

```yaml
api_version: openclaw.io/v1
kind: NodeCapability
node_id: node-01
owner: team-or-person
region: us-east-1
trust_level: trusted-local
platform:
  os: android
  os_version: "15"
  architecture: arm64
  device_class: phone
  sandbox: [mobile-app-sandbox]
hardware:
  cpu_cores: 8
  memory_gb: 8
  accelerators:
    - type: npu
      vendor: mobile-soc-vendor
      model: example-neural-engine
mobile:
  battery_policy: charging-only
  min_battery_percent: 60
  network_policy: unmetered-only
  permissions_allowed: []
  user_consent_required: true
skills:
  - name: image-render
    version: 1.2.0
  - name: data-transform
    version: 0.5.1
posture:
  disk_encryption: true
  patch_state: current
  remote_attestation: available
labels:
  data_residency: [us]
  allowed_sensitivity: [public, internal, confidential]
  network_zone: private
signature:
  algorithm: ed25519
  value: signed-manifest-placeholder
```

## Coordination Plan Manifest

```yaml
api_version: openclaw.io/v1
kind: CoordinationPlan
request_id: req-123
graph:
  tasks:
    - id: preprocess
      required_skills: [data-transform]
      can_run_on: [linux, macos, windows, android, ios, ipados]
    - id: infer
      depends_on: [preprocess]
      required_skills: [on-device-inference]
    - id: aggregate
      depends_on: [infer]
      required_skills: [secure-aggregate]
synchronization:
  barriers:
    - after: preprocess
      verify: hash-and-signature
    - after: infer
      verify: quorum-or-replay
aggregation:
  strategy: secure-merge
  conflict_resolution: policy-defined
  quorum: 2-of-3
resilience:
  heartbeat_interval: 30s
  lease_ttl: 2m
  retry_policy: replace-stalled-worker
  rollback_points: [preprocess]
privacy:
  direct_worker_to_worker_transfer: false
  coordinator_mediated_handoff: true
signature:
  algorithm: ed25519
  value: signed-coordination-plan-placeholder
```

## Task Manifest

```yaml
api_version: openclaw.io/v1
kind: Task
request_id: req-123
policy_decision_id: pdp-456
coordination_plan_id: plan-123
purpose: approved-purpose
required_capabilities:
  os: [linux, macos, windows, android, ios, ipados]
  skills:
    - name: data-transform
      version_constraint: ">=0.5.0"
privacy:
  data_classification: confidential
  mode: local-only
  allowed_regions: [us]
inputs:
  - ref: dataset://local/private-dataset
    hash: sha256-placeholder
    access: read-only
outputs:
  - ref: artifact://approved-output-location
    max_classification: confidential
sandbox:
  network_egress: deny
  mobile_permissions: []
  require_charging_for_mobile: true
  cpu_limit: "4"
  memory_limit: 8Gi
  timeout: 30m
credentials:
  broker: openclaw-secret-broker
  ttl: 30m
  scope: task-only
coordination:
  task_id: preprocess
  depends_on: []
  barrier_after_completion: true
  heartbeat_interval: 30s
  lease_ttl: 2m
  retry_policy: replace-stalled-worker
  handoff: coordinator-mediated
verification:
  method: signed-result-and-hash
  replay_required: false
  partial_result_required: true
expires_at: "2026-06-02T12:00:00Z"
signature:
  algorithm: ed25519
  value: signed-task-placeholder
```

## Result Envelope

```yaml
api_version: openclaw.io/v1
kind: TaskResult
task_id: task-789
node_id: node-01
status: partial-succeeded
coordination_plan_id: plan-123
coordination_task_id: preprocess
partial_result:
  sequence: 1
  barrier_released: true
outputs:
  - ref: artifact://approved-output-location/result
    hash: sha256-placeholder
provenance:
  started_at: "2026-06-02T11:10:00Z"
  completed_at: "2026-06-02T11:18:00Z"
  runtime: container-runtime-version
  skill_versions:
    data-transform: 0.5.1
logs:
  ref: log://redacted-log-location
  private_payloads_redacted: true
signature:
  algorithm: ed25519
  value: signed-result-placeholder
```
