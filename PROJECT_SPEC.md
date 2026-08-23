# PROJECT_SPEC.md

## 1. Purpose of this file

This file is the single source of truth for the project.

Any coding agent working on this repository should read this file before changing code, data schemas, model targets, thresholds, or simulation protocols.

If a requested implementation conflicts with this document, stop and surface the conflict instead of silently changing the project scope.

---

# 2. Project title

**Physics-Validated Generative Molecular Design of Sustainable Dielectric Liquids for Single-Phase Immersion Cooling of AI Data Centres**

Working shorter title:

**Generative Molecular Design of Single-Phase Immersion Cooling Fluids**

---

# 3. Project summary

The project investigates whether machine learning can discover novel molecular liquids suitable for **single-phase dielectric immersion cooling** of high-density AI hardware.

The project is focused specifically on the **working fluid**, not on designing the entire cooling system.

The core idea is:

```text
engineering requirements
        ↓
experimental molecular-property data
        ↓
molecular representation / RDKit
        ↓
property prediction
        ↓
generative molecular design
        ↓
hard-constraint filtering
        ↓
multi-objective screening / Pareto ranking
        ↓
top 2–3 candidates
        ↓
molecular dynamics / NEMD
        ↓
physics-based validation of thermal conductivity
        ↓
evidence-backed shortlist
```

The final output is not a claim that a molecule is experimentally proven to be a commercial coolant.

The intended output is a shortlist of candidates supported by:

1. data-driven property prediction, and
2. independent physics simulation.

Experimental synthesis, full toxicology, full materials-compatibility qualification, and long-duration aging tests are outside the current project scope.

---

# 4. Research motivation

High-density AI systems are pushing data-centre cooling away from conventional air-only approaches and toward liquid cooling.

Current mainstream high-density AI deployments primarily use **direct-to-chip liquid cooling**, while single-phase immersion remains an active alternative with different engineering advantages and constraints.

This project does **not** assume that immersion will replace direct-to-chip cooling.

Instead, the research question is narrower:

> Can molecular design improve the working-fluid bottleneck for single-phase dielectric immersion cooling?

Immersion fluids must combine several properties that are difficult to optimize simultaneously:

- heat-transfer performance,
- low viscosity / pumpability,
- electrical insulation,
- low dielectric constant,
- low volatility,
- fire safety,
- chemical stability,
- materials compatibility,
- environmental acceptability.

This makes the problem a natural multi-objective molecular-design task.

---

# 5. Central research question

> **Can generative machine learning identify novel, environmentally preferable dielectric molecular liquids that satisfy the competing thermal, electrical, flow, and safety requirements of single-phase immersion cooling, and can molecular dynamics independently validate their predicted thermal conductivity?**

---

# 6. Scope

## In scope

- single-phase immersion cooling
- molecular dielectric liquids
- organic / molecular coolant candidates
- experimental molecular-property datasets
- RDKit molecular validation and descriptors
- graph neural-network property prediction
- classical ML baselines
- generative molecular modelling
- molecular validity and novelty checks
- multi-objective screening
- Pareto analysis
- synthetic-accessibility heuristics
- environmental structural screening
- force-field parameterization
- equilibrium MD
- NEMD thermal-conductivity validation
- uncertainty and model-vs-physics comparison
- comparison with known reference/commercial fluids

## Out of scope

- designing immersion tanks
- designing pumps or CDUs
- full data-centre HVAC design
- CFD of the entire tank or facility
- GPU cold-plate design
- hardware manufacturing
- experimental synthesis
- experimental dielectric qualification
- full fire certification
- full toxicology
- multi-year oxidation experiments
- full materials-compatibility qualification
- claiming commercial readiness from simulation alone

---

# 7. Decisions already locked

These decisions should not be changed without explicit project-owner approval.

## D1 — Cooling architecture

**Locked:** single-phase immersion cooling.

Do not switch the project to two-phase immersion or direct-to-chip cooling without an explicit scope change.

## D2 — Research object

**Locked:** the working fluid.

The system architecture is used to define engineering requirements, but the project does not optimize pumps, tanks, manifolds, or facility infrastructure.

## D3 — Physics validation

**Locked:** the top 2–3 candidates should receive molecular-dynamics validation.

Thermal conductivity is the main physics-validated property.

## D4 — Thermal validation method

