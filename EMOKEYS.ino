// EMOKEYS by Taliyah

// Turn on if you want initial setup to be automated
const bool auto_setup = true;
// If above is true, add your path to cerial.py
const String path = "~/Documents/Arduino/EMOKEYS";
// And change this to the number of times needed to get to Unicode Hex Input keyboard
const int num_switch = 4;

// Keyboard Layout
// Row 0: [0_0] [0_1] [0_2] [0_3]
// Row 1: [1_0] [1_1] [1_2] [1_3]
// Row 2: [2_0] [2_1] [2_2] [2_3]

#include <Keyboard.h>

#include <Adafruit_GFX.h>
#include <Adafruit_SSD1331.h>
#include <SPI.h>

#define scl   21
#define sda   20
#define dc    19

// Set pins for rows
const byte rows[] = {A0, A1, A2};
const int rowCount = sizeof(rows) / sizeof(rows[0]);

// Set pins for columns
const byte cols[] = {A4, A5, A6, A7};
const int colCount = sizeof(cols) / sizeof(cols[0]);

char buf[10];
uint16_t arrays[9][2304];
uint16_t myIndex = 0;
int unicodeIndex = 0;
bool emojiType = 0;

String codes[3][3] = {{"", "", ""}, {"", "", ""}, {"", "", ""}};
bool keyStates[3][4] = { {false, false, false, false}, {false, false, false, false}, {false, false, false, false} };
int keyDelays[3][4] = { {0, 0, 0, 0}, {0, 0, 0, 0}, {0, 0, 0, 0} };

int currentRow = 0;
byte keys[rowCount][colCount];
bool rowLoad = 0;
uint8_t preLoad = 2;

const byte res[] = {22, 24, 26, 28, 30, 32, 34, 36, 38};
const byte cs[] = {23, 25, 27, 29, 31, 33, 35, 37, 39};

Adafruit_SSD1331 display0_0 = Adafruit_SSD1331(cs[0], dc, sda, scl, res[0]);
Adafruit_SSD1331 display0_1 = Adafruit_SSD1331(cs[1], dc, sda, scl, res[1]);
Adafruit_SSD1331 display0_2 = Adafruit_SSD1331(cs[2], dc, sda, scl, res[2]);

Adafruit_SSD1331 display1_0 = Adafruit_SSD1331(cs[3], dc, sda, scl, res[3]);
Adafruit_SSD1331 display1_1 = Adafruit_SSD1331(cs[4], dc, sda, scl, res[4]);
Adafruit_SSD1331 display1_2 = Adafruit_SSD1331(cs[5], dc, sda, scl, res[5]);

Adafruit_SSD1331 display2_0 = Adafruit_SSD1331(cs[6], dc, sda, scl, res[6]);
Adafruit_SSD1331 display2_1 = Adafruit_SSD1331(cs[7], dc, sda, scl, res[7]);
Adafruit_SSD1331 display2_2 = Adafruit_SSD1331(cs[8], dc, sda, scl, res[8]);

void setup() {
  SerialUSB.begin(115200);
  Keyboard.begin();

  for (int x = 0; x < rowCount; x++) {
    pinMode(rows[x], INPUT);
  }

  for (int x = 0; x < colCount; x++) {
    pinMode(cols[x], INPUT_PULLUP);
  }

  // Auto Setup
  if (auto_setup == true) {
    delay(500);
    // Toggle to Unicode Hex Input keyboard
    Keyboard.press(KEY_LEFT_CTRL);
    Keyboard.press(KEY_LEFT_ALT);
    for (uint8_t i = 0; i < num_switch; i++) {
      Keyboard.print(" ");
      delay(1);
    }
    Keyboard.release(KEY_LEFT_ALT);
    Keyboard.release(KEY_LEFT_CTRL);

    // Run cerial.py on Terminal
    Keyboard.press(KEY_LEFT_GUI);
    Keyboard.print(" ");
    Keyboard.release(KEY_LEFT_GUI);
    delay(100);
    Keyboard.println("Terminal");
    delay(300);
    Keyboard.println("cd " + path);
    delay(100);
    Keyboard.println("python3 cerial.py");
  }

  display0_0.begin();
  display0_1.begin();
  display0_2.begin();

  display1_0.begin();
  display1_1.begin();
  display1_2.begin();

  display2_0.begin();
  display2_1.begin();
  display2_2.begin();

  display2_0.fillScreen(0x0000);
  display2_1.fillScreen(0x0000);
  display2_2.fillScreen(0x0000);

  display1_0.fillScreen(0x0000);
  display1_1.fillScreen(0x0000);
  display1_2.fillScreen(0x0000);

  display0_0.fillScreen(0x0000);
  display0_1.fillScreen(0x0000);
  display0_2.fillScreen(0x0000);

  SerialUSB.print(preLoad);
}

