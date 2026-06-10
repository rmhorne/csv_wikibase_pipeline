from copy import deepcopy
from utils import load_json, write_json


def rewrite_plan(plan, alignment):
    """
    replaces ALL local IDs with Wikibase QIDs
    """

    out = []

    for stmt in plan:
        stmt = deepcopy(stmt)

        if stmt["subject"] in alignment:
            stmt["subject"] = alignment[stmt["subject"]]

        if stmt["object"] in alignment:
            stmt["object"] = alignment[stmt["object"]]

        out.append(stmt)

    return out


def write_resolved_plan(plan, path):
    write_json(plan, path)