**Locked as current plan:** non-equilibrium molecular dynamics (NEMD) using Fourier's law.

Conceptually:

\[
J_q = -k \nabla T
\]

and therefore:

\[
k = -\frac{J_q}{dT/dx}
\]

## D5 — Raw experimental data policy

**Locked:** one experimental measurement per row.

Do not prematurely average repeated literature measurements.

Preserve measurement conditions and provenance.

---

# 8. Decisions intentionally still open

Codex must not silently decide these.

## O1 — Environmental chemistry constraint

Still open:

### Option A
**Non-PFAS** according to an explicit structural/regulatory definition.

### Option B
**Strict fluorine-free**

\[
N_F = 0
\]

Current preferred scientific framing:

- primary research goal: environmentally preferable / non-PFAS chemistry
- optional stricter search: fluorine-free chemical space

Do **not** hard-code `F_count == 0` as the universal project rule until this decision is finalized.

## O2 — Final ML target set

The final set of predicted properties must be decided **after** the data-availability and overlap audit.

Do not assume all desired engineering properties have enough experimental labels for a GNN.

## O3 — Generator architecture

Candidate options include:

- VAE
- conditional VAE
- diffusion model
- other constrained molecular generator

Current educational/default preference is a **CVAE**, but this is not yet locked.

## O4 — Force field

Possible starting points include:

- OPLS-AA
- GAFF
- another validated organic-liquid force field

The choice must be made after checking parameter coverage for the finalist chemistry.

---

# 9. Engineering fluid requirements

A good single-phase immersion fluid is a **multi-property** fluid.

Do not optimize thermal conductivity alone.

The overall thermal behavior depends on properties including:

\[
k,\quad c_p,\quad \rho,\quad \mu,\quad \beta
\]

where:

- \(k\) = thermal conductivity
- \(c_p\) = isobaric specific heat capacity
- \(\rho\) = density
- \(\mu\) = dynamic viscosity
- \(\beta\) = volumetric thermal-expansion coefficient

## Working property list

### Thermal / flow

- thermal conductivity \(k(T)\): higher is generally better
- heat capacity \(c_p(T)\): higher is generally better
- density \(\rho(T)\): context-dependent but required for volumetric heat capacity and FOMs
- viscosity \(\mu(T)\): lower is generally better
- thermal expansion \(\beta(T)\): relevant to natural convection
- vapor pressure \(P_{vap}(T)\): lower is generally better
- boiling point \(T_b\): must be sufficiently high for single-phase operation

### Electrical

- relative permittivity / dielectric constant \(\varepsilon_r\): lower is generally preferred for signal integrity
- dielectric loss \(\tan\delta\): lower is preferred
- dielectric strength: higher is preferred
- volume resistivity: higher is preferred

Important:

\[
\text{dielectric constant} \neq \text{dielectric strength} \neq \text{conductivity}
\]

Do not conflate these quantities.

### Safety

- flash point: higher is preferred
- autoignition temperature: higher is preferred
- low volatility
- chemically stable liquid over the operating range

### Environmental

- non-PFAS / fluorine rule: still to be finalized
- low persistence
- low bioaccumulation
- low toxicity
- low GWP
- ODP = 0 where relevant

### Long-term / system-level

These matter industrially but are not currently core GNN targets:

- oxidation stability
- corrosion
- material compatibility
- water contamination sensitivity
- elastomer/plastic/adhesive compatibility
- long-duration reliability

These should be treated as late-stage validation requirements or limitations unless reliable datasets become available.

---

# 10. Working benchmark values

The following are **provisional OCP-derived engineering benchmarks**, not immutable project truths.

They must be re-verified against the source literature before being enforced as final hard filters.

### Single-phase working benchmarks

- boiling point: approximately \(>150^\circ C\)
- flash point: approximately \(>150^\circ C\)
- vapor pressure: approximately \(<0.8\) kPa at \(25^\circ C\)
- dynamic viscosity: approximately \(<0.015\) Pa·s at \(25^\circ C\)
- relative permittivity: approximately \(\le 2.3\)
- dielectric loss: approximately \(\le 0.05\)
- dielectric strength: approximately \(>6\) kV/mm
- volume resistivity: approximately \(>10^{11}\ \Omega\cdot cm\)
- ODP: 0

### OCP thermal figures of merit

A useful natural-convection figure of merit is:

