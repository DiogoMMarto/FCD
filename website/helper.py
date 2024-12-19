

import json
import random

pallete = {}
def color_category(category):
    global pallete
    if category not in pallete:
        color = [str(random.randint(0, 255)) for _ in range(3)]
        while check_if_color_too_dark_or_light((int(color[0]), int(color[1]), int(color[2]))):
            color = [str(random.randint(0, 255)) for _ in range(3)]
        pallete[category] = color_to_string(color)
    return pallete[category]

def check_if_color_too_dark_or_light(color):
    r, g, b = color
    c = (r*0.3 + g*0.50 + b*0.2) / 3
    return 100 < c < 150

def color_to_string(color):
    return f"rgb({color[0]}, {color[1]}, {color[2]})"

class Node:
    def __init__(self, data, connections):
        self.category = data['category']
        self.date = data['date']
        self.number = data['number']
        self.path = data['path']
        self.timestamp = data['timestamp']
        self.title = data['title']
        self.url = data['url']
        self.connections = connections
        self.color = color_category(self.category)

    def get_arquive_link(self):
        return f"https://arquivo.pt/noFrame/replay/{self.timestamp}/{self.url}"


    def to_json(self) -> str:
        return {
            "category": self.category,
            "date": self.date,
            "id": self.number,
            "path": self.path,
            "timestamp": self.timestamp,
            "title": self.title,
            "connections": self.connections,
            "color": self.color,
            "arquive_link": self.get_arquive_link(),
            "connections": self.connections
        }
    
def node_list_to_json(nodes):
    return json.dumps([node.to_json() for node in nodes])