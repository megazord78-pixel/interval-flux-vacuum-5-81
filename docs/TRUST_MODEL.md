# Trust model

## Central theorem

For a continuously differentiable real map (F:\mathbb R^{12}\to\mathbb
R^{12}), a center (x_0), a box (X=x_0+[-r,r]^{12}), and a nonsingular
preconditioner (C), strict inclusion of the Krawczyk image

\[
K(X)=x_0-CF(x_0)+(I-CJ(X))(X-x_0)
\]

in the interior of (X) proves existence and uniqueness of a zero in the
box.  The all-orders theorem additionally needs a rigorous enclosure of the
change in (F) and (J) caused by every omitted GKZ degree.

## Minimal trusted components

The final reviewer-facing chain should contain only:

1. exact model data and immutable hashes;
2. an Arb evaluator of the complete finite system on the declared box;
3. exact rational low-tail and geometric high-tail witnesses;
4. explicit, disjoint and exhaustive degree-category lists;
5. a componentwise propagation to (F), (J), and the Krawczyk image;
6. this dependency-free final checker.

Approximate roots, inverse matrices and triangulations are witnesses.  Their
correctness is established by interval or exact checks; they are not axioms.

## Excluded from the central trusted base

- the five-curve geometry, which is supporting evidence only;
- the physical 113-field admission gate;
- Pfaffians, mobile-D3 geometry and uplift;
- cosmological or phenomenological claims;
- the remainder of the parent `Theory of All` research program.

## Fail-closed rules

- A missing category, hash or bound rejects the theorem.
- Pointwise numerical agreement cannot stand in for a box enclosure.
- Boolean conclusions from upstream files are not trusted; the verifier
  recomputes the final inequalities.
- Decimal upper bounds must be outward-rounded before serialization.
- The checker accepts no legacy cache and performs no cache migration.

## Remaining independent-reimplementation target

The publication version should have a second generator for the final
Krawczyk inequality, preferably in a different language or interval package.
This is not required for mathematical validity but materially increases
reviewer confidence and catches convention errors.
