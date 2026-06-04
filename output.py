from utils import write_json


def write_plan(plan, path):

    def ser(s):
        return {
            "subject": s.subject,
            "subject_label": s.subject_label,
            "predicate": s.predicate,
            "predicate_label": s.predicate_label,
            "object": s.object,
            "object_label": s.object_label,
            "object_type": s.object_type,
            "source": s.source,
            "references": s.references,
            "qualifiers": s.qualifiers
        }

    write_json([ser(x) for x in plan], path)