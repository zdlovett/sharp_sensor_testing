
#include "sample.h"
#include "arduino.h"



void Sample::set_sample(long ref, long data){
	sampleTime = millis();
	sampleRef = ref;
	sampleData = data;
}

void Sample::print_CSV(void){
	Serial.print(sampleTime);
	Serial.print(',');
	Serial.print(sampleRef);
	Serial.print(',');
	Serial.println(sampleData);
}