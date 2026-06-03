from dataclasses import dataclass, field
from typing import Literal, Optional, List, Tuple, Dict, Any

ObjectType = Literal["entity", "literal"]
ActionType = Literal["create", "reuse"]


@dataclass
class Statement:
    subject: str
    predicate: str
    object: str
    object_type: ObjectType
    action: ActionType = "reuse"
    qid: Optional[str] = None
    field_type: Optional[str] = None

    source: Optional[Dict[str, Any]] = None

    references: List[str] = field(default_factory=list)

    qualifiers: List[Tuple[str, str]] = field(default_factory=list)

    qualifier_role: Optional[str] = None
    confidence: Optional[float] = None