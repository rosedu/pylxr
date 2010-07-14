/*
   320112
   a7_6.c
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
		printf("You should supply an input file!\n");
		return 1;
	}
	if ( argc > 2 )
		strcpy(filename_o, argv[2]);
	else {
		printf("You should supply an output file!\n");
		return 1;
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
	if ( strstr(buf, "P6") != buf ) {
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
		for (j=0; j<width; ++j) { // changed, depends on type of binary file
			int r, g, b;
			if ( colors == 255 ) {
				unsigned char c;
				fread(&c, 1, 1, fi); r = c;
				fread(&c, 1, 1, fi); g = c;
				fread(&c, 1, 1, fi); b = c;
			} else {
				unsigned char c[2];
				fread(c, 1, 2, fi); r = (c[0] << 8) + c[1];
				fread(c, 1, 2, fi); g = (c[0] << 8) + c[1];
				fread(c, 1, 2, fi); b = (c[0] << 8) + c[1];
			}
			if ( b==colors && r==0 && g==0 )
				r = g = colors, b = 0;
			else if ( r==colors && b==0 && g==0 )
				g = colors, r = b = 0;

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

