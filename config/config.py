import yaml


def get_config():
    with open('config.yaml', 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)


def get_games_config():
    config = get_config()
    if config is None:
        return None
    return config.get("games")


def get_val(config, key):
    return config.get(key)
