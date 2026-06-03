from utils import write_json_file


def write_resolution_json(data, filename="resolution_output.json"):
    write_json_file(data, filename)


def write_missing_entities_json(data, filename="missing_entities.json"):
    write_json_file(data, filename)


def write_seed_plan_json(data, filename="entity_seed_plan.json"):
    write_json_file(data, filename)