void loop() {
  readMatrix();
  if (readline(SerialUSB.read(), buf, 10) > 0) {
    if (buf[0] == 'u') { // Unicode
      if (int(2 - floor(unicodeIndex / 3)) > 0) {
        codes[int(2 - floor(unicodeIndex / 3))][int(unicodeIndex % 3)] = String(buf).substring(1);
      } else {
        for (uint16_t m = 0; m < 3; m++) {
          if (unicodeIndex < (m + 1) * 3 && unicodeIndex >= 3 * m) {
            codes[rowLoad * 2][unicodeIndex - 3 * m] = String(buf).substring(1);
          }
        }
      }
      unicodeIndex++;
    } else {
      uint16_t i;
      sscanf(buf, "%d", &i);
      for (uint16_t m = 0; m < 3; m++) {
        if (myIndex < 2304 * (m + 1) && myIndex >= 2304 * m) {
          if (preLoad > 0) {
            arrays[m + 3 * preLoad][myIndex - 2304 * m] = i;
          } else {
            arrays[m + rowLoad * 6][myIndex - 2304 * m] = i;
          }
        }
      }
      myIndex++;
    }
    if (myIndex == 2304 * 3) {

      if (preLoad > 0) { // Load in all 9 graphics in the beginning

        myIndex = 0;
        preLoad--;
        SerialUSB.print(preLoad);

        if (preLoad == 1) {
          display2_0.drawRGBBitmap(24, 8, arrays[6], 48, 48);
          display2_1.drawRGBBitmap(24, 8, arrays[7], 48, 48);
          display2_2.drawRGBBitmap(24, 8, arrays[8], 48, 48);
        } else if (preLoad == 0) {
          display1_0.drawRGBBitmap(24, 8, arrays[3], 48, 48);
          display1_1.drawRGBBitmap(24, 8, arrays[4], 48, 48);
          display1_2.drawRGBBitmap(24, 8, arrays[5], 48, 48);
        }

      } else { // Otherwise load in the top or bottom row

        if (rowLoad == 0) {
          display0_0.drawRGBBitmap(24, 8, arrays[0], 48, 48);
          display0_1.drawRGBBitmap(24, 8, arrays[1], 48, 48);
          display0_2.drawRGBBitmap(24, 8, arrays[2], 48, 48);
        } else {
          display2_0.drawRGBBitmap(24, 8, arrays[6], 48, 48);
          display2_1.drawRGBBitmap(24, 8, arrays[7], 48, 48);
          display2_2.drawRGBBitmap(24, 8, arrays[8], 48, 48);
        }

      }
    }
  }
}

