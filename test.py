from PIL import Image

# Загрузка изображения
image_path = 'assets/frame.png'  # Укажите путь к вашему изображению
image = Image.open(image_path)

# Конвертация изображения в 1-битный режим
image_1bit = image.convert('1')

# Сохранение 1-битного изображения (опционально)
image_1bit.save('your_image_1bit.png')

# Отображение изображения
image_1bit.show()