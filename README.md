# OpenRGB E1.31 Settings:

- **IP (Unicast):** Local Wi-Fi IP
- **Start Universe:** 1

*Note: Start Universe is the universe that we listen to.*
```python
@receiver.listen_on("universe", universe=1)
```

- **Start Channel:** 1
    - Use 1 to avoid corrupting RGB order and packet data.

- **Number of LEDs:** TOTAL_LED_COUNT
- **RGB Order:** RGB
- **Universe Size:** TOTAL_LED_COUNT * 3

# Raspberry PI 4 Pinout:

You can connect data wires to the following GPIO pins:
- GPIO 10
- GPIO 12
- GPIO 18
- GPIO 21

*Note: GPIO 12 & GPIO 18 share the same PWM channel. Combining these pins may result in signal duplication and incorrect colors. It is recommended not to use these pins together.*