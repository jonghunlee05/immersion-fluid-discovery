"""Deterministic RDKit validation for source-provided molecular identities."""

from __future__ import annotations

from dataclasses import dataclass

from rdkit import Chem, rdBase
from rdkit.Chem import Crippen, Descriptors, rdMolDescriptors


@dataclass(frozen=True)
class ValidatedStructure:
    """Canonical identity and descriptors derived from one sanitized structure."""

    canonical_smiles: str
    isomeric_smiles: str
    inchi: str
    inchikey: str
    molecular_formula: str
    molecular_weight: float
    logp: float
    tpsa: float
    atom_count: int
    heavy_atom_count: int
    ring_count: int
    heteroatom_count: int
    fluorine_count: int
    formal_charge: int
    rotatable_bond_count: int
    fragment_count: int
    stereocenter_count: int
    unassigned_stereocenter_count: int
    stereochemistry_status: str


class StructureValidationError(ValueError):
    """Raised when a source identity cannot produce one sanitized molecule."""


def validate_structure(
    *, inchi: str | None = None, smiles: str | None = None
) -> ValidatedStructure:
    """Parse, sanitize, canonicalize, and describe a source-provided structure."""

    cleaned_inchi = _clean(inchi)
    cleaned_smiles = _clean(smiles)
    with rdBase.BlockLogs():
        if cleaned_inchi:
            molecule = Chem.MolFromInchi(cleaned_inchi, sanitize=True, removeHs=True)
        elif cleaned_smiles:
            molecule = Chem.MolFromSmiles(cleaned_smiles, sanitize=True)
        else:
            raise StructureValidationError("missing_structure_identifier")
    if molecule is None:
        raise StructureValidationError("rdkit_parse_failed")

    try:
        with rdBase.BlockLogs():
            Chem.SanitizeMol(molecule)
            derived_inchi = Chem.MolToInchi(molecule)
            derived_inchikey = Chem.MolToInchiKey(molecule)
    except Exception as exc:  # RDKit exposes multiple exception classes by build.
        raise StructureValidationError("rdkit_sanitization_failed") from exc
    if not derived_inchi or not derived_inchikey:
        raise StructureValidationError("rdkit_identity_generation_failed")

    stereocenters = Chem.FindMolChiralCenters(
        molecule, includeUnassigned=True, includeCIP=True
    )
    unassigned_stereocenters = [
        center for center in stereocenters if center[1] == "?"
    ]

    return ValidatedStructure(
        canonical_smiles=Chem.MolToSmiles(
            molecule, canonical=True, isomericSmiles=False
        ),
        isomeric_smiles=Chem.MolToSmiles(
            molecule, canonical=True, isomericSmiles=True
        ),
        inchi=derived_inchi,
        inchikey=derived_inchikey,
        molecular_formula=rdMolDescriptors.CalcMolFormula(molecule),
        molecular_weight=Descriptors.MolWt(molecule),
        logp=Crippen.MolLogP(molecule),
        tpsa=rdMolDescriptors.CalcTPSA(molecule),
        atom_count=Chem.AddHs(molecule).GetNumAtoms(),
        heavy_atom_count=molecule.GetNumHeavyAtoms(),
        ring_count=rdMolDescriptors.CalcNumRings(molecule),
        heteroatom_count=rdMolDescriptors.CalcNumHeteroatoms(molecule),
        fluorine_count=sum(
            1 for atom in molecule.GetAtoms() if atom.GetAtomicNum() == 9
        ),
        formal_charge=sum(atom.GetFormalCharge() for atom in molecule.GetAtoms()),
        rotatable_bond_count=rdMolDescriptors.CalcNumRotatableBonds(molecule),
        fragment_count=len(Chem.GetMolFrags(molecule)),
        stereocenter_count=len(stereocenters),
        unassigned_stereocenter_count=len(unassigned_stereocenters),
        stereochemistry_status=(
            "unspecified" if unassigned_stereocenters else "specified_or_achiral"
        ),
    )


def _clean(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None
