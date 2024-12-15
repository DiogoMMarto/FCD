import json
import pprint
import time
import requests
import os
import re
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
import bs4 as bs
import spacy as sp
from sklearn.feature_extraction.text import TfidfVectorizer
from neo4j_driver import add_all_pages_to_neo4h, driver

DEST_FOLDER = "train/processed/"

# deterministic hash
def my_hash(s: str):
    h = hashlib.sha256(s.encode('utf-8')).hexdigest()
    return h

def open_site(url:str,cached:bool = True) -> tuple[str, str]:
    hash_url = my_hash(url)
    file_path = '.cache/' + hash_url + ".json"
    if os.path.exists(file_path):
        return read_cache(url) , file_path
        
    response = requests.get(url)

    if response.status_code == 200:        
        if cached:
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
    # TODO: CHECK IF things after ? change page content
    url = url_original.replace("https://www.publico.pt/", "")
    url_split = url.split("/")
    if len(url_split) > 6:
        raise Exception(f"Invalid url: {url}")
    date = url_split[2] + "/" + url_split[1] + "/" + url_split[0]
    category = url_split[3]
    if url_split[4] != "noticia":
        raise Exception(f"Invalid url: {url}")
    title = url_split[5]
    # split by ? or #
    title_split = re.split(r"[#?]", title)
    if len(title_split) > 1:
        raise Exception(f"Invalid url: {url}")
    title = title_split[0]
    url = "https://www.publico.pt/" + url_split[0] + "/" + url_split[1] + "/" + url_split[2] + "/" + url_split[3] + "/" + url_split[4] + "/" + title
    return url, date, category, title

def parse_big_file(file_path:str) -> dict:
    filter_larger = {}
    with open(file_path, 'r') as f:
        n = 0
        for line in f:
            n = n + 1
            if n % 1000 == 0:
                print(f"\r{n}", end="")
            line = line.strip()
            json_obj = json.loads(line)
            if json_obj['mime'] != "text/html" or json_obj['status'] != "200":
                continue
            try:
                url , date, category, title = parse_url(json_obj['url'])
            except Exception as e:
                continue
            timestamp = int(json_obj['timestamp'])
            cur_time =  int(filter_larger.get(url, {"timestamp": 0})["timestamp"])
            if timestamp > cur_time:
                filter_larger[url] = {
                                      "url": url,
                                      "date": date,
                                      "category": category,
                                      "title": title,
                                      "number": n,
                                      "timestamp": timestamp
                                    }
    print(f"\r{n}\n", end="")
    return filter_larger


url_pattern = r"https?://[^\s\"'>]+"
def extract_urls(content:str) -> set[str]:
    # TODO: CHECK IF URL_2 IS NEEDED
    # url_pattern2 = r"href=\".*\""
    # for x in set(re.findall(url_pattern2, content)):
    #     x2 = x.replace("href=\"", "").replace("\"", "")
    #     if len(x2) > 0 and x2[0] == "/":
    #         x2 = "https://www.publico.pt" + x2
    #     r.add(x2)
    r = set(re.findall(url_pattern, content))
    return r

def process_site(_url,d,number) -> tuple[str,list[int]]:
    url_file , _ = open_site(_url, False)
    urls = extract_urls(url_file)
    urls2 = list()
    for url in urls:
        try:
            r = parse_url(url)
        except Exception as e:
            continue
        urls2.append(r[0])
    connections = []
    for url in urls2:
        if url in d:
            connections.append(d[url]["number"])
    textR = extract_text(url_file)
    textC = clean_text(textR)
    path = DEST_FOLDER + str(number) + ".txt"
    with open(path, 'w', encoding='utf-8') as f:
        f.write(textC)
    return path , connections

def process_filtered_sites(d,n = 0, save_callback = lambda x: None):
    results = []
    
    def process_data(data):
        # Local function to process each data entry
        for _ in range(3):  # Retry up to 3 times
            try:
                url = data["url"]
                timestamp = data["timestamp"]
                url = f"https://arquivo.pt/noFrame/replay/{timestamp}/{url}"
                path, connections = process_site(url, d, data["number"])
                data["path"] = path
                data["connections"] = connections
                return data  # Return the modified data on success
            except Exception as e:
                print(f"\n[ERROR] {data} {url} {e} ")
                time.sleep(60)  # Delay before retrying
        return None  # Return None if all retries fail

    with ThreadPoolExecutor(max_workers=32) as executor:
        futures = {executor.submit(process_data, data): data for i,data in enumerate(d.values()) if i >= n}
        for i, future in enumerate(as_completed(futures), n):
            result = future.result()
            # print(f"\r{i}/{len(d)}", end="")
            print(i)
            # if i % 1000 == 0:
            #     save_callback(results.copy())
            if result is not None:
                results.append(result)  # Collect successful results

    print("\nDone")

    return results  # Return list of processed data entries

def extract_text(content:str) -> str:
    soup = bs.BeautifulSoup(content, 'html.parser')
    # get text from only elements inside a div with the class "story__body" and "story__headline"
    text = soup.find("h1", class_="story__headline").get_text() 
    text = soup.find("div", class_="story__body").get_text() + text
    # replace newlines with spaces and multiple spaces with single spaces
    text = re.sub(r'\n+', ' ', text)
    text = re.sub(r'\d+', 'NUM', text)
    return text
    
nlp = sp.load("pt_core_news_lg")
def clean_text(text:str) -> str:
    # use spacy to clean the text
    # remove stop words
    # lemmatize
    doc = nlp(text)
    text = " ".join(
        [token.lemma_ for token in doc 
         if not token.is_stop and not token.is_punct])
    return text


def tfidf(documents) -> dict:
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(documents)
    feature_names = vectorizer.get_feature_names_out()
    dense_tfidf = tfidf_matrix.todense()
    return dense_tfidf , feature_names

def main():
    _ , path = open_site("https://arquivo.pt/wayback/cdx?url=publico.pt/*&filter=url:noticia&filter=mime:html&output=json")

    l = parse_big_file(path)
    with open(".cache/filtered.json", 'w') as f:
        f.write(pprint.pformat(l))

    l2 = process_filtered_sites(l)
    with open(".cache/filtered_and_connections.json", 'w') as f:
        f.write(json.dumps(l2))
    with open(".cache/filtered_and_connections.json", 'r') as f:
        s = f.read()
        l2 = json.loads(s.replace("'","\""))
    print("Inserting data into Neo4j...")
    add_all_pages_to_neo4h(l2)
    driver.close()
    print("\nDone")

if __name__ == "__main__":
    if not os.path.exists(".cache"):
        os.mkdir(".cache")
    main()