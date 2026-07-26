# TDT-Pipe ProVerif Models

This folder contains ProVerif models of the TDT-Pipe message-authentication
core and of the validated telemetry pipeline.

## Files

- `tdt_pipe_core.pv`: compact single-device model of payload integrity, HMAC
  authentication, and topic binding.
- `tdt_pipe_reachability_sanity.pv`: bounded honest-execution sanity model used
  only to check that both registered device-topic streams can reach gateway
  acceptance. It is not used as an attacker-resistance proof.
- `tdt_pipe_pipeline.pv`: richer actor-chain model with two devices, secure
  publishers, an untrusted broker channel, registry-style gateway checks,
  provenance creation, DT-state application events, and symbolic per-stream
  private locks around the sequence-state critical section.
- `tdt_pipe_pipeline_atomic_replay.pv`: bounded two-input version of the richer
  pipeline model in which the already accepted sequence state is represented
  explicitly for the second gateway input. This file is used to inspect the
  replay-related correspondence under a sequential gateway abstraction.
- `run_all.py`: runs all models and stores the full ProVerif output and RESULT
  summaries.

The models focus on the part of the pipeline where a registered device publishes
a protected telemetry message containing:

- device identity;
- authorized topic;
- timestamp;
- sequence value;
- payload;
- payload digest;
- HMAC over the protected body.

The MQTT/broker channel is public and controlled by a Dolev-Yao attacker. The
attacker may intercept, modify, replay, drop, and inject messages, but does not
know the private validation keys of non-compromised devices.

## Verified Properties

Across the models, ProVerif checks the following symbolic properties:

1. Device validation keys remain secret.
2. If the gateway accepts a message, then the corresponding secure publisher
   previously published the same device, topic, payload, and sequence value.
3. Messages on unauthorized topics are not accepted by the gateway.
4. Accepted updates are associated with provenance/audit and DT-state application
   events.
5. Under the explicit assumption that gateway sequence-state validation and
   update are atomic/sequential for a device-topic stream, replay protection is
   represented by rejecting a second gateway input carrying an already accepted
   device-topic-sequence triple.

The reachability sanity model is intentionally reported separately from these
security properties. It checks that the two honest registered streams can reach
`gateway_accept`, so the security queries are not interpreted over an obviously
dead device branch. In ProVerif output, the expected reachability result is
reported as `not event(...) is false`.

The distinction in point 5 is important. Replay protection depends on the
sequence-state check and update being one atomic critical section for each
device-topic stream. The unbounded replicated gateway model
(`tdt_pipe_pipeline.pv`) includes symbolic private per-stream locks for that
critical section and proves the non-injective authentication, secrecy,
authorization, sensor-origin, and state/audit correspondence queries. ProVerif
does not prove the injective query in that unbounded model because of its
abstraction of replicated processes and tables; the output reports that no
concrete trace is found for the derivation.
The bounded `tdt_pipe_pipeline_atomic_replay.pv` model makes the same atomicity
assumption explicit for two gateway inputs, which is the representative replay
pattern. In the current model, ProVerif proves the non-injective authentication,
secrecy, authorization, sensor-origin, and state/audit correspondence queries.
It still reports the injective correspondence query as not proved, without
producing a concrete attack trace. Therefore, the ProVerif evidence should be
reported as a symbolic validation of authentication, integrity, topic binding,
and validated admission to provenance/state, while replay resistance should be
stated as relying on an atomic implementation of the sequence-state check and
update.

## Scope

These are symbolic models, not implementation benchmarks. They intentionally
abstract away:

- numeric timestamp windows;
- unbounded numeric counter arithmetic;
- semantic plausibility rules;
- quarantine lifecycle;
- audit persistence;
- MQTT QoS/session behavior;
- concrete DT-state storage;
- compromised gateway, registry, or device-key scenarios.

Those aspects are handled by the formal model, security discussion, and
experimental evaluation in the paper. The ProVerif models provide symbolic
validation of the authentication, payload-integrity, topic-binding, and
admission-to-state/audit core under the stated assumptions.

## Running

Install ProVerif and run:

```bash
python3 experiments/proverif/run_all.py
```

Outputs are written to:

```text
experiments/proverif/output/
```
