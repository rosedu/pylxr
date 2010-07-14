/*
   320112
   a7_5.c
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
} // don't you just hate unformatted input? x( LEGACY FUNCTION :)

int main(int argc, char **argv) {
	char filename[LMAX], filename_o[LMAX];
	if ( argc > 1 )
		strcpy(filename, argv[1]); // from commandline
	else {
		printf("Enter input filename: ");
		fgets(filename, LMAX, stdin);
	}
	if ( argc > 2 )
		strcpy(filename_o, argv[2]);
	else {
		printf("Enter output filename: ");
		fgets(filename_o, LMAX, stdin);
	}

	printf("Using input file \"%s\" and output file \"%s\"...\n",
		   filename, filename_o);
	FILE *fi = fopen(filename, "rt");
	if ( fi == NULL ) {
		fprintf(stderr, "Not able to open input file.\nExiting...\n");
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

	// printing surpressed

	// pixel data starts on a NEW LINE
	// therefore, we can go on with fscanf from now on
	// BTW: by the time I learned I could use fscanf
	// just as well for the whitespace problem,
	// I had already implemented the my_read routine
	// and I still keep it in use as it does its job.

	PPM myImg;
	ppm_init(&myImg, filename, width, height);
	int i, j;
	for (i=0; i<height; ++i)
		for (j=0; j<width; ++j) {
			int r, g, b;
			fscanf(fi, "%d %d %d", &r, &g, &b);
			myImg.px[i][j] = pixel_init(r,g,b);
		}

	// printing surpressed

	FILE *fo = fopen(filename_o, "w");
	if ( fo == NULL ) {
		fprintf(stderr, "Not able to open output file.\nExiting...\n");
		return 1;
	}
	fprintf(fo, "P6\n%d %d\n%d\n", width, height, colors);

	for (i=0; i<height; ++i)
		for (j=0; j<width; ++j) {
			if ( colors == 255 ) {
				putc(myImg.px[i][j].r,fo);
				putc(myImg.px[i][j].g,fo);
				putc(myImg.px[i][j].b,fo);
			} else {
				putc(myImg.px[i][j].r >> 8, fo);		// first 8 bits
				putc(myImg.px[i][j].r & 255, fo);		// last 8 bits
				putc(myImg.px[i][j].g >> 8, fo);
				putc(myImg.px[i][j].g & 255, fo);
				putc(myImg.px[i][j].b >> 8, fo);
				putc(myImg.px[i][j].b & 255, fo);				
			}
		}
	
	fclose(fo);
	fclose(fi);
	return 0;
}

