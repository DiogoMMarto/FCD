# open .cache/folder
# traverse files and if in first 3 lines there is <!doctype html> then rename the file so that it has .html extension

from concurrent.futures import ThreadPoolExecutor
import os
import re


def p(file, root,i):
    print(f"\r{i}", end="")
    if file.endswith(".json"):
        new_name = file.replace(".json", ".html")
        # with open(os.path.join(root, file), "r" , encoding="utf-8") as f:
        #     for _ in range(3):
        #         line = f.readline()
        #         if line == "<!doctype html>\n":
        #             new_name = file.replace(".json", ".html")
        #             break
        os.rename(os.path.join(root, file), os.path.join(root, new_name))

# Thread execution
a = list(os.walk(".cache"))
print("Starting...")
with ThreadPoolExecutor(max_workers=16) as executor:
    i = 0
    for root, dirs, files in a:
        for file in files:
            executor.submit(p, file, root,i)
            i += 1

print("Done")



        