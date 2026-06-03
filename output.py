from utils import write_json_file


def write_plan_json(plan, filename="plan_output.json"):
    """
    Full deterministic serialization of statement plan.
    """

    def serialize_qualifiers(qs):
        """
        Convert internal tuple format into clean JSON objects.
        """
        if not qs:
            return []

        return [
            {
                "property": k,
                "value": v
            }
            for (k, v) in qs
        ]

    out = [
        {
            "subject": s.subject,
            "predicate": s.predicate,
            "object": s.object,
            "object_type": s.object_type,
            "action": s.action,
            "qid": s.qid,
            "field_type": s.field_type,

            # provenance
            "source": s.source,

            # FIXED SERIALIZATION (NO RAW TUPLES)
            "references": s.references,

            "qualifiers": serialize_qualifiers(s.qualifiers)
        }
        for s in plan
    ]

    write_json_file(out, filename)


def write_resolution_json(data, filename="resolution_output.json"):
    write_json_file(data, filename)


def write_missing_entities_json(data, filename="missing_entities.json"):
    write_json_file(data, filename)


def write_seed_plan_json(data, filename="entity_seed_plan.json"):
    write_json_file(data, filename)