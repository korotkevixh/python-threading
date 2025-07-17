import multiprocessing
import requests
import time


# ----------- НАСТРОЙКИ -----------

NUM_WORKERS = 3
urls = ["https://deelay.me/2000/https://example.com"] * 5

# ----------- ГЛОБАЛЬНЫЕ ОБЪЕКТЫ -----------

task_queue = multiprocessing.JoinableQueue()
done_event = multiprocessing.Event()
print_lock = multiprocessing.Lock()  # чтобы не мешались выводы

# ----------- РАБОЧИЙ ПРОЦЕСС -----------

def worker():
    while True:
        url = task_queue.get()
        if url is None:
            task_queue.task_done()
            break

        with print_lock:
            print(f"[{multiprocessing.current_process().name}] 🔄 Начал загрузку: {url}")

        try:
            response = requests.get(url)
            status = response.status_code
        except Exception as e:
            status = f"Ошибка: {e}"

        with print_lock:
            print(f"[{multiprocessing.current_process().name}] ✅ Завершил: {url} [{status}]")

        task_queue.task_done()

# ----------- УВЕДОМИТЕЛЬ О ЗАВЕРШЕНИИ -----------

def notify_when_done():
    task_queue.join()
    done_event.set()

# ----------- ЗАПУСК -----------

def main():
    start = time.time()

    # Создаём и запускаем воркеры
    processes = []
    for i in range(NUM_WORKERS):
        p = multiprocessing.Process(target=worker, name=f"Worker-{i+1}")
        p.start()
        processes.append(p)

    notifier = multiprocessing.Process(target=notify_when_done)
    notifier.start()

    # Кладём задачи в очередь
    for url in urls:
        task_queue.put(url)

    # Ждём завершения
    done_event.wait()
    with print_lock:
        print("✅ Все задачи завершены!")

    # Завершаем процессы
    for _ in processes:
        task_queue.put(None)

    for p in processes:
        p.join()

    notifier.join()

    print(f"⏱ Общее время: {round(time.time() - start, 2)} сек.")

# ----------- СТАРТ ПРОГРАММЫ -----------

if __name__ == "__main__":
    main()
