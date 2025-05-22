#include <errno.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define REVISION 2

#define IDENTIFIER1 'K'
#define IDENTIFIER2 'S'
#define IDENTIFIER3 'y'
#define IDENTIFIER4 'M'

#define FLAG_GLOBAL (1 << 0)

typedef struct {
    uint64_t name_offset;
    uint16_t flags;
    uint16_t rsv0;
    uint32_t rsv1;
    uint64_t size;
    uint64_t address;
} __attribute__((packed)) symbol_t;

typedef struct {
    uint8_t identifier[4];
    uint8_t revision;
    uint8_t rsv0[3];
    uint64_t names_offset, names_size;
    uint64_t symbols_offset, symbol_size, symbols_count;
} __attribute__((packed)) header_t;

int main(int argc, char **argv) {
    // Validate arguments
    if(argc < 2) {
        fprintf(stderr, "missing input file");
        return EXIT_FAILURE;
    }

    if(argc < 3) {
        fprintf(stderr, "missing output file");
        return EXIT_FAILURE;
    }

    bool verbose = false;
    if(argc >= 4 && strcmp(argv[3], "verbose") == 0) verbose = true;

    // Allocate buffers
    symbol_t *symbol_buffer = NULL;
    size_t symbol_buffer_count = 0;

    char *name_buffer = NULL;
    size_t name_buffer_size = 0;

    // Process input file
    FILE *input = fopen(argv[1], "r");
    if(input == NULL) {
        fprintf(stderr, "failed to open input `%s`", strerror(errno));
        return EXIT_FAILURE;
    }

    uint64_t address, size;
    char type;
    char name[2048];
    while(fscanf(input, "%lx %lx %c %s", &address, &size, &type, name) == 4) {
        bool global = type >= 'A' && type <= 'Z';
        uint64_t flags = (uint64_t) type << 8;
        if(global) type |= FLAG_GLOBAL;

        if(verbose) printf("%#lx | %#lx | %c '%c' | %s\n", address, size, global ? 'G' : '-', type, name);

        symbol_buffer = reallocarray(symbol_buffer, ++symbol_buffer_count, sizeof(symbol_t));
        symbol_buffer[symbol_buffer_count - 1] = (symbol_t) { .address = address, .size = size, .name_offset = name_buffer_size, .flags = flags };

        size_t name_len = strlen(name) + 1;
        name_buffer = realloc(name_buffer, name_buffer_size + name_len);
        memcpy(&name_buffer[name_buffer_size], name, name_len);
        name_buffer_size += name_len;
    }

    fclose(input);

    uint64_t padding = name_buffer_size % sizeof(uint64_t);
    if(padding != 0) padding = sizeof(uint64_t) - padding;

    // Flush to output file
    FILE *output = fopen(argv[2], "w");
    if(output == NULL) {
        fprintf(stderr, "failed to output file `%s`", strerror(errno));
        return EXIT_FAILURE;
    }

    if(fwrite(
           &(header_t) { .identifier[0] = IDENTIFIER1,
                         .identifier[1] = IDENTIFIER2,
                         .identifier[2] = IDENTIFIER3,
                         .identifier[3] = IDENTIFIER4,
                         .revision = REVISION,
                         .names_offset = sizeof(header_t),
                         .names_size = name_buffer_size,
                         .symbols_offset = sizeof(header_t) + name_buffer_size + padding,
                         .symbol_size = sizeof(symbol_t),
                         .symbols_count = symbol_buffer_count },
           sizeof(header_t),
           1,
           output
       ) != 1)
    {
        fprintf(stderr, "failed to write header to output `%s`", strerror(errno));
        return EXIT_FAILURE;
    }

    if(fwrite(name_buffer, 1, name_buffer_size, output) != name_buffer_size) {
        fprintf(stderr, "failed to flush name buffer to output file `%s`", strerror(errno));
        return EXIT_FAILURE;
    }

    uint8_t zero = 0;
    if(fwrite(&zero, 1, padding, output) != padding) {
        fprintf(stderr, "failed to pad output file `%s`", strerror(errno));
        return EXIT_FAILURE;
    }

    if(fwrite(symbol_buffer, sizeof(symbol_t), symbol_buffer_count, output) != symbol_buffer_count) {
        fprintf(stderr, "failed to flush symbols to output file `%s`", strerror(errno));
        return EXIT_FAILURE;
    }

    fclose(output);

    // Free buffers
    if(name_buffer != NULL) free(name_buffer);
    if(symbol_buffer != NULL) free(symbol_buffer);

    return 0;
}
