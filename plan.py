from dataclasses import dataclass
from typing import Optional, Dict, Any, List


@dataclass
class Statement:
    subject: str
    subject_label: Optional[str]

    predicate: str
    predicate_label: Optional[str]

    object: Optional[str]
    object_label: Optional[str]

    object_type: str  # entity | literal

    source: Dict[str, Any]

    # NEW: row-level traceability
    provenance: Optional[int] = None

    references: List = None
    qualifiers: List = None

    def __post_init__(self):
        self.references = self.references or []
        self.qualifiers = self.qualifiers or []