\[
FOM_1 =
k
\left(
\frac{\beta c_p \rho^2}
{\mu k}
\right)^{0.2813}
\]

Working OCP targets previously identified:

- Tier 1: \(FOM_1 > 35\)
- Tier 2: \(FOM_1 > 45\)

These must be source-checked before final use.

---

# 11. Temperature treatment

Temperature dependence is mandatory.

Do not build a dataset that stores a property without its measurement temperature when temperature is relevant.

Correct:

```text
thermal_conductivity = 0.135 W/(m·K)
temperature_K = 313.15
```

Incorrect:

```text
thermal_conductivity = 0.135
```

Priority temperature-dependent properties:

\[
k(T),\quad
\mu(T),\quad
\rho(T),\quad
c_p(T),\quad
P_{vap}(T)
\]

Relative permittivity may also depend on temperature and frequency.

### Important industry-context rule

NVIDIA's approximately \(45^\circ C\) direct-to-chip coolant inlet is useful context for the industry's move toward warm-liquid cooling.

It is **not automatically the operating specification for this immersion project**.

Do not hard-code \(45^\circ C\) as the immersion design temperature.

Working data strategy:

- preserve all valid temperatures
- pay particular attention to approximately 25–70°C
- consider ~50°C as a provisional comparison/evaluation point only after source verification

---

# 12. Current ML-target strategy

The first-pass data audit suggests the following architecture.

## Tier 1 — likely core ML targets

\[
\rho(T)
\]

\[
\mu(T)
\]

\[
k(T)
\]

\[
T_b
\]

\[
T_{flash}
\]

## Tier 2 — likely feasible, pending data audit

\[
c_p(T)
\]

\[
P_{vap}(T)
\]

## Derived rather than directly predicted

Thermal expansion coefficient:

\[
\beta =
-\frac{1}{\rho}
\left(
\frac{\partial \rho}{\partial T}
\right)_P
\]

Prefer deriving \(\beta(T)\) from a reliable density-vs-temperature model instead of training a separate model unless direct data justify it.

## Currently data-limited / specialist

\[
\varepsilon_r
\]

\[
E_{breakdown}
\]

\[
\tan\delta
\]

\[
\rho_{electrical}
\]

Do not promise a broad dielectric GNN until label counts and chemistry coverage are verified.

## Do not assume these are ML targets yet

- toxicity
- GWP
- long-term oxidation
- materials compatibility
- corrosion

These require a separate evidence and data assessment.

---

# 13. Data-source hierarchy

Use the following preference order.

## Tier A — primary experimental sources

1. NIST ThermoML / Thermodynamics Research Center data
2. peer-reviewed experimental datasets
3. original journal articles

## Tier B — engineering/commercial baselines

4. manufacturer technical datasheets
5. OCP-recognized product/specification documents

## Tier C — identity / metadata

6. PubChem
7. authoritative chemical registries

PubChem is useful for:

- identifiers
- canonical/isomeric SMILES
- InChI / InChIKey
- formula
- molecular weight
- synonyms

Do not treat PubChem aggregation alone as the preferred source for high-value experimental property labels when a primary measurement source is available.

## Avoid as training truth unless traced to the original source

- random web tables
- unsourced aggregators
- LLM-generated property values
- values with no temperature/method/source
- predicted values mixed with experiments without labels

---

# 14. Raw experimental schema

The canonical raw-measurement table should follow a long format.

Recommended columns:

```text
record_id
molecule_id
molecule_name
CAS
InChI
InChIKey
SMILES
canonical_SMILES
property_name
property_value
property_unit
temperature_K
pressure_Pa
phase
frequency_Hz
measurement_method
uncertainty
uncertainty_type
source_type
source_title
source_DOI
source_url
publication_year
source_record_id
notes
quality_flag
```

Not every column will be populated for every measurement.

Never discard missingness silently.

---

# 15. Unit policy

Normalize units only in the processed layer.

Raw values and original units should remain available.

Canonical processed units:

- temperature: K
- pressure: Pa
- thermal conductivity: W·m⁻¹·K⁻¹
- dynamic viscosity: Pa·s
- kinematic viscosity: m²/s
- density: kg/m³
- heat capacity: J·kg⁻¹·K⁻¹
- vapor pressure: Pa
- boiling point: K
- flash point: K
- dielectric constant: dimensionless
- dielectric strength: V/m or clearly documented kV/mm
- resistivity: Ω·m or source-preserved plus normalized field

