from modules.LightController import LightController
from modules.OLEDController import OLEDController

if __name__ == "__main__":
    OLEDController().start_display_loop()
    LightController = LightController()
    LightController.run()
    