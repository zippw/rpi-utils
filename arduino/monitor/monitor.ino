#include <Adafruit_GFX.h>
#include <MCUFRIEND_kbv.h>
MCUFRIEND_kbv tft;

#define END_OF_TRANSMISSION 0x0D
#define SEPARATOR ','
#define MAX_LINE_LENGTH 24

// DDD.DDD.DDD.DDD
// 999.99 °C
int txt_padding[] = { 20, 40 };
const char *text_form_str[] = {
  "IP:   %s",
  "TEMP: %s \xF7\C"
};
String txt_form[] = { "IP: ", "TEMP: " };

void setup(void) {
  /* Serial init */
  Serial.begin(9600);
  Serial.setTimeout(3000);

  /* Touch screen init */
  uint16_t ID = tft.readID();
  if (ID == 0xD3D3) ID = 0x9481;  //force ID if write-only display
  tft.begin(ID);
  tft.setRotation(3);

  /* Initial render */
  tft.fillScreen(0x0000);
  text_form(0, "0.0.0.0");
  text_form(1, "XX.X");
  Serial.println("Hello");
}

void loop() {
  if (Serial.available()) {
    char data[30];
    int amount = Serial.readBytesUntil(END_OF_TRANSMISSION, data, 30);
    data[amount] = '\0';

    char *comma_position = strchr(data, SEPARATOR);

    if (comma_position != NULL) {
      int num_length = comma_position - data;
      char num_str[num_length + 1];
      strncpy(num_str, data, num_length);
      num_str[num_length] = '\0';

      int code = atoi(num_str);         // command code
      char *data = comma_position + 1;  // command data

      text_form(code, data);
    }
  }
}

void text_form(int code, char *data) {
  char result[MAX_LINE_LENGTH];
  snprintf(result, MAX_LINE_LENGTH, text_form_str[code], data);
  fill_with_space(result);
  showmsgXY(20, txt_padding[code], 2, NULL, result, 0xFFFF, NULL);
}

/* HELPERS */
void fill_with_space(char *str) {
  int length = strlen(str);
  int spaces_to_add = MAX_LINE_LENGTH - length;

  if (spaces_to_add > 0) {
    for (int i = length; i < MAX_LINE_LENGTH - 1; ++i) {
      str[i] = ' ';
    }
    str[MAX_LINE_LENGTH - 1] = '\0';
  }
}

void showmsgXY(int x, int y, int sz, const GFXfont *f, const char *msg, uint16_t color, uint16_t background_color) {
  int16_t x1, y1;
  uint16_t wid, ht;
  tft.setFont(f);
  tft.setCursor(x, y);
  tft.setTextColor(color, background_color);
  tft.setTextSize(sz);
  tft.print(msg);
}