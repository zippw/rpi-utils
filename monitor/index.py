import os

from library.lcd.lcd_comm import Orientation
from library.lcd.lcd_comm_rev_c import LcdCommRevC

lcd_comm = LcdCommRevC(com_port="AUTO",
                       display_width=800,
                       display_height=480)

lcd_comm.Reset()
lcd_comm.InitializeComm()
lcd_comm.SetBrightness(level=25)
lcd_comm.SetBackplateLedColor(led_color=(255, 0, 0))
lcd_comm.SetOrientation(orientation=Orientation.REVERSE_LANDSCAPE)

# lcd_comm.DisplayText("Custom italic text", x=5, y=150,
#                      font="roboto/Roboto-Italic.ttf",
#                      font_size=30,
#                      font_color=(0, 0, 255),
#                      background_color=(0, 255, 0))

lcd_comm.DisplayText("Transparent bold text", x=5, y=250,
                     font="geforce/GeForce-Bold.ttf",
                     font_size=30,
                     font_color=(255, 255, 255),
                     background_color=(0, 255, 0))

# Получаем абсолютный путь к текущему рабочему каталогу
current_directory = os.getcwd()

# Получаем абсолютный путь к текущему скрипту (если он запущен из этого проекта)
current_script_path = os.path.abspath(__file__)

# Если вы хотите получить путь к корневому каталогу проекта, можете использовать какую-то метку или имя каталога,
# которое уникально для вашего проекта
project_root_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), 'ваш_каталог_проекта'))

print("Текущий рабочий каталог:", current_directory)
print("Путь к текущему скрипту:", current_script_path)
print("Путь к корневому каталогу проекта:", project_root_directory)