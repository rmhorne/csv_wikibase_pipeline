from copy import deepcopy


def rewrite_plan_with_qids(plan, id_map):
    new_plan = []

    for stmt in plan:
        stmt = deepcopy(stmt)

        orig_s = stmt["subject"]
        orig_o = stmt["object"]

        if stmt["subject"] in id_map:
            stmt["subject"] = id_map[stmt["subject"]]

        if stmt["object"] in id_map:
            stmt["object"] = id_map[stmt["object"]]

        stmt.setdefault("qualifiers", []).append({
            "local_subject": orig_s,
            "local_object": orig_o,
            "resolved_subject": stmt["subject"],
            "resolved_object": stmt["object"]
        })

        new_plan.append(stmt)

    return new_plan