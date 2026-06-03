from .base import BaseExecutor
from wikibase_search import get_session, search_entity
from utils import normalize_text
from output import (
    write_resolution_json,
    write_missing_entities_json,
    write_seed_plan_json
)


class SimulateExecutor(BaseExecutor):
    def setup(self):
        self.session = get_session()

    def process(self, plan):
        seen = set()
        out = []
        missing = {}
        seed_plan = []

        total = len(plan)
        print(f"[SIMULATE] total statements: {total}", flush=True)

        for i, s in enumerate(plan):
            if i % 10 == 0:
                print(f"[SIMULATE] {i}/{total}", flush=True)

            if s.object_type != "entity":
                continue

            label = normalize_text(s.object)
            if not label:
                continue

            field_type = normalize_text(getattr(s, "field_type", "entity"), lower=True) or "entity"

            key = (label, field_type)
            if key in seen:
                continue

            seen.add(key)

            try:
                result = search_entity(self.session, label, field_type=field_type)
                matches = result["raw"]
                filtered = result["filtered"]
            except Exception as e:
                print(f"❌ search failed for {label}: {e}", flush=True)
                matches, filtered = [], []

            out.append({
                "label": label,
                "field_type": field_type,
                "source": getattr(s, "references", []),
                "matches": matches,
                "filtered_matches": filtered
            })

            if not filtered:
                missing.setdefault(label, {
                    "label": label,
                    "field_type": field_type,
                    "count": 0
                })["count"] += 1

                seed_plan.append({
                    "label": label,
                    "type_guess": field_type,
                    "status": "to_create"
                })

        write_resolution_json(out)
        write_missing_entities_json(missing)
        write_seed_plan_json(seed_plan)

        print(f"✔ resolution_output.json written ({len(out)})", flush=True)