import logging

_main_logger = None

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
    
def main_logger():
    global _main_logger
    if not _main_logger:
        _main_logger = create_logger('main.log')
    return _main_logger

if __name__ == '__main__':
    main_logger().info('Test. Hello WOrld')
    main_logger().info('Test2. Hello WOrld')
    
    
    logger = create_logger('test.log', False)
    logger.info('989898')    
