//datalogger.ino

#include "sample.h"

#include <Wire.h>
#define    LIDARLite_ADDRESS   0x62          // Default I2C Address of LIDAR-Lite.
#define    RegisterMeasure     0x00          // Register to write to initiate ranging.
#define    MeasureValue        0x04          // Value to initiate ranging.
#define    RegisterHighLowB    0x8f          // Register to get both High and Low bytes in 1 call.

#define QUEUE_LENGTH 32

int led = 13;
Sample sampleQueue[QUEUE_LENGTH];


void setup() {
  //set the pin mode for Serial2 to outputs and inputs
  pinMode(16, OUTPUT);
  pinMode(17, INPUT);

  Wire.begin(); // join i2c bus
  Serial.begin(115200);
  Serial2.begin(115200);

  //config the Teraranger
  Serial2.print('PB');

}

unsigned int value = 0;
int index = 0;
unsigned long lastTime;


int startLidarRead = 0;
int lindarReading;
void loop() {

  nonBlockingReadLidar();

  if(millis() - lastTime > 60){
    startLidarRead = 1;
  }

  if(millis() - lastTime > 100){
    lastTime = millis();
    sampleQueue[index].set_sample(readLidar(), value);
    sampleQueue[index].print_CSV();

    index = advanceIndex(index);
  }
}


int advanceIndex(int i)
{
    i++;
    if(i == QUEUE_LENGTH){
      i = 0;
    }
    return i;
}

void serialEvent2(){
  char c = Serial2.peek();
  if(c == 'T' && Serial2.available()>4){
    parseValue();
  }
}

void parseValue(){
  unsigned int incoming[4];
  for(int i=0; i<4;i++){
    incoming[i] = Serial2.read();
  }
  value = incoming[1] << 8;
  value += incoming[2];
}


void nonBlockingReadLidar(){
  static unsigned long startTime;
  static char reading;

  switch (reading) {
      case 0:
        if(startLidarRead == 1){
          Serial.println("reading to state 1");
          reading = 1;
          startTime == millis();
          Wire.beginTransmission((int)LIDARLite_ADDRESS); // transmit to LIDAR-Lite
          Wire.write((int)RegisterMeasure); // sets register pointer to  (0x00)  
          Wire.write((int)MeasureValue); // sets register pointer to  (0x00)  
          Wire.endTransmission(); // stop transmitting
        }
        break;
      case 1:
        if(millis() - startTime >= 20){
          Serial.println("reading to state 2");
          reading = 2;
          Wire.beginTransmission((int)LIDARLite_ADDRESS); // transmit to LIDAR-Lite
          Wire.write((int)RegisterHighLowB); // sets register pointer to (0x8f)
          Wire.endTransmission(); // stop transmitting
        }
        break;
      case 2:
          if(millis() - startTime >= 40){
            char result = Wire.requestFrom((int)LIDARLite_ADDRESS, 2); // request 2 bytes from LIDAR-Lite
            if(result != 2){
              Serial.println("read request failed.");
            }
            Serial.println("reading to state 3");
            reading = 3;
        }
        break;
      case 3:
        if(2 <= Wire.available()) // if two bytes were received
        {
          lindarReading = Wire.read(); // receive high byte (overwrites previous reading)
          lindarReading = lindarReading << 8; // shift high byte to be high 8 bits
          lindarReading |= Wire.read(); // receive low byte as lower 8 bits
          Serial.println("reading to state 0");
          reading = 0;
        }
        break;
      default:
        Serial.println("default case");
    
  }
}


void onReceive(int byteCount){
  Serial.print(byteCount);
}


int readLidar(void){
  int reading = -1;

  Wire.beginTransmission((int)LIDARLite_ADDRESS); // transmit to LIDAR-Lite
  Wire.write((int)RegisterMeasure); // sets register pointer to  (0x00)  
  Wire.write((int)MeasureValue); // sets register pointer to  (0x00)  
  Wire.endTransmission(); // stop transmitting

  delay(20); // Wait 20ms for transmit

  Wire.beginTransmission((int)LIDARLite_ADDRESS); // transmit to LIDAR-Lite
  Wire.write((int)RegisterHighLowB); // sets register pointer to (0x8f)
  Wire.endTransmission(); // stop transmitting

  delay(20); // Wait 20ms for transmit

  Wire.requestFrom((int)LIDARLite_ADDRESS, 2); // request 2 bytes from LIDAR-Lite

  if(2 <= Wire.available()) // if two bytes were received
  {
    reading = Wire.read(); // receive high byte (overwrites previous reading)
    reading = reading << 8; // shift high byte to be high 8 bits
    reading |= Wire.read(); // receive low byte as lower 8 bits
  }

  return reading;
}