Viscosity relation:

\[
\mu = \rho \nu
\]

where:

- \(\mu\) = dynamic viscosity
- \(\nu\) = kinematic viscosity
- \(\rho\) = density

Do not mix \(\mu\) and \(\nu\).

---

# 16. Raw-data immutability rule

Directory intent:

```text
data/
├── raw/
├── interim/
└── processed/
```

## `data/raw/`

Immutable source downloads.

Never manually edit files here.

## `data/interim/`

Parsed, normalized, or identity-resolved intermediate data.

## `data/processed/`

Model-ready datasets.

Every processed file should be reproducible from raw data through code.

---

# 17. Molecular identity and RDKit policy

All model-ready molecular structures must pass an identity and chemistry pipeline.

Conceptual pipeline:

```text
source identity
    ↓
SMILES / InChI
    ↓
RDKit parse
    ↓
sanitization
    ↓
canonicalization
    ↓
deduplication
    ↓
descriptor calculation
    ↓
project-specific chemistry filters
```

Important:

\[
\text{chemical validity} \neq \text{passes project constraints}
\]

A molecule can be valid chemistry while failing an environmental, boiling-point, safety, or electrical constraint.

Recommended RDKit-derived fields:

- canonical SMILES
- isomeric SMILES
- InChIKey
- molecular weight
- logP
- TPSA
- atom count
- heavy-atom count
- ring count
- heteroatom count
- fluorine count
- formal charge
- rotatable bonds

Do not remove fluorinated molecules until the final PFAS/fluorine decision is locked.

---

# 18. Data-quality rules

Each model target must have a documented cleaning policy.

At minimum:

1. experimental vs predicted values must be distinguished
2. temperature must be retained
3. pressure must be retained when relevant
4. liquid phase must be verified
5. mixtures must not be silently treated as pure compounds
6. salts/ionic liquids should be handled explicitly rather than mixed with neutral molecular fluids by accident
7. duplicate publications must be identified where possible
8. obvious unit errors must be quarantined, not silently corrected
9. outliers must be flagged with rationale
10. provenance must survive every processing step

No value should enter a training table with unknown origin.

---

# 19. Coverage audit before modelling

Before training any GNN, calculate for each property:

- number of experimental rows
- number of unique molecules
- number of unique chemical scaffolds
- temperature range
- pressure range
- chemical-family distribution
- missingness
- duplicate density
- source distribution

Also calculate label overlap:

\[
N_k,\quad
N_\mu,\quad
N_\rho,\quad
N_{c_p}
\]

and intersections such as:

\[
N_{k\cap\mu}
\]

\[
N_{k\cap\mu\cap\rho}
\]

\[
N_{k\cap\mu\cap\rho\cap c_p}
\]

This determines whether to use:

- separate single-task models,
- partially labelled multitask learning,
- or a fully shared multitask model.

Do not choose the multitask architecture before this audit.

---

# 20. Baseline-model rule

Before building a GNN, train at least one classical baseline.

Recommended:

```text
Morgan fingerprint
    ↓
Random Forest / XGBoost / another standard regressor
    ↓
property prediction
```

The GNN must justify its complexity relative to the baseline.

---

# 21. GNN concept

Molecular graph:

- nodes = atoms
- edges = bonds

Possible node features:

- atomic number
- degree
- formal charge
- aromaticity
- hybridization
- implicit/explicit hydrogen information

Possible edge features:

- bond type
- aromaticity
- conjugation
- ring membership

Temperature-dependent model concept:

```text
molecular graph ──→ GNN ──→ molecular embedding
                              │
temperature ──────────────────┘
                              ↓
                           MLP head
                              ↓
                         property(T)
```

Do not assume the exact architecture, depth, hidden dimension, or pooling type until after the baseline and data audit.

---

# 22. Evaluation policy

For regression:

- MAE
- RMSE
- \(R^2\)

Use:

- train/validation/test separation
- scaffold-aware splitting where appropriate
- cross-validation if dataset size is small
- uncertainty estimates where feasible

Do not tune on the test set.

For temperature-dependent properties, evaluate both:

- molecule generalization
- temperature interpolation/extrapolation behavior

---

# 23. Generative-model stage

