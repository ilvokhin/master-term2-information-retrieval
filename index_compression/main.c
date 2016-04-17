#include <stdio.h>
#include <wchar.h>
#include <stdlib.h>
#include <string.h>
#include <locale.h>
#include <unistd.h>

#define MAX_TERM_LEN 4096

struct posting_easy {
  int term_id;
  int size;
  int *docs;
};

/* posting list compressed with variable byte */
struct posting_compressed {
  int term_id;
  int size;
  char* docs;
};

int make_easy_postings(FILE *src, FILE *dst) {
  wchar_t term_buf[MAX_TERM_LEN];
  int term_id = 0;
  struct posting_easy posting;

  while(fwscanf(src, L"%ls\t%d", term_buf, &posting.size) == 2) {
    posting.docs = (int *) malloc(sizeof(int) * posting.size);
    for(int i = 0; i < posting.size; i++)
      fwscanf(src, L"%d", &posting.docs[i]);

    /* write binary data to dst */
    fwrite(&term_id, sizeof(term_id), 1, dst);
    fwrite(&posting.size, sizeof(posting.size), 1, dst);
    fwrite(posting.docs, sizeof(posting.docs[0]), posting.size, dst);

    free(posting.docs);
    term_id++;
  }

  return 0;
}

int make_compressed_postings(FILE *src, FILE *dst) {
  return 0;
}

void usage(char *bin_name) {
  fprintf(stderr, "usage %s: easy | compressed\n", bin_name);
}

int main(int argc, char* argv[])
{
  if(argc != 2) {
    usage(argv[0]);
    exit(EXIT_FAILURE);
  }

  // quick locale fix
  setlocale(LC_CTYPE, "en_US.UTF-8");

  FILE *binary_dst = NULL;
  if((binary_dst = fopen("test.data", "wb")) == NULL) {
    perror("Error");
    exit(EXIT_FAILURE);
  }

  if(strcmp(argv[1], "easy") == 0)
    make_easy_postings(stdin, binary_dst);
  else if(strcmp(argv[1], "compressed") == 0)
    make_compressed_postings(stdin, binary_dst);
  else {
    usage(argv[0]);
    exit(EXIT_FAILURE);
  }

  exit(EXIT_SUCCESS);
}
