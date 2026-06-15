# plan.py
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List

@dataclass
class Statement:
    subject:         str
    subject_label:   Optional[str]
    predicate:       str
    predicate_label: Optional[str]
    object:          Optional[str]
    object_label:    Optional[str]
    object_type:     str            # "entity" | "literal"
    source:          Dict[str, Any]
    provenance:      Optional[int]  = None
    references:      List           = field(default_factory=list)
    qualifiers:      List           = field(default_factory=list)