Do not begin generative modelling until property models and screening rules are credible.

Possible architecture:

```text
molecule
   ↓
encoder
   ↓
latent distribution
   ↓
z
   +
condition vector c
   ↓
decoder
   ↓
generated molecule
```

A CVAE is currently the simplest preferred option because it supports property conditioning.

Generator evaluation must include:

- validity
- uniqueness
- novelty
- diversity
- synthetic accessibility
- property-target hit rate
- hard-constraint pass rate

Do not treat validity alone as success.

---

# 24. Screening architecture

Conceptual pipeline:

```text
generated molecule
      ↓
RDKit validity
      ↓
canonicalize
      ↓
deduplicate
      ↓
environmental chemistry rule
      ↓
single-phase / volatility constraints
      ↓
flash / safety constraints
      ↓
electrical screening
      ↓
property predictions
      ↓
thermal FOM calculation
      ↓
synthetic-accessibility check
      ↓
Pareto ranking
```

Hard constraints and soft objectives must remain separate.

Do not combine everything into one arbitrary weighted score unless there is a documented reason.

---

# 25. Pareto optimization

A candidate A dominates candidate B if A is:

- at least as good in every selected objective, and
- strictly better in at least one.

The Pareto front should preserve trade-offs rather than hiding them inside one scalar score.

Candidate objectives may include:

- higher \(k\)
- higher \(c_p\)
- lower \(\mu\)
- lower \(\varepsilon_r\)
- lower vapor pressure
- higher flash point
- lower environmental hazard
- easier synthesis

Final objective set remains data-dependent.

---

# 26. Commercial / reference baselines

Generated candidates must be compared with known fluids.

Baseline categories should include:

1. at least one current commercial single-phase immersion fluid
2. at least one traditional dielectric liquid / hydrocarbon or ester reference
3. at least one historical fluorinated reference where scientifically useful

The baseline list is not locked yet.

A generated property value should never be presented without context.

For example:

```text
candidate k = 0.145 W/(m·K)
```

is much less informative than:

```text
candidate k = 0.145 W/(m·K)
commercial baseline k = ...
measurement temperature = ...
```

---

# 27. Force-field and MD stage

Only top candidates should enter expensive simulation.

Conceptual workflow:

```text
candidate molecule
      ↓
force-field parameterization
      ↓
periodic liquid box
      ↓
energy minimization
      ↓
NVT equilibration
      ↓
NPT equilibration
      ↓
production / validation
      ↓
NEMD hot/cold setup
      ↓
steady state
      ↓
heat flux + temperature gradient
      ↓
thermal conductivity
```

Force field provides:

\[
U(\mathbf r)
\]

and forces:

\[
\mathbf F_i = -\nabla_i U
\]

The integrator updates positions.

Do not conflate the force field with the integration algorithm.

---

# 28. Force-field validation rule

Never simulate a novel generated molecule and trust the output solely because LAMMPS ran without errors.

Before using a force-field workflow on finalists:

1. select at least one chemically similar known liquid
2. simulate it
3. compare simulated properties with experimental values
4. document the error
5. decide whether the parameterization is credible for that chemical family

Stable simulation does not imply physical accuracy.

---

# 29. NEMD thermal-conductivity protocol

Core relationship:

\[
J_q = -k\nabla T
\]

For 1D transport:

\[
k = -\frac{J_q}{dT/dx}
\]

Conceptual setup:

```text
cold region
    │
    │ temperature bins
    │
hot region
```

or equivalent periodic geometry.

Requirements:

- establish steady state
- measure thermostat energy exchange
- compute heat flux correctly for the geometry
- bin temperature along the transport direction
- fit the linear interior region
- exclude directly thermostatted regions from the main gradient fit
- quantify uncertainty
- check finite-size sensitivity if feasible

Possible finite-size extrapolation form:

\[
\frac{1}{k(L)} =
\frac{1}{k_\infty} + \frac{C}{L}
\]

Do not assume this relation is exact for every system; document its use.

---

# 30. What MD validates

The MD/NEMD stage validates:

\[
\boxed{\text{thermal conductivity component}}
\]

It does **not** prove:

- full coolant suitability
- hardware compatibility
- long-term chemical stability
- fire certification
- toxicity
- commercial manufacturability

Final reporting must state this limitation clearly.

---

# 31. Final comparison

For each finalist, report something like:

