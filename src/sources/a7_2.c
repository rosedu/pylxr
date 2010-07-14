/*
   320112
   a7_1.c
   Mihai Cotizo Sima
   m.sima@jacobs-university.de
*/

#include <stdio.h>

int N, i;
char buf[10];

int main() {
	printf("Enter integer number: ");
	fgets(buf, 10, stdin);
	sscanf(buf, "%d", &N);

	FILE *fo = fopen("squares.txt", "w");
	if ( fo == NULL ) {
		fprintf(stderr, "Failed to open \"squares.txt\". Exiting.\n");
		return 1;
	}
	for (i=1; i<=N; ++i)
		fprintf(fo, "Square of %d is %d.\n", i, i*i);
	fclose(fo);
	return 0;
}


