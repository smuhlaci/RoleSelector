from orjson import loads


def set_age_role(role_index: int):
    with open(f"embed_jsons/roles.json", "r") as file:
        roles = loads(file.read())['age_roles']