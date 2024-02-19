import pygame

# Инициализация Pygame
pygame.init()

# Загрузка звукового файла
sound_file = "horn.wav"  # Укажите путь к вашему звуковому файлу
pygame.mixer.music.load(sound_file)

# Воспроизведение звука
pygame.mixer.music.play()

# Завершение Pygame (не блокирует выполнение)
pygame.quit()
