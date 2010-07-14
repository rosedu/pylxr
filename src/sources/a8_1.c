/*
  320112
  a8_1.c
  Mihai Cotizo Sima
  m.sima@jacobs-university.de
*/

#include <math.h>
#include <stdio.h>

inline float mylog2(float x) { return log(x) / log(2); }

int main(int argc, char **argv) {
	FILE *fo = fopen("data.txt", "wt");
	if ( fo==NULL ) {
		fprintf(stderr, "Not able to open file.\n");
		return 0;
	}

	float i;
	for (i=0.5; i<=1000; i+=0.5) 
		fprintf(fo, "%f\t%f\t%f\t%f\n", i, i*i, mylog2(i), mylog2(i)*i);

	fclose(fo);
	return 0;
}
