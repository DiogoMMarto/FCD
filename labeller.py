import argparse
import json
import os
import random
from transformers import pipeline
import torch

classifier = None

labels = {} # key: number value: label of category
nodes = {} # key: number value: node info
text = {} # key: number value: text
OPTIONS = [] 
OPTION = None
N = 0
def options_for(n):
    global OPTIONS
    if not os.path.exists("train/labels/label_names.csv"):
        return Exception("train/labels/label_names.csv not found")
    
    with open("train/labels/label_names.csv", 'r') as f:
        for i, line in enumerate(f):
            if i + 1 == n:
                OPTIONS = line.strip().split(";")
                return None
            
    return Exception(f"line {n} not found in train/labels/label_names.csv")

def append_option(_options: list[str]):
    with open("train/labels/label_names.csv", 'a') as f:
        f.write("".join([i + ";" for i in _options[:-1]]) + _options[-1] + "\n")

def printc(*args):
    global N
    print(*args)
    N += 1

def RED(s):
    return "\033[91m" + s + "\033[0m"

def GREEN(s):
    return "\033[92m" + s + "\033[0m"

def CLEAR_LINES(n):
    print('\033[1A\033[2K'*n, end='')
    
def load_files():
    global nodes
    global text
    global labels
    global OPTION
    if not os.path.exists(f"train/labels/labels_{OPTION}.txt"):
        with open(f"train/labels/labels_{OPTION}.txt", 'w') as f:
            pass
    with open(f"train/labels/labels_{OPTION}.txt", 'r') as f:
        for line in f:
            line = line.strip()
            n , label = line.split(":")
            labels[int(n)] = label

    with open(".cache/filtered_and_connections.json", 'r') as f:
        l2 = json.loads(f.read())
    for i in l2:
        nodes[i["number"]] = i

    if not os.path.exists("train/processed/text.json"):
        i = 0
        for root, dirs, files in os.walk("train/processed"):
            for file in files:
                with open(os.path.join(root, file), 'r', encoding="utf-8") as f:
                    i = i +1
                    if i % 100 == 0:
                        print(f"\r{i}/{len(files)}",end="")
                    text[int(file.split(".")[0])] = f.read()
        with open("train/processed/text.json", 'w', encoding="utf-8") as f:
            f.write(json.dumps(text))
        print(f"\r{i}/{len(files)}",end="")
    else:
        with open("train/processed/text.json", 'r', encoding="utf-8") as f:
            text = json.loads(f.read())

def is_labelled(number):
    return number in labels

def get_random():
    global nodes
    global labels
    while True:
        number = random.randint(0, len(nodes))
        if not is_labelled(number) and str(number) in text and number in nodes:
            return number
        
def get_randoms(n):
    global nodes
    global labels
    l = []
    while len(l) < n:
        number = random.randint(0, len(nodes))
        if not is_labelled(number) and str(number) in text and number in nodes and number not in l:
            l.append(number)
    return l

def show_menu(number,auto) -> str:
    global nodes
    global text
    def show_node_info(node,text):
        printc(RED("_"*80))
        printc("Category: " + node["category"])
        printc("Title: " + node["title"])
        printc("Link: " + node["url"])
        printc(RED("_"*80))
        printc(text)

    def show_options():
        def show_option(i):
            return f"({i+1}) {OPTIONS[i]:<25}" if i < len(OPTIONS) else ""
        printc(RED("_"*80))
        for i in range(0,len(OPTIONS),4):
            printc("".join(show_option(k) for k in range(i,i+4)))
    
    node = nodes[number]
    text_ = text[str(number)]
    
    if not auto:
        show_node_info(node,text_)
        show_options()
        printc(RED("_"*80))

    while True:
        try:
            if not auto:
                option = int(input(GREEN("Select an option: ")))
            else:
                option = auto_choice(node,text_)["labels"][0]
                printc("Select option: " + str(option))
                return option
            if option < 0 or option > len(OPTIONS):
                raise ValueError
            return OPTIONS[option]
        except ValueError as e:
            printc("Invalid option. Please try again." + str(e))
        except KeyboardInterrupt:
            return None

def multiple_choice(dataset):
    global classifier
    if classifier is None:
        print("GPU Device Name:", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "No GPU detected")
        classifier = pipeline(
            "zero-shot-classification", 
            model="facebook/bart-large-mnli", 
            device=0 if torch.cuda.is_available() else -1  # Use GPU if available
        )
    prompt = lambda title, text , cat: f"Try to label the category of this news article and give the same importance to each category. This news article is from Portugal and previously it was classified as {cat}. Title: {title} Text: {text}"
    prompts = [
        prompt(title,text_,cat) for _ ,title, text_ , cat in dataset
    ]
    results = classifier(prompts, OPTIONS)
    return [(dataset[i][0],results[i]["labels"][0]) for i in range(len(results))]

def auto_choice(node,text):
    global classifier
    if classifier is None:
        printc("GPU Device Name:", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "No GPU detected")
        classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli", device="cuda" if torch.cuda.is_available() else "cpu")
    return classifier("Try to label the category of this news article and give the same importance to each category. This news article is from Portugal. title:" + node["title"] + "text:" + text, OPTIONS)

def append_label(number, label):
    global labels
    global OPTION
    labels[number] = label
    # append to labels_{OPTION}.txt
    if not os.path.exists(f"train/labels/labels_{OPTION}.txt"):
        with open(f"train/labels/labels_{OPTION}.txt", 'w') as f:
            f.write(f"{number}:{label}\n")
    with open(f"train/labels/labels_{OPTION}.txt", 'a') as f:
        f.write(f"{number}:{label}\n")
        
def extract_title_text(numbers):
    r = []
    for number in numbers:
        node = nodes[number]
        text_ = text[str(number)]
        r.append((number,node["title"],text_,node["category"]))
    return r

def main(auto=False):
    load_files()
    i = 0
    while True:
        printc(i)
        if not auto:
            i += 1
            number = get_random()
            label = show_menu(number, auto)
            if label is None:
                break
            append_label(number, label)
        else:
            i += 100
            numbers = get_randoms(100)
            data = extract_title_text(numbers)
            classification = multiple_choice(data)
            for number , label in classification:
                append_label(number, label)
    return

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--new", nargs="+", help="Create a new label set by reading arguments")
    parser.add_argument("--labels", type=int, default=1, help="Choose the label set to use for the labelling")
    parser.add_argument("--auto", action="store_true", help="If present will try to label automatically")
    args = parser.parse_args()

    if args.new:
        OPTIONS = args.new
        append_option(OPTIONS)
    else:
        OPTION = args.labels
        options_for(OPTION)

    main(args.auto)