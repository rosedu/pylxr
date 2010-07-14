/*
   320112
   a7_4.c
   Mihai Cotizo Sima
   m.sima@jacobs-university.de
*/

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#define LMAX 100

typedef struct {
	int r, g, b;
} pixel;

typedef struct ppm {
	char *name;
	int w, h;
	pixel **px;
} PPM;

pixel pixel_init(const int r, const int g, const int b) {
	pixel ret;
	ret.r = r;
	ret.g = g;
	ret.b = b;
	return ret;
}

void ppm_init(PPM *p, const char *n, const int w, const int h) {
	strcpy(p->name, n);
	p->w = w;
	p->h = h;
	p->px = (pixel**)malloc(sizeof(pixel*)*h);
	int i;
	for (i=0; i<h; ++i)
		p->px[i] = (pixel*)malloc(sizeof(pixel)*w);
}

int my_read(char **stream, int *ret) { // extracts whitespace
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
	char filename[LMAX];
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
	printf("Total number of pixels: %d.\n", width*height);

	// pixel data starts on a NEW LINE
	// therefore, we can go on with fscanf from now on
	// BTW: by the time I learned I could use fscanf
	// just as well for the whitespace problem,
	// I had already implemented the my_read routine
	// and I still keep it in use as it does its job.

	PPM myImg;
	ppm_init(&myImg, filename, width, height);
	int i, j;
	int nrRed = 0, nrGreen = 0;
	for (i=0; i<height; ++i)
		for (j=0; j<width; ++j) {
			int r, g, b;
			fscanf(fi, "%d %d %d", &r, &g, &b);
			myImg.px[i][j] = pixel_init(r,g,b);
			nrRed += ( r==255 && g==0 && b==0 ) ? 1 : 0;
			nrGreen += ( r==0 && g==255 && b==0 ) ? 1 : 0;
		}

	printf("Total number of red pixels: %d.\n", nrRed);
	printf("Total number of green pixels: %d.\n", nrGreen);
	printf("Total number of green OR red pixels: %d.\n", nrRed+nrGreen);
	
	fclose(fi);
	return 0;
}

