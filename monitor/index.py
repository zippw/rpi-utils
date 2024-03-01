from library.lcd.lcd_comm import Orientation
from library.lcd.lcd_comm_rev_c import LcdCommRevC

lcd_comm = LcdCommRevC(com_port="AUTO",
                       display_width=800,
                       display_height=480)

lcd_comm.Reset()
lcd_comm.InitializeComm()
lcd_comm.SetBrightness(level=100)
lcd_comm.SetBackplateLedColor(led_color=(255, 0, 0))
lcd_comm.SetOrientation(orientation=Orientation.REVERSE_LANDSCAPE)

# lcd_comm.DisplayText("Custom italic text", x=5, y=150,
#                      font="roboto/Roboto-Italic.ttf",
#                      font_size=30,
#                      font_color=(0, 0, 255),
#                      background_color=(0, 255, 0))

lcd_comm.DisplayText("text", x=1, y=250,
                     font="geforce/GeForce-Bold.ttf",
                     font_size=30,
                     font_color=(255, 255, 255),
                     background_color=(0, 255, 0))