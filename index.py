from modules.LightController import LightController
from modules.OLEDController import OLEDController

if __name__ == "__main__":
    LightController = LightController()
    LightController.run()
    
    OLEDController().start_display_loop()