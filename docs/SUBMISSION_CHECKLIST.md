# Submission checklist

## Blocking author actions

- [x] Supply author name exactly as it should appear in indexes: Evgeniy
      Agafonov.
- [x] Use affiliation `Independent Researcher, Sochi, Russia`.
- [x] Supply durable email: `my@eagafonov.ru`.
- [x] Register an ORCID and insert it into the manuscript and citation file: `0009-0005-9059-5291`.
- [ ] Confirm arXiv hep-th endorsement or arrange an endorser.
- [ ] Choose the software/data license for the release; the verifier package
      is currently BSD-3-Clause.

## Artifact freeze

- [ ] Run the complete repository suite once after the final freeze.
- [ ] Run `python scripts/render_certificate_table.py`.
- [ ] Run `PYTHONPATH=src python -m fluxcert --source-root ../..`.
- [ ] Run `PYTHONPATH=src python -m unittest discover -s tests -v`.
- [ ] Build the LaTeX manuscript twice with BibTeX and inspect the PDF.
- [ ] Create a clean archive without `__pycache__`, temporary files, or private
      research notes.
- [ ] Deposit the archive with a DOI and record its SHA-256.
- [ ] Insert DOI, commit/release identifier, and access date into the paper,
      README, and `CITATION.cff`.

## Scientific review

- [ ] Obtain a technical read from an interval-arithmetic specialist.
- [ ] Obtain a technical read from a mirror-symmetry/flux-vacua specialist.
- [ ] Repeat the priority search immediately before arXiv submission.
- [ ] Confirm that every occurrence of “vacuum” is scoped to the six-field
      closed subsystem where appropriate.
- [ ] Confirm that the five rigid curves are described as supporting and
      non-exhaustive.

## Submission order

- [ ] Post the frozen manuscript and ancillary archive to arXiv.
- [ ] Submit to JHEP with the focused cover letter.
- [ ] If declined for fit or priority, revise the cover letter and submit to
      Nuclear Physics B; use Classical and Quantum Gravity as the next option.
