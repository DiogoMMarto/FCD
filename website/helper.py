

import json
import random

pallete = {}
def color_category(category):
    global pallete
    if category not in pallete:
        pallete[category] = f"#{''.join([str(random.randint(0, 255)) for _ in range(3)])}"
    return pallete[category]

class Node:
    def __init__(self, data, connections):
        self.category = data['category']
        self.date = data['date']
        self.length = data['length']
        self.mime = data['mime']
        self.number = data['number']
        self.path = data['path']
        self.status = data['status']
        self.timestamp = data['timestamp']
        self.title = data['title']
        self.url = data['url']
        self.connections = connections
        self.color = color_category(self.category)

    def get_arquive_link(self):
        return f"https://arquivo.pt/noFrame/replay/{self.timestamp}id_/{self.url}"


    def to_json(self) -> str:
        return {
            "category": self.category,
            "date": self.date,
            # "length": self.length,
            # "mime": self.mime,
            "id": self.number,
            "path": self.path,
            # "status": self.status,
            "timestamp": self.timestamp,
            "title": self.title,
            # "url": self.url,
            "connections": self.connections,
            "color": self.color,
            "arquive_link": self.get_arquive_link(),
            "connections": self.connections
        }
    
def node_list_to_json(nodes):
    return json.dumps([node.to_json() for node in nodes])