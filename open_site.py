import json
import time
import requests
import os
import pprint
import re
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed

from neo4j_driver import add_page_to_neo4j , driver

# deterministic hash
def my_hash(s: str):
    h = hashlib.sha256(s.encode('utf-8')).hexdigest()
    return h

def open_site(url:str) -> tuple[str, str]:
    """
    Opens a given URL and reads its content. If the content has already been retrieved, it is read from a cache file.
    The cache file is saved in .cache directory with the name of the url encoded in hex.
    If the content is not in the cache, the function sends a GET request for the given URL and saves the response to the cache.
    :param url: The URL to open
    :return: A tuple with the content of the URL and the path of the cache file
    :raises Exception: If the GET request fails
    """
    hash_url = my_hash(url)
    file_path = '.cache/' + hash_url + ".json"
    if os.path.exists(file_path):
        return read_cache(url) , file_path
        
    response = requests.get(url)

    if response.status_code == 200:        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(response.text)
        return response.text , file_path
    else:
        raise Exception(f"Failed to open site: {response.status_code}")
    
def read_cache(url):
    hash_url = my_hash(url)
    file_path = '.cache/' + hash_url + ".json"
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def parse_url(url_original:str) -> tuple[str,str,str,str]:
    url = url_original.replace("https://www.publico.pt/", "")
    url_split = url.split("/")
    if len(url_split) > 6:
        raise Exception(f"Invalid url: {url}")
    date = url_split[2] + "/" + url_split[1] + "/" + url_split[0]
    category = url_split[3]
    if url_split[4] != "noticia":
        raise Exception(f"Invalid url: {url}")
    title = url_split[5]
    title_split = title.split("?")
    if len(title_split) > 1:
        raise Exception(f"Invalid url: {url}")
    title = title_split[0]
    url = "https://www.publico.pt/" + url_split[0] + "/" + url_split[1] + "/" + url_split[2] + "/" + url_split[3] + "/" + url_split[4] + "/" + title
    return url, date, category, title

def parse_big_file(file_path:str) -> dict:
    filter_larger = {}
    with open(file_path, 'r') as f:
        i = 0
        for line in f:
            line = line.strip()
            json_obj = json.loads(line)
            if json_obj['mime'] != "text/html" or json_obj['status'] != "200":
                continue
            try:
                url , date, category, title = parse_url(json_obj['url'])
            except Exception as e:
                continue
            i += 1
            timestamp = int(json_obj['timestamp'])
            cur_time =  int(filter_larger.get(url, {"timestamp": 0})["timestamp"])
            if timestamp > cur_time:
                filter_larger[url] = {
                                      "length": json_obj['length'], 
                                      "mime": json_obj['mime'],
                                      "status": json_obj['status'],
                                      "url": json_obj['url'],
                                    #   "url": url,
                                      "date": date,
                                      "category": category,
                                      "title": title,
                                      "number": i,
                                      "timestamp": timestamp
                                    }
    return filter_larger

url_pattern = r"https?://[^\s\"'>]+"
url_pattern2 = r"href=\".*\""
def extract_urls(content:str) -> list[str]:
    return re.findall(url_pattern, content) + [ x.replace("href=\"", "").replace("\"", "") for x in re.findall(url_pattern2, content)]

def process_site(url,d) -> tuple[str,list[int]]:
    url , path = open_site(url)
    urls = extract_urls(url)
    urls2 = set()
    for url in urls:
        try:
            r = parse_url(url)
        except Exception as e:
            continue
        urls2.add(r[0])
    connections = []
    for url in urls2:
        if url in d:
            connections.append(d[url]["number"])
    return path , connections
def process_filtered_sites(d):
    results = []
    
    def process_data(data):
        # Local function to process each data entry
        for _ in range(3):  # Retry up to 3 times
            try:
                url = data["url"]
                timestamp = data["timestamp"]
                url = f"https://arquivo.pt/noFrame/replay/{timestamp}id_/{url}"
                path, connections = process_site(url, d)
                data["path"] = path
                data["connections"] = connections
                return data  # Return the modified data on success
            except Exception as e:
                print(f"\n[ERROR] {url} {e}")
                time.sleep(60)  # Delay before retrying
        return None  # Return None if all retries fail

    with ThreadPoolExecutor(max_workers=16) as executor:
        futures = {executor.submit(process_data, data): data for data in d.values()}
        for i, future in enumerate(as_completed(futures), 1):
            print(f"\r{i}/{len(d)}", end="")
            result = future.result()
            if result is not None:
                results.append(result)  # Collect successful results

    return results  # Return list of processed data entries

def main():
    _ , path = open_site("https://arquivo.pt/wayback/cdx?url=publico.pt/*&filter=url:noticia&filter=mime:html&output=json")
    l = parse_big_file(path)
    with open(".cache/filtered.json", 'w') as f:
        f.write(pprint.pformat(l))
    l2 = process_filtered_sites(l)
    with open(".cache/filtered_and_connections.json", 'w') as f:
        f.write(pprint.pformat(l2))
    print()
    for i,item in enumerate(l2):
        print(f"\r{i}/{len(l2)}", end="")
        add_page_to_neo4j(item)
    driver.close()
    print("Done")

if __name__ == "__main__":
    if not os.path.exists(".cache"):
        os.mkdir(".cache")
    main()