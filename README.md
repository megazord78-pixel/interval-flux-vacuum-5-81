# Interval flux vacuum certificate on the `(h21,h11)=(5,81)` model

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21906027.svg)](https://doi.org/10.5281/zenodo.21906027)

This is an isolated, fail-closed publication artifact for a proposed theorem:
existence and local uniqueness of a root of the six-complex-field closed flux
subsystem after inclusion of the complete GKZ series.

**Current status: verified for the declared six-field local theorem.** The
finite 557-degree blocker is closed by the exact coverage ledger and a
recentered full-finite Arb/Krawczyk witness. The checker certifies existence
and local uniqueness after attaching the infinite GKZ tail. It does not claim
a 113-field or physical vacuum theorem. See
[`docs/CRITICAL_GAP.md`](docs/CRITICAL_GAP.md).

## What is isolated here

- a dependency-free verifier using exact rational arithmetic for the final
  preconditioner/tail propagation and high-precision decimal arithmetic for
  the remaining published inequalities;
- a small machine-readable certificate and immutable provenance hashes;
- negative tests that destroy the certificate when scope or inequalities are
  altered;
- a narrowly scoped manuscript draft;
- an optional geometric supplement for five rigid rational curves.

The verifier never imports the parent project and never writes files.  Heavy
Arb, Normaliz and CYTools calculations remain upstream certificate generators,
not part of the last-mile trusted checker.

## Run the audit

From this directory in PowerShell:

```powershell
$env:PYTHONPATH = "src"
python -m fluxcert --source-root ../..
python -m unittest discover -s tests -v
python scripts/render_certificate_table.py
```

The strict verifier exits with status zero for the checked-in certificate.
`--candidate-audit` remains available for diagnosing deliberately damaged or
incomplete candidate witnesses.

## Admitted scope after closure

The strongest permissible theorem will be local and subsystem-specific:

- six complex closed fields, equivalently twelve real equations;
- one explicitly declared componentwise box;
- existence and uniqueness inside that box;
- the complete closed-sector GKZ series.

It will not establish global uniqueness, the 113-field system, Kähler/open
stabilisation, uplift, phenomenology, or a complete physical vacuum.

## Directory layout

- `src/fluxcert`: small independent checker;
- `data/certificate.json`: admitted six-field witness and coverage ledger;
- `data/finite_sector_coverage.json`: explicit 557-row and 8,150-degree ledger;
- `data/full_finite_krawczyk.json`: recentered full-finite Arb witness;
- `data/recentered_tail_propagation.json`: all 144 absolute
  \(C_{\rm new}\) bounds, the \(\Delta F\)/\(\Delta J\) vectors, and 12
  exactly recomputable rational tail additions;
- `tests`: positive structural and negative mutation tests;
- `manuscript`: focused article draft;
- `docs/TRUST_MODEL.md`: trusted-base boundary;
- `docs/PUBLICATION_PLAN.md`: actions required before submission.

## Release metadata

Code is offered under BSD-3-Clause. The exact `v1.0.1` release is archived by
Zenodo at [10.5281/zenodo.21906027](https://doi.org/10.5281/zenodo.21906027).
The concept DOI for all versions is `10.5281/zenodo.21906026`.
