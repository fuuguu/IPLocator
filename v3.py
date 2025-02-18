import os
import platform
import requests
import psutil
import pynvml


def create_hidden_folder(folder_path):
    """Создаёт скрытую папку по указанному пути."""
    try:
        # Создаём папку, если её нет
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        # Устанавливаем атрибут "скрытый" (для Windows)
        if platform.system() == "Windows":
            import ctypes
            ctypes.windll.kernel32.SetFileAttributesW(folder_path, 2)  # 2 = скрытый атрибут
        else:
            # Для Linux/macOS просто добавляем точку в начало имени папки
            hidden_folder = os.path.join(os.path.dirname(folder_path), f".{os.path.basename(folder_path)}")
            os.rename(folder_path, hidden_folder)
            folder_path = hidden_folder

        print(f"Скрытая папка создана: {folder_path}")
        return folder_path
    except Exception as e:
        print(f"Ошибка при создании скрытой папки: {e}")
        return None


def get_location():
    try:
        response = requests.get('https://ipinfo.io')
        data = response.json()
        ip = data.get('ip')
        city = data.get('city')
        region = data.get('region')
        country = data.get('country')
        loc = data.get('loc')
        return f"""
=== Информация о местоположении ===
IP: {ip}
Город: {city}
Регион: {region}
Страна: {country}
Координаты: {loc}
"""
    except Exception as e:
        return f"Произошла ошибка при определении местоположения: {e}"


def get_system_info():
    info = "\n=== Информация о системе ===\n"
    info += f"Операционная система: {platform.system()} {platform.release()}\n"
    info += f"Версия ОС: {platform.version()}\n"
    info += f"Архитектура: {platform.machine()}\n"
    info += f"Процессор: {platform.processor()}\n"
    info += f"Имя компьютера: {platform.node()}\n"
    info += f"Количество ядер: {psutil.cpu_count(logical=False)}\n"
    info += f"Логических процессоров: {psutil.cpu_count(logical=True)}\n"

    mem = psutil.virtual_memory()
    info += f"Оперативная память: {mem.total / (1024 ** 3):.2f} GB\n"
    info += f"Доступно памяти: {mem.available / (1024 ** 3):.2f} GB\n"

    info += "\n=== Диски ===\n"
    partitions = psutil.disk_partitions()
    for partition in partitions:
        info += f"Устройство: {partition.device}\n"
        info += f"  Точка монтирования: {partition.mountpoint}\n"
        info += f"  Файловая система: {partition.fstype}\n"
        usage = psutil.disk_usage(partition.mountpoint)
        info += f"  Всего места: {usage.total / (1024 ** 3):.2f} GB\n"
        info += f"  Использовано: {usage.percent}%\n"

    info += get_gpu_info()

    info += "\n=== Сетевые подключения ===\n"
    addrs = psutil.net_if_addrs()
    for interface, addresses in addrs.items():
        info += f"Интерфейс: {interface}\n"
        for addr in addresses:
            if addr.family == 'AF_INET':
                info += f"  IP-адрес: {addr.address}\n"
                info += f"  Маска подсети: {addr.netmask}\n"
            elif addr.family == 'AF_INET6':
                info += f"  IPv6-адрес: {addr.address}\n"

    info += "\n=== Активные сетевые подключения ===\n"
    connections = psutil.net_connections()
    for conn in connections:
        if conn.status == psutil.CONN_ESTABLISHED:
            info += f"Протокол: {conn.type}\n"
            info += f"  Локальный адрес: {conn.laddr.ip}:{conn.laddr.port}\n"
            info += f"  Удаленный адрес: {conn.raddr.ip}:{conn.raddr.port}\n"

    return info


def get_gpu_info():
    try:
        pynvml.nvmlInit()
        gpu_info = "\n=== Графические процессоры (GPU) ===\n"
        device_count = pynvml.nvmlDeviceGetCount()
        for i in range(device_count):
            handle = pynvml.nvmlDeviceGetHandleByIndex(i)
            name = pynvml.nvmlDeviceGetName(handle)
            if isinstance(name, bytes):
                name = name.decode('utf-8')
            memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
            utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)
            gpu_info += f"GPU {i}: {name}\n"
            gpu_info += f"  Использовано памяти: {memory_info.used / 1024 ** 2:.2f} MB\n"
            gpu_info += f"  Всего памяти: {memory_info.total / 1024 ** 2:.2f} MB\n"
            gpu_info += f"  Загрузка GPU: {utilization.gpu}%\n"
        return gpu_info
    except Exception as e:
        return f"Ошибка при получении информации о GPU: {e}"
    finally:
        pynvml.nvmlShutdown()


def save_to_txt(data, folder_path, filename="system_info.txt"):
    """Сохраняет данные в файл внутри скрытой папки."""
    try:
        file_path = os.path.join(folder_path, filename)
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(data)
        print(f"Файл сохранён: {file_path}")
    except Exception as e:
        print(f"Ошибка при сохранении файла: {e}")


if __name__ == "__main__":
    # Путь к скрытой папке
    hidden_folder_path = os.path.join(os.path.expanduser("~"), "HiddenSystemInfo")  # В домашней директории пользователя

    # Создаём скрытую папку
    hidden_folder = create_hidden_folder(hidden_folder_path)
    if hidden_folder:
        # Получаем данные
        location_info = get_location()
        system_info = get_system_info()
        full_info = location_info + system_info

        # Сохраняем данные в файл
        save_to_txt(full_info, hidden_folder)