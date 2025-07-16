import threading    # для создания и управления потоками
import requests     # для выполнения HTTP-запросов
import time         # для замера времени выполнения
import queue


urls = ["https://deelay.me/2000/https://example.com"] * 5
print_lock = threading.Lock() # defend for print
task_queue = queue.Queue()

def worker():
    while True:
        url = task_queue.get()
        if url is None:
            break
        with print_lock:
            print(f"[{threading.current_thread().name}] Starting {url}")
        response = requests.get(url)
        with print_lock:
            print(f"[{threading.current_thread().name}] {url} done with status {response.status_code}")
        task_queue.task_done()

start = time.time()
threads = []

for _ in range(3):
    t = threading.Thread(target=worker)
    t.start()
    threads.append(t)

for url in urls:
    task_queue.put(url)

task_queue.join()

for _ in threads:
    task_queue.put(None)

for t in threads: 
    t.join()

print("Time:", time.time() - start)