```text
molecule
canonical SMILES
structural class
hard-constraint status
predicted k(T)
predicted viscosity(T)
predicted density(T)
predicted Cp(T)
predicted flash point
predicted boiling point
dielectric evidence
thermal FOM
synthetic-accessibility score
Pareto status
NEMD k(T)
GNN-vs-NEMD difference
uncertainty
limitations
```

---

# 32. Repository structure

Recommended structure:

```text
immersion-fluid-discovery/
│
├── PROJECT_SPEC.md
├── README.md
├── pyproject.toml
├── requirements.txt
│
├── config/
│   ├── properties.yaml
│   ├── units.yaml
│   └── screening.yaml
│
├── data/
│   ├── raw/
│   ├── interim/
│   ├── processed/
│   └── external/
│
├── notebooks/
│   ├── 01_data_audit.ipynb
│   ├── 02_identity_rdkit.ipynb
│   ├── 03_eda.ipynb
│   ├── 04_baselines.ipynb
│   ├── 05_gnn_evaluation.ipynb
│   └── 06_candidate_analysis.ipynb
│
├── src/
│   └── immersion_ml/
│       ├── data/
│       │   ├── download.py
│       │   ├── thermoml.py
│       │   ├── normalize.py
│       │   ├── identity.py
│       │   └── quality.py
│       │
│       ├── chemistry/
│       │   ├── rdkit_validation.py
│       │   ├── descriptors.py
│       │   ├── fingerprints.py
│       │   └── filters.py
│       │
│       ├── models/
│       │   ├── baseline.py
│       │   ├── gnn.py
│       │   ├── losses.py
│       │   └── evaluation.py
│       │
│       ├── generation/
│       │   ├── cvae.py
│       │   ├── sampling.py
│       │   └── metrics.py
│       │
│       ├── screening/
│       │   ├── constraints.py
│       │   ├── fom.py
│       │   └── pareto.py
│       │
│       └── md/
│           ├── parameterize.py
│           ├── build_box.py
│           ├── analyze_equilibration.py
│           └── analyze_nemd.py
│
├── tests/
│   ├── test_units.py
│   ├── test_identity.py
│   ├── test_rdkit_validation.py
│   ├── test_filters.py
│   └── test_fom.py
│
├── reports/
│   ├── data_audit/
│   ├── model_results/
│   └── md_results/
│
└── references/
    └── literature_registry.csv
```

---

# 33. Configuration-over-hardcoding rule

Thresholds should live in configuration files, not scattered through Python code.

Example:

```yaml
# config/screening.yaml

boiling_point_min_K: null
flash_point_min_K: null
relative_permittivity_max: null

environmental_mode: undecided
# allowed future values:
# - non_pfas
# - fluorine_free
```

Until a threshold is formally locked, use `null` / `None` and fail clearly rather than inventing a value.

---

# 34. Testing requirements

At minimum, add tests for:

- unit conversions
- temperature conversion
- dynamic vs kinematic viscosity conversion
- RDKit parsing
- canonical SMILES stability
- fluorine counting
- duplicate detection
- mixture rejection/flagging
- FOM calculation
- hard-constraint logic
- provenance retention

Scientific pipeline code should be testable independently of notebooks.

Notebooks are for exploration and reporting, not the only implementation.

---

# 35. Reproducibility rules

- use a version-controlled repository
- pin major package versions
- use deterministic seeds where appropriate
- save train/validation/test split identifiers
- save model configuration with every model artifact
- record data version/hash
- record preprocessing configuration
- record software environment
- never overwrite raw input data
- never overwrite previous experimental results silently

---

# 36. Codex operating instructions

Any Codex agent working in this repository should follow these rules.

## Before coding

1. Read `PROJECT_SPEC.md`.
2. Inspect the existing repository before creating duplicate utilities.
3. Identify which project stage the requested task belongs to.
4. Check whether the task depends on an unresolved decision.
5. If it does, do not silently decide it.

## During coding

1. Prefer reusable modules under `src/` over notebook-only code.
2. Preserve raw data.
3. Preserve provenance.
4. Keep units explicit.
5. Keep temperature explicit.
6. Add tests for data transformations.
7. Log rejected/filtered records with reasons.
8. Do not silently impute scientific values.
9. Do not fabricate missing property data.
10. Do not substitute model predictions for experiments without a field marking them as predicted.

