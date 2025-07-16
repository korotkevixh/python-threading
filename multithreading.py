import threading
import queue
import requests
import time

# ----------- НАСТРОЙКИ -----------

NUM_WORKERS = 3
urls = ["https://deelay.me/2000/https://example.com"] * 5

# ----------- ГЛОБАЛЬНЫЕ ОБЪЕКТЫ -----------

task_queue = queue.Queue()
print_lock = threading.Lock()
done_event = threading.Event()
thread_data = threading.local()

# ----------- ОТЛОЖЕННАЯ ЗАДАЧА (Timer) -----------

def delayed_task():
    with print_lock:
        print("🕒 [Timer] Отложенная задача выполнена!")

timer = threading.Timer(1.0, delayed_task)
timer.start()

# ----------- РАБОЧИЙ ПОТОК -----------

def worker():
    thread_data.start_time = time.time()

    while True:
        url = task_queue.get()
        if url is None:
            break  # сигнал завершения

        with print_lock:
            print(f"[{threading.current_thread().name}] 🔄 Начал загрузку: {url} "
                  f"(инициализировался в {round(thread_data.start_time, 2)})")

        try:
            response = requests.get(url)
            status = response.status_code
        except Exception as e:
            status = f"Ошибка: {e}"

        with print_lock:
            print(f"[{threading.current_thread().name}] ✅ Завершил: {url} [{status}]")

        task_queue.task_done()

# ----------- УВЕДОМИТЕЛЬ О ЗАВЕРШЕНИИ -----------

def notify_when_done():
    task_queue.join()
    done_event.set()

# ----------- ЗАПУСК -----------

def main():
    start = time.time()

    # Создаём и запускаем воркеры
    threads = []
    for i in range(NUM_WORKERS):
        t = threading.Thread(target=worker, name=f"Worker-{i+1}")
        t.start()
        threads.append(t)

    # Запускаем отдельный поток, который сообщит, когда всё будет готово
    notifier = threading.Thread(target=notify_when_done)
    notifier.start()

    # Кладём задачи в очередь
    for url in urls:
        task_queue.put(url)

    # Ждём сигнал о завершении всех задач
    done_event.wait()
    with print_lock:
        print("✅ Все задачи завершены!")

    # Отправляем сигнал потокам остановиться
    for _ in threads:
        task_queue.put(None)

    # Дожидаемся завершения потоков
    for t in threads:
        t.join()

    notifier.join()
    timer.join()

    print(f"⏱ Общее время: {round(time.time() - start, 2)} сек.")

# ----------- СТАРТ ПРОГРАММЫ -----------

if __name__ == "__main__":
    main()
