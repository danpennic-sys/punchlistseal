# PunchListSeal

**Local-first punch-list / deficiency logger and QuantumGuard evidence sealer for field operators.**

Offline. Deterministic. Pay once. Compatible with QuantumGuard CONTRACT-v1, VeriQuote, FieldSeal, JobSeal, MediaSeal, ChangeOrderSeal, CloseSeal, LifecycleSeal, and Evidence-Core.

## Why PunchListSeal?

Punch items and deficiencies get lost in notes, texts, and memory. Clients dispute whether an item was open, closed, or never raised. Supervisors need a clean, verifiable record at walkthrough and close-out.

PunchListSeal captures punch items (location, description, status, owner, photos via media hashes, timestamps), then seals the list into a client-verifiable QuantumGuard evidence bundle.

- No SaaS. No subscription. Runs completely offline after key setup.
- Clients (or their auditors) verify the pack with the free QuantumGuard verifier (`qg verify`).
- Pairs with MediaSeal for photo evidence, FieldSeal / JobSeal for job context, CloseSeal for final close-out, and LifecycleSeal for the full job pack.

## Quick Start

```bash
# Optional but recommended for real Ed25519 signatures
pip install cryptography

python3 src/punchlistseal.py --demo
python3 src/punchlistseal.py --list samples/punch-001.json --out sealed_punch.json
```

Verify the output with the QuantumGuard CLI (from the quantumguard repo):

```bash
qg verify sealed_punch.json
```

Expected verdict: PASS (when using real cryptography).

## What you can sell

| SKU       | Price | Includes                                      |
|-----------|-------|-----------------------------------------------|
| Operator  | $69   | CLI + templates + key setup guide + 1-year email support |
| Command   | $189  | + batch mode + HTML punch form + reseller rights |
| Agency    | $479  | + white-label HTML + design partner onboarding |

Purchase / access: danpennic@gmail.com

Source remains free under Apache-2.0 OR MIT. Commercial Operator Pack sold separately.

## Stack Fit

- Python CLI (same family as VeriQuote, FieldSeal, MediaSeal, ChangeOrderSeal, JobSeal, CloseSeal, LifecycleSeal)
- Emits QuantumGuard CONTRACT-v1 bundles (Ed25519, deterministic hashing)
- Local key storage (PEM)
- Ready for LifecycleSeal aggregation and CloseSeal handoff

## License

Apache-2.0 OR MIT
