import requests
import platform
import psutil
import pynvml

def get_location():
    try:
        # Получаем IP-адрес и информацию о местоположении
        response = requests.get('https://ipinfo.io')
        data = response.json()

        # Извлекаем нужные данные
        ip = data.get('ip')
        city = data.get('city')
        region = data.get('region')
        country = data.get('country')
        loc = data.get('loc')  # Широта и долгота

        # Выводим информацию
        print("\n=== Информация о местоположении ===")
        print(f"IP: {ip}")
        print(f"Город: {city}")
        print(f"Регион: {region}")
        print(f"Страна: {country}")
        print(f"Координаты: {loc}")

    except Exception as e:
        print(f"Произошла ошибка при определении местоположения: {e}")

def get_system_info():
    print("\n=== Информация о системе ===")
    # Информация об операционной системе
    print(f"Операционная система: {platform.system()} {platform.release()}")
    print(f"Версия ОС: {platform.version()}")
    print(f"Архитектура: {platform.machine()}")
    print(f"Процессор: {platform.processor()}")
    print(f"Имя компьютера: {platform.node()}")

    # Информация о процессоре
    print(f"Количество ядер: {psutil.cpu_count(logical=False)}")
    print(f"Логических процессоров: {psutil.cpu_count(logical=True)}")

    # Информация об оперативной памяти
    mem = psutil.virtual_memory()
    print(f"Оперативная память: {mem.total / (1024 ** 3):.2f} GB")
    print(f"Доступно памяти: {mem.available / (1024 ** 3):.2f} GB")

    # Информация о дисках
    print("\n=== Диски ===")
    partitions = psutil.disk_partitions()
    for partition in partitions:
        print(f"Устройство: {partition.device}")
        print(f"  Точка монтирования: {partition.mountpoint}")
        print(f"  Файловая система: {partition.fstype}")
        usage = psutil.disk_usage(partition.mountpoint)
        print(f"  Всего места: {usage.total / (1024 ** 3):.2f} GB")
        print(f"  Использовано: {usage.percent}%")

    # Информация о GPU
    get_gpu_info()

    # Информация о сети
    print("\n=== Сетевые подключения ===")
    addrs = psutil.net_if_addrs()
    for interface, addresses in addrs.items():
        print(f"Интерфейс: {interface}")
        for addr in addresses:
            if addr.family == 'AF_INET':  # Исправлено на строку
                print(f"  IP-адрес: {addr.address}")
                print(f"  Маска подсети: {addr.netmask}")
            elif addr.family == 'AF_INET6':  # Исправлено на строку
                print(f"  IPv6-адрес: {addr.address}")

    # Информация о текущих подключениях
    connections = psutil.net_connections()
    print("\n=== Активные сетевые подключения ===")
    for conn in connections:
        if conn.status == psutil.CONN_ESTABLISHED:
            print(f"Протокол: {conn.type}")
            print(f"  Локальный адрес: {conn.laddr.ip}:{conn.laddr.port}")
            print(f"  Удаленный адрес: {conn.raddr.ip}:{conn.raddr.port}")


def get_gpu_info():
    try:
        pynvml.nvmlInit()
        print("\n=== Графические процессоры (GPU) ===")
        device_count = pynvml.nvmlDeviceGetCount()
        for i in range(device_count):
            handle = pynvml.nvmlDeviceGetHandleByIndex(i)
            name = pynvml.nvmlDeviceGetName(handle)

            # Проверяем тип name и декодируем, если это bytes
            if isinstance(name, bytes):
                name = name.decode('utf-8')

            memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
            utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)
            print(f"GPU {i}: {name}")
            print(f"  Использовано памяти: {memory_info.used / 1024 ** 2:.2f} MB")
            print(f"  Всего памяти: {memory_info.total / 1024 ** 2:.2f} MB")
            print(f"  Загрузка GPU: {utilization.gpu}%")
    except Exception as e:
        print(f"Ошибка при получении информации о GPU: {e}")
    finally:
        pynvml.nvmlShutdown()

if __name__ == "__main__":
    get_location()  # Получаем информацию о местоположении
    get_system_info()  # Получаем информацию о системе