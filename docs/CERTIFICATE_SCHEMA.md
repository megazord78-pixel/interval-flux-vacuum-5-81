# Certificate schema and promotion protocol

The checked-in `data/certificate.json` is an admitted witness for the declared
six-field local theorem. Its promotion was made as an atomic replacement
containing:

1. `finite_source_sector.rigorous_box_jet_bound_attached = true`;
2. outward-rounded value, gradient, and Hessian bounds for that sector;
3. `finite_source_sector.recentered_full_finite_sector_root_interval_certified = true`;
4. the recentered box radius, center displacement, remainder row sums, and
   componentwise inclusion witness;
5. an explicit degree-partition artifact accepted by
   `fluxcert.coverage.verify_partition`;
6. SHA-256 entries for every new witness and generator.

Future replacements must be reviewed as a single immutable unit. It is not
permitted to retain either boolean while deleting its attachment. The verifier
makes the numerical fields mandatory, authenticates both attachments and
recomputes the combined finite-plus-infinite Krawczyk image.

All real bounds should be encoded as exact decimal strings rounded outward,
or as explicit integer numerator/denominator objects.  JSON numbers are not
accepted for proof-critical real quantities.
