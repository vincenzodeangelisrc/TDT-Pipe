# TDT-Pipe ProVerif Models

This folder contains three ProVerif models of the TDT-Pipe validated telemetry
pipeline.

## Files

- `tdt_pipe_pipeline.pv`: richer actor-chain model with two devices, secure
  publishers, an untrusted broker channel, registry-style gateway checks,
  provenance creation, DT-state application events, and symbolic per-stream
  private locks around the sequence-state critical section.
- `tdt_pipe_pipeline_atomic_replay.pv`: bounded two-input version of the
  pipeline model in which the already accepted sequence state is represented
  explicitly for the second gateway input. This file checks that an exact reuse
  of an already accepted device-topic-sequence triple cannot produce a second
  acceptance in the bounded sequential scenario. It also includes reachability
  checks showing that replay rejection can occur and that a distinct valid
  second update can still be accepted.
- `tdt_pipe_reachability_sanity.pv`: bounded honest-execution sanity model used
  only to check that both registered device-topic streams can reach gateway
  acceptance. It is not used as an attacker-resistance proof.
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

Across the pipeline and atomic-replay models, ProVerif checks the following
symbolic properties:

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
6. The replay-rejection branch is reachable for both registered streams, and the
   bounded model can still accept a second valid update when it does not reuse
   the stored device-topic-sequence triple.

The reachability sanity model is intentionally reported separately from these
security properties. It checks that the two honest registered streams can reach
`gateway_accept`, so the security queries are not interpreted over an obviously
dead device branch. In ProVerif output, the expected reachability result is
reported as `not event(...) is false`.

The distinction in point 5 is important. Replay protection depends on the
sequence-state check and update being one atomic critical section for each
device-topic stream. The unbounded replicated gateway model
(`tdt_pipe_pipeline.pv`) includes symbolic private per-stream locks for that
critical section and proves secrecy, non-injective authentication,
authorization, sensor-origin, and state/audit correspondence queries. The model
does not claim a global injective authentication theorem for the replicated
gateway process; replay is instead checked in the focused bounded model below.
The bounded `tdt_pipe_pipeline_atomic_replay.pv` model makes the same atomicity
assumption explicit for two gateway inputs, which is the representative exact
replay pattern. In this bounded model, ProVerif proves secrecy,
non-injective authentication, authorization, sensor-origin linkage, and the
absence of a second acceptance when the second input reuses the already accepted
device-topic-sequence triple. The same model also checks that the replay branch
is not dead: ProVerif reconstructs traces in which an exact replay reaches
`replay_rejected` for both registered streams. A further reachability query
shows that a distinct second valid update can still reach
`gateway_second_accept`, so the model is not proving replay safety by rejecting
all second inputs. These results do not extend to an unbounded number of
gateway inputs, numeric sequence monotonicity, timestamp-window validation, or
recovery after loss of sequence state.

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
validation of authentication, payload integrity, topic binding, and
admission-to-state/audit behavior under the stated assumptions.

## Running

Install ProVerif and run from this folder:

```bash
python3 run_all.py
```

Outputs are written to:

```text
output/
```
