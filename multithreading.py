import threading    # для создания и управления потоками
import requests     # для выполнения HTTP-запросов
import time         # для замера времени выполнения


urls = ["https://deelay.me/2000/https://example.com"] * 5

def download(url):
    print(f"Starting {url}")
    response = requests.get(url)
    print(f"{url} done with status {response.status_code}")

start = time.time()
threads = []

for url in urls:
    t = threading.Thread(target=download, args=(url,))
    t.start()
    threads.append(t)

for t in threads: 
    t.join()

print("Time:", time.time() - start)
