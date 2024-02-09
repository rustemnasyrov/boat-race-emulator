import logging

_logger = None

def create_logger(filename, use_formatter = True):
    # Создаем объект логгера
    logger = logging.getLogger(__name__)

    # Устанавливаем уровень логирования
    logger.setLevel(logging.INFO)

    # Создаем обработчик для записи в файл
    file_handler = logging.FileHandler(filename)

    # Устанавливаем уровень логирования для обработчика
    file_handler.setLevel(logging.INFO)

    if use_formatter:
        # Создаем форматтер для сообщений лога
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # Устанавливаем форматтер для обработчика
        file_handler.setFormatter(formatter)

    # Добавляем обработчик к логгеру
    logger.addHandler(file_handler)

    return logger

def get_logger():
    global _logger
    if not _logger:
        _logger = create_logger('main.log')
    return _logger


def log_info(message):
    get_logger().info(message)
    pass

