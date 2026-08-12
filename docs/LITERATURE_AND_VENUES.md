# Literature and venue assessment

## Defensible novelty statement

The safe claim for the manuscript is:

> To our knowledge, this is the first end-to-end interval certificate of local
> existence and uniqueness for an explicit multi-parameter compact
> Calabi--Yau closed-flux root that includes a complete finite GKZ sector and a
> rigorously propagated all-orders infinite tail.

This wording is narrower than “the first stable string vacuum” and does not
claim a 113-field solution, global uniqueness, or a full physical vacuum.

The literature search performed on 12 August 2026 found four adjacent but
distinct lines of work:

1. algorithmic algebraic geometry and numerical homotopy methods for locating
   or enumerating flux vacua (Gray--He--Lukas 2006; Mehta 2011;
   Martinez-Pedrera et al. 2013);
2. practical Krawczyk certification for polynomial systems (Breiding--Rose--
   Timme 2024), without the Calabi--Yau GKZ-tail problem;
3. computational mirror symmetry and high-degree GV calculations in
   many-modulus compact threefolds (Demirtas et al. 2024);
4. flux-vacuum analyses in which instanton corrections are evaluated or shown
   numerically to be small, including the source model and later boundary
   studies (Demirtas et al. 2021; Chauhan et al. 2026).

No located paper combined exhaustive degree accounting, exact finite Chow
arithmetic, an analytic infinite-tail majorant, propagation through the
F-term Jacobian, and a strict interval uniqueness proof. This is evidence for
the stated priority claim, not a logically exhaustive proof that no obscure
precedent exists. Repeat the search immediately before arXiv submission.

Primary links:

- <https://arxiv.org/abs/hep-th/0606122>
- <https://arxiv.org/abs/1108.1201>
- <https://arxiv.org/abs/1212.4530>
- <https://arxiv.org/abs/2011.05000>
- <https://arxiv.org/abs/2107.09064>
- <https://arxiv.org/abs/2303.00757>
- <https://arxiv.org/abs/2404.12422>
- <https://arxiv.org/abs/2607.20777>

## Recommended journal sequence

### 1. Journal of High Energy Physics

Best scientific fit if the paper foregrounds the explicit type-IIB flux
system and all-orders instanton control. JHEP is demanding, but the source
geometry and the closest computational-mirror-symmetry work already live in
that community. Publishing costs have been covered through SCOAP3 rather than
charged to authors: <https://www.springer.com/gp/about-springer/media/press-releases/corporate/journal-of-high-energy-physics-turns-twenty-/13344768>.

### 2. Nuclear Physics B

Strong fallback for a paper balanced between high-energy theory,
mathematical physics, and a computer-assisted proof. Elsevier states that
authors do not pay publication fees for SCOAP3 journals:
<https://www.elsevier.com/en-in/subject/physics-and-astronomy/journals/open-access-for-physics-journals>.

### 3. Classical and Quantum Gravity

Reasonable fallback if the exposition emphasizes rigorous compactification
methods and the broader relevance of controlled string vacua. CQG explicitly
includes string vacua and compactifications in scope and states that
subscription-access publication is free of charge:
<https://publishingsupport.iopscience.iop.org/journals/classical-and-quantum-gravity/about-classical-quantum-gravity/>.

Communications in Mathematical Physics is not the first target in the current
state. A CMP submission would benefit from a more abstract theorem separating
the general certification framework from this single compactification and an
independent second implementation of the interval generator.

## Submission prerequisites

- Author, correspondence, and ORCID metadata are complete.
- Obtain or confirm arXiv hep-th endorsement if needed.
- Deposit the exact release in Zenodo or another DOI-issuing repository.
- Add the DOI and immutable release hash to the paper and `CITATION.cff`.
- Ask one interval-arithmetic specialist and one mirror-symmetry specialist
  for private technical readings.
- Include a short cover-letter paragraph distinguishing the six-field theorem
  from a full physical-vacuum claim.
