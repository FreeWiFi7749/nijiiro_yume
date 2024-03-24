import json
import os

def get_reaction_config_path(server_id):
    return f"data/auto_reaction/{server_id}/channel/"

def save_reaction_config(server_id, channel_id, emoji):
    path = get_reaction_config_path(server_id)
    os.makedirs(path, exist_ok=True)
    config_file_path = f"{path}{channel_id}.json"

    if os.path.exists(config_file_path):
        with open(config_file_path, 'r', encoding='utf-8') as config_file:
            try:
                config = json.load(config_file)
            except json.JSONDecodeError:
                config = {}
    else:
        config = {}

    emojis = config.get('emojis', [])
    if emoji not in emojis:
        emojis.append(emoji)
    config['emojis'] = emojis

    with open(config_file_path, 'w', encoding='utf-8') as config_file:
        json.dump(config, config_file)

def remove_reaction_config(server_id, channel_id, emoji=None):
    path = get_reaction_config_path(server_id)
    config_file_path = f"{path}{channel_id}.json"
    
    if os.path.exists(config_file_path):
        with open(config_file_path, 'r', encoding='utf-8') as config_file:
            config = json.load(config_file)
        
        if emoji and emoji in config['emojis']:
            config['emojis'].remove(emoji)
            with open(config_file_path, 'w', encoding='utf-8') as config_file:
                json.dump(config, config_file)
        elif not emoji:
            os.remove(config_file_path)

def load_reaction_config(server_id, channel_id):
    path = get_reaction_config_path(server_id)
    try:
        with open(f"{path}{channel_id}.json", 'r', encoding='utf-8') as config_file:
            return json.load(config_file)
    except FileNotFoundError:
        return None