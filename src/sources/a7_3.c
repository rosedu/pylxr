/*
   320112
   a7_3.c
   Mihai Cotizo Sima
   m.sima@jacobs-university.de
*/

#include <stdio.h>
#include <string.h>
#define LMAX 100

char filename[LMAX];

int my_read(char **stream, int *ret) {
	while ( **stream!=0 && strchr("0123456789", **stream) == NULL ) // skip the whiteshit
		++ (*stream);
	if ( **stream == 0 )
		return 1; // error, we did not find an int in the current buffer
	*ret = 0;
	for (; **stream!=0 && strchr("0123456789", **stream) != NULL; ++(*stream))
		*ret = (*ret) * 10 + (**stream - '0');

	return 0; 
} // don't you just hate unformatted input? x(

int main(int argc, char **argv) {
	if ( argc > 1 )
		strcpy(filename, argv[1]); // from commandline
	else {
		printf("Enter filename: ");
		fgets(filename, LMAX, stdin);
	}

	printf("Using file \"%s\"...\n", filename);	
	FILE *fi = fopen(filename, "rt");
	if ( fi == NULL ) {
		fprintf(stderr, "Not able to open file. Sorry! :(\nExiting...\n");
		return 1;
	}

	char buf[LMAX];
	fgets(buf, LMAX, fi);
	if ( strstr(buf, "P3") != buf ) {
		printf("File not PPM image. Exiting...\n");
		return 0;
	}

	char *p = buf + 2; // ignore the magic number and start extracting ints
	int width, height, colors;
	while ( my_read(&p, &width) != 0 ) // we did not extract a number yet
		fgets(buf, LMAX, fi), p = buf; // get another line and repeat
	while ( my_read(&p, &height) != 0 )
		fgets(buf, LMAX, fi), p = buf;
	while ( my_read(&p, &colors) != 0 )
		fgets(buf, LMAX, fi), p = buf;

	printf("Image has width %d and height %d.\n", width, height);
	if ( colors == 255 )
		printf("Image supports 8-bit colors.\n");
	else
		printf("Image supports 16-bit colors.\n");

	fclose(fi);
	return 0;
}

