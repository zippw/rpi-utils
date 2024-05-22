import threading
import time
from modules.LightController import LightController
from modules.OLEDController import OLEDController


def run_oled_controller():
    oled_controller = OLEDController()
    oled_controller.start_display_loop()


def run_light_controller():
    light_controller = LightController()
    light_controller.run()


if __name__ == "__main__":
    oled_thread = threading.Thread(target=run_oled_controller)
    light_thread = threading.Thread(target=run_light_controller)

    oled_thread.start()
    light_thread.start()

    oled_thread.join()
    light_thread.join()
