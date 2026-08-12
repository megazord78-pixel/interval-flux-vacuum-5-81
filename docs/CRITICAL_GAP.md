# Closed publication blocker: finite source-sector coverage

Status on 2026-08-12: closed for the declared six-field local theorem. The
canonical 557-row/8,150-representation ledger, recentered full-finite Arb
Krawczyk witness and combined infinite-tail inclusion are attached under
`data/`. The independent verifier returns `verified=true` with no blockers.

The text below records the original blocker and closure requirements.

The current upstream all-orders certificate cannot yet be used as the theorem
of a paper.

The tail classifier removes three categories before forming its rigorous
majorant:

1. Chow-zero degrees;
2. positive multicovers of the four displayed primitives;
3. every charge occurring in the 557-row source table.

The first two exclusions have structural meanings.  The third requires a
separate proof that the complete contribution of the finite source sector is
already contained in the four-term prepotential used by the Krawczyk solve, or
a rigorous bound on the difference throughout the full complex box.

At present the repository contains only a pointwise 80-digit comparison.  Its
largest second-derivative difference is approximately `3.10e-39`.  The report
itself correctly says that this is not a box-wide derivative bound.  Because
the inverse Jacobian has norm of order `1e23`, pointwise agreement cannot be
silently substituted into a radius-`1e-30` inclusion theorem.

## Required closure

Use one of the following routes:

- prove an exact identity, including mirror-map and multicover conventions,
  between the 557-degree Chow reduction and the four polylogarithmic terms;
- derive outward-rounded value, first-derivative and second-derivative bounds
  for their difference on the full box, propagate them through the F-terms,
  and show that the old box persists;
- include the complete finite sector in the Arb evaluator, solve for the
  shifted center, and construct a new Krawczyk enclosure.  This is the safest
  route if the difference is nonzero.

The independent verifier intentionally rejects the positive theorem until the
certificate records both a rigorous finite-sector box bound and an interval
certificate for the appropriately centered system.
