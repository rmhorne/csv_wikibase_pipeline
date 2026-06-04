#frbr.py
from dataclasses import dataclass
from typing import Dict, Any, List, Tuple


@dataclass
class FRBRNode:
    level: str
    qid: str
    source_qid: str
    predicate: str


def build_frbr_chain(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Returns FRBR chain as-is from config, validated.

    No logic here — only normalization layer.
    """
    chain = config.get("frbr_chain", [])

    if not isinstance(chain, list):
        raise ValueError("frbr_chain must be a list")

    return chain


def get_frbr_level(node: Dict[str, Any]) -> str:
    return node.get("to", {}).get("level")


def get_frbr_predicate(node: Dict[str, Any]) -> str:
    return node.get("predicate")


def get_match_fields(node: Dict[str, Any]) -> List[str]:
    return node.get("match_fields", [])


def get_mode(node: Dict[str, Any]) -> str:
    return node.get("mode", "create_or_match")


def get_strategy(node: Dict[str, Any]) -> str:
    return node.get("strategy", "exact")