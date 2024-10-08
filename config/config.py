import yaml
import os

config_file_path = 'config.yaml'

# 要写入的默认配置内容
default_config = {
    'app': {
        'table_refresh': 3000  # 表格刷新时间 单位毫秒
    },
    'windows': {
        'w': 600,
        'h': 400
    },
    'games': {
        'wu-kong': {
            'name': '黑神话悟空',
            'source': '%APPDATA%/wu-kong/',
            'back': './back'
        },
        'EldenRing': {
            'name': '艾尔登法环',
            'source': '%APPDATA%/EldenRing/',
            'back': './back'
        },
    }
}


def check_file():
    if not os.path.exists(config_file_path):
        # 如果文件不存在，创建并写入内容
        with open(config_file_path, 'w', encoding='utf-8') as config_file:
            yaml.dump(default_config, config_file, allow_unicode=True, default_flow_style=False)
        print(f"{config_file_path} 文件不存在，已创建并写入默认配置。")


def get_config():
    with open('config.yaml', 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)


def update_config(data):
    # 将修改后的数据保存回 YAML 文件
    with open('config.yaml', 'w', encoding='utf-8') as file:
        yaml.dump(data, file, default_flow_style=False, allow_unicode=True)


def get_games_config():
    config = get_config()
    if config is None:
        return None
    return config.get("games")


def get_val(config, key):
    return config.get(key)
