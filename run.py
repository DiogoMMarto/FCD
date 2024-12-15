from open_site import *


request_urls = lambda year, month: f"https://arquivo.pt/wayback/cdx?url=publico.pt/{year}/{month if month > 9 else '0'+str(month)}*&filter=url:noticia&filter=mime:html&output=json"

path_list = []
def collect_info(url_):
    _ , path = open_site(url_)
    path_list.append(path)
    with open(path, 'r') as f:
        lines = f.readlines()
        if len(lines) == 100000:
            print("\033[91m", end="")
            print(f"[WARNING] The file has 100000 lines {i}-{j}")
            print("\033[0m", end="")
            path_list.pop()
    
for i in range(1995, 2025):
    for j in range(1, 13):
        collect_info(request_urls(i, j))

request_urls2 = lambda day: f"https://arquivo.pt/wayback/cdx?url=publico.pt/2020/9/{day}*&filter=url:noticia&filter=mime:html&output=json"
request_urls3 = lambda day: f"https://arquivo.pt/wayback/cdx?url=publico.pt/2020/10/{day}*&filter=url:noticia&filter=mime:html&output=json"
request_urls4 = lambda day: f"https://arquivo.pt/wayback/cdx?url=publico.pt/2019/1/{day}*&filter=url:noticia&filter=mime:html&output=json"
for day in range(1, 32):
    collect_info(request_urls2(day))
    collect_info(request_urls3(day))

all_texts = ""
for path in path_list:
    with open(path, 'r') as f:
        all_texts += f.read()
with open("all_requests.txt", 'w') as f:
    f.write(all_texts)
with open("all_requests.txt", 'r') as f:
    lines = f.readlines()
    print("\nNumber of lines in the file: ", len(lines))

l = parse_big_file("all_requests.txt")
with open("filtered.json","w",encoding="utf-8") as f:
    f.write(json.dumps(l))

with open("filtered.json","r",encoding="utf-8") as f:
    l = json.loads(f.read())

def save(l):
    with open("filtered_and_connections.json","w",encoding="utf-8") as f:
        f.write(json.dumps(l2))

l2 = process_filtered_sites(l,0,save_callback=save)
save(l2)

with open("filtered_and_connections.json","r",encoding="utf-8") as f:
    l2 = json.loads(f.read())

print("Inserting data into Neo4j...")

add_all_pages_to_neo4h(l2)

driver.close()

print("\nDone")