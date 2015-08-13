
#ifndef SAMPLE_H
#define SAMPLE_H

class Sample
{
private:
	 unsigned long sampleTime;
	 long sampleRef;
	 long sampleData;

public:

	Sample(){
	 	sampleTime = 0;
	 	sampleRef = 0;
	 	sampleData = 0;
	 }

	void set_sample(long ref, long data);
	void print_CSV(void);

	unsigned long getTime() {return sampleTime;}
	long getRef() {return sampleRef;}
	long getSample() {return sampleData;}
};


#endif