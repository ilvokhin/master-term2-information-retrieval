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
  unsigned char* docs;
};

void make_easy_postings(FILE *src, FILE *dst)
{
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

    term_id++;
    free(posting.docs);
  }
}

void make_delta(const int *in_docs, const int size, int *deltas)
{
  deltas[0] = in_docs[0];
  for(int i = 1; i < size; i++)
    deltas[i] = in_docs[i] - in_docs[i - 1];
}

int compress(const int *in_docs, const int in_size, unsigned char *out_docs,
  const int out_size)
{
  int records_cnt = 0;
  int *deltas = (int*) malloc(sizeof(int) * in_size);
  make_delta(in_docs, in_size, deltas);

  printf("deltas:\n");
  for(int i = 0; i < in_size; i++) {
    printf("%d ", deltas[i]);
  }
  printf("\n");

  for(int i = 0; i < in_size; i++) {
    int delta = deltas[i];
    if(delta == 0) {
      out_docs[records_cnt++] = 0;
      continue;
    }
    while(delta) {
      /*
       * Get last seven bits from delta + most significant bit
       * as continuation flag.
       */
      unsigned char delta_part = (((1U << 8) - 1) & delta) | (1U << 7);
      printf("add delta part: %d from (%d)\n", (int) delta_part, in_docs[i]);
      out_docs[records_cnt++] = delta_part;
      delta >>= 7;
      if(records_cnt == out_size) {
        free(deltas);
        return -1;
      }
    }
    out_docs[records_cnt - 1] &= ~(1U << 7);
  }

  printf("compressed deltas:\n");
  for(int i = 0; i < records_cnt; i++)
    printf("%d ", out_docs[i]);
  printf("\n");

  free(deltas);
  return records_cnt;
}

void make_compressed_postings(FILE *src, FILE *dst)
{
  wchar_t term_buf[MAX_TERM_LEN];
  int term_id = 0;
  int docs_cnt = 0;
  struct posting_compressed posting;

  while(fwscanf(src, L"%ls\t%d", term_buf, &docs_cnt) == 2) {
    int *docs = (int *) malloc(sizeof(int) * docs_cnt);
    for(int i = 0; i < docs_cnt; i++)
      fwscanf(src, L"%d", &docs[i]);

   /*
    * Not a bug here: alloc a little bit more memory, that we need
    * to store all input *ints*. In case if we get a bad compression.
    */
    int out_max_size = sizeof(int) * docs_cnt * 2;
    posting.docs = (unsigned char *) malloc(sizeof(unsigned char) * out_max_size);
    posting.size = compress(docs, docs_cnt, posting.docs,
      out_max_size / sizeof(unsigned char));

    if(posting.size == -1) {
      fprintf(stderr, "Error: not enough memory for compressed data "
                      "for term: %d\n", term_id);
      exit(1);
    }

    fwrite(&term_id, sizeof(term_id), 1, dst);
    fwrite(&posting.size, sizeof(posting.size), 1, dst);
    fwrite(posting.docs, sizeof(posting.docs[0]), posting.size, dst);

    term_id++;
    free(docs);
    free(posting.docs);
  }
}

void decompress_postings(FILE *src, FILE *dst)
{
  struct posting_compressed posting;

  while(fread(&posting.term_id, sizeof(posting.term_id), 1, src) != 0) {
    int prev_doc_id = 0;
    int docs_cnt = 0;

    fread(&posting.size, sizeof(posting.size), 1, src);
    
    int *docs = (int*) malloc(sizeof(int) * posting.size);
    posting.docs = (unsigned char*) malloc(sizeof(unsigned char) * posting.size);

    fread(posting.docs, sizeof(posting.docs[0]), posting.size, src);

    for(int i = 0; i < posting.size; ) {
      int delta = 0;
      int shift = 1;
      unsigned int delta_part = (((1U << 8) - 1) & posting.docs[i]);
      int go_on = delta_part & (1U << 7);
      delta_part &= ~(1U << 7);
      while(go_on) {
        //delta |= (delta_part & ~(1U << 7));
        //delta <<= 7;
        //printf("%d\n", delta_part);
        delta |= delta_part;
        delta_part = (((1U << 8) - 1) & posting.docs[++i]);
        //printf("original: %d\n", delta_part);
        go_on = delta_part & (1U << 7);
        delta_part = ((delta_part & ~(1U << 7)) << 7 * shift);
        shift++;
        //printf("updated: %d\n", delta_part);
      }
      //printf("%d\n", delta_part);
      delta |= delta_part;
      prev_doc_id += delta;
      docs[docs_cnt++] = prev_doc_id;
      i++;
    }

    fprintf(dst, "%d\t%d", posting.term_id, docs_cnt);
    for(int i = 0; i < docs_cnt; i++)
      fprintf(dst, "\t%d", docs[i]);
    printf("\n");

    free(posting.docs);
    free(docs);
  }
}

void usage(char *bin_name)
{
  fprintf(stderr, "usage %s: easy | compress | decompress\n", bin_name);
}

int main(int argc, char* argv[])
{
  if(argc != 2) {
    usage(argv[0]);
    exit(EXIT_FAILURE);
  }

  /* quick locale fix */
  setlocale(LC_CTYPE, "en_US.UTF-8");

  FILE *binary_dst = NULL;
  if((binary_dst = fopen("test.data", "wb")) == NULL) {
    perror("Error");
    exit(EXIT_FAILURE);
  }

  if(strcmp(argv[1], "easy") == 0)
    make_easy_postings(stdin, binary_dst);
  else if(strcmp(argv[1], "compress") == 0)
    make_compressed_postings(stdin, binary_dst);
  else if(strcmp(argv[1], "decompress") == 0) {
    fclose(binary_dst);
    if((binary_dst = fopen("test2.data", "rb")) == NULL) {
      perror("Error");
      exit(EXIT_FAILURE);
    }
    decompress_postings(binary_dst, stdout);
  } else {
    usage(argv[0]);
    exit(EXIT_FAILURE);
  }

  fclose(binary_dst);
  exit(EXIT_SUCCESS);
}