void readMatrix() {
  // iterate the columns
  for (int colIndex = 0; colIndex < colCount; colIndex++) {
    // col: set to output to low
    byte curCol = cols[colIndex];
    pinMode(curCol, OUTPUT);
    digitalWrite(curCol, LOW);

    // row: interate through the rows
    for (int rowIndex = 0; rowIndex < rowCount; rowIndex++) {
      byte rowCol = rows[rowIndex];
      pinMode(rowCol, INPUT_PULLUP);
      keys[rowIndex][colIndex] = digitalRead(rowCol);
      if (keys[rowIndex][colIndex] == LOW) {
        if (keyStates[rowIndex][colIndex] == false) {
          if (colIndex != 3) {
            if (emojiType == 0) {
              Keyboard.press(0x82);
              Keyboard.print(codes[rowIndex][colIndex]);
              Keyboard.release(0x82);
            } else {
              Keyboard.print(":" + codes[rowIndex][colIndex] + ":");
            }

          } else {

            myIndex = 0;
            unicodeIndex = 0;

            if (rowIndex == 1) {

              if (emojiType == 0) {
                emojiType = 1;
              } else {
                emojiType = 0;
              }

              SerialUSB.print(-2);

              if (SerialUSB.readString() == "a") {
                preLoad = 2;
                rowLoad = 0;
                SerialUSB.print(preLoad);
              }

              display2_0.fillScreen(0x0000);
              display2_1.fillScreen(0x0000);
              display2_2.fillScreen(0x0000);

              display1_0.fillScreen(0x0000);
              display1_1.fillScreen(0x0000);
              display1_2.fillScreen(0x0000);

              display0_0.fillScreen(0x0000);
              display0_1.fillScreen(0x0000);
              display0_2.fillScreen(0x0000);

              currentRow = 0;

            } else {

              if (rowIndex == 0 && currentRow >= 1) { // Go Up a Row
                for (int m = 5; m >= 0; m--) {
                  for (uint16_t t = 0; t < 2304; t++) {
                    arrays[m + 3][t] = arrays[m][t];
                  }
                  for (int t = 0; t < 3; t++) {
                    codes[int(m / 3) + 1][t] = codes[int(m / 3)][t];
                  }
                }

                currentRow--;
                rowLoad = 0;
                SerialUSB.print(currentRow);

                display2_0.drawRGBBitmap(24, 8, arrays[6], 48, 48);
                display2_1.drawRGBBitmap(24, 8, arrays[7], 48, 48);
                display2_2.drawRGBBitmap(24, 8, arrays[8], 48, 48);

                display1_0.drawRGBBitmap(24, 8, arrays[3], 48, 48);
                display1_1.drawRGBBitmap(24, 8, arrays[4], 48, 48);
                display1_2.drawRGBBitmap(24, 8, arrays[5], 48, 48);

                display0_0.fillScreen(0x0000);
                display0_1.fillScreen(0x0000);
                display0_2.fillScreen(0x0000);
              } else if (rowIndex == 2) { // Go Down a Row
                for (int m = 0; m < 6; m++) {
                  for (uint16_t t = 0; t < 2304; t++) {
                    arrays[m][t] = arrays[m + 3][t];
                  }
                  for (int t = 0; t < 3; t++) {
                    codes[int(m / 3)][t] = codes[int(m / 3) + 1][t];
                  }
                }

                currentRow++;
                rowLoad = 1;
                SerialUSB.print(currentRow + 2);

                display0_0.drawRGBBitmap(24, 8, arrays[0], 48, 48);
                display0_1.drawRGBBitmap(24, 8, arrays[1], 48, 48);
                display0_2.drawRGBBitmap(24, 8, arrays[2], 48, 48);

                display1_0.drawRGBBitmap(24, 8, arrays[3], 48, 48);
                display1_1.drawRGBBitmap(24, 8, arrays[4], 48, 48);
                display1_2.drawRGBBitmap(24, 8, arrays[5], 48, 48);

                display2_0.fillScreen(0x0000);
                display2_1.fillScreen(0x0000);
                display2_2.fillScreen(0x0000);
              }
            }
          }
        }
        keyStates[rowIndex][colIndex] = true;
        keyDelays[rowIndex][colIndex] = 0;
      } else {
        keyDelays[rowIndex][colIndex]++;
        if (keyDelays[rowIndex][colIndex] > 10) {
          keyStates[rowIndex][colIndex] = false;
          keyDelays[rowIndex][colIndex] = 0;
        }
      }
      pinMode(rowCol, INPUT);
    }
    // disable the column
    pinMode(curCol, INPUT);
  }
}

int readline(int readch, char *buffer, int len) {
  static int pos = 0;
  int rpos;

  if (readch > 0) {
    switch (readch) {
      case '\r': // Ignore CR
        break;
      case '\n': // Return on new-line
        rpos = pos;
        pos = 0;  // Reset position index ready for next time
        return rpos;
      default:
        if (pos < len - 1) {
          buffer[pos++] = readch;
          buffer[pos] = 0;
        }
    }
  }
  return 0;
}