## After coding

1. Run tests.
2. Report files changed.
3. Report assumptions.
4. Report unresolved issues.
5. Report any data that could not be parsed.
6. Report exact output locations.
7. Do not proceed automatically into a new project phase unless requested.

---

# 37. Things Codex must never do silently

Do not silently:

- switch from single-phase to two-phase cooling
- change the research question
- set `N_F = 0` as the final environmental rule
- invent property thresholds
- average conflicting measurements
- drop temperature information
- mix gas/solid/liquid records
- mix pure compounds and mixtures
- treat predicted database entries as experiments
- replace missing experimental values with LLM guesses
- train on the test set
- use the final test set for model selection
- claim MD proves commercial coolant suitability
- skip force-field validation
- declare a molecule “safe” from structure alone
- declare a molecule “PFAS-free” without the project's chosen explicit rule

---

# 38. Current implementation stage

Current status:

```text
[✓] cooling landscape review
[✓] single-phase immersion chosen
[✓] fluid-focused scope chosen
[✓] first engineering-property review
[✓] first data-availability audit
[✓] experimental dataset construction
[✓] molecular identity / RDKit cleaning
[→] detailed EDA
[ ] baseline models
[ ] GNN property predictors
[ ] generative model
[ ] screening / Pareto front
[ ] finalist selection
[ ] force-field validation
[ ] MD / NEMD
[ ] final comparison
```

The current task is:

\[
\boxed{\text{detailed identity-aware EDA and Gate A preparation}}
\]

Do not begin GNN or generative-model development until the data audit is complete.

---

# 39. Immediate next tasks

## Task 1 — Build ThermoML ingestion

**Status: completed by IFD-003.**

Extract pure-liquid experimental measurements for:

- thermal conductivity
- viscosity
- density
- isobaric heat capacity
- vapor pressure
- boiling temperature
- relative permittivity where available

Preserve:

- temperature
- pressure
- phase
- units
- uncertainty
- method
- compound identity
- DOI/source

## Task 2 — Produce coverage report

**Status: completed by IFD-003 for the raw experimental corpus.**

For each property calculate:

- measurement count
- unique molecule count
- temperature range
- median measurements per molecule
- missingness
- chemistry coverage if identities are available

## Task 3 — Produce overlap report

**Status: completed by IFD-003 for source-provided molecular identities.**

Measure cross-property overlap for unique molecules.

This decides single-task vs multitask learning.

## Task 4 — Identity/RDKit pipeline

**Status: completed by IFD-004 for the current ThermoML corpus.**

After the raw audit:

- join compound metadata
- resolve structures
- parse/sanitize
- canonicalize
- deduplicate
- add descriptors
- retain fluorinated compounds until environmental rule is finalized

---

# 40. Stage gates

## Gate A — before ML

Must have:

- documented data sources
- normalized units
- molecular identities
- coverage report
- overlap report
- trainable target decision
- leakage-safe split strategy

## Gate B — before generation

Must have:

- credible property predictors
- classical baselines
- test-set performance
- uncertainty/error analysis
- screening rules
- baseline fluids

## Gate C — before MD

Must have:

- shortlist from Pareto screening
- structural sanity check
- parameterization route
- known-liquid force-field validation

## Gate D — before final claims

Must have:

- ML prediction uncertainty
- NEMD uncertainty
- model-vs-MD comparison
- explicit limitations
- no claim of experimental/commercial validation

---

# 41. Definition of success

A successful project does not need to discover a commercially deployable fluid.

The project succeeds if it demonstrates a scientifically defensible workflow that:

1. builds a provenance-preserving experimental fluid-property dataset,
2. learns useful structure–property relationships,
3. generates valid novel molecular candidates,
4. screens them using physically meaningful multi-objective criteria,
5. identifies a small Pareto-optimal shortlist,
6. independently validates thermal conductivity for top candidates using MD/NEMD,
7. quantifies disagreement and uncertainty,
8. clearly states what remains experimentally unverified.

---

# 42. Final principle

The project should always follow this evidence hierarchy:

```text
engineering requirement
        ↓
experimental evidence
        ↓
machine-learning prediction
        ↓
multi-objective screening
        ↓
physics simulation
        ↓
candidate recommendation
```

Never reverse the order and never let a model prediction become the requirement it is supposed to satisfy.
