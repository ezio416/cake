// c 2025-01-02
// m 2025-01-09

#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include "cake.h"

typedef bool         cake_bool;
typedef int_fast8_t  cake_int1;  // -128 - 127
typedef int_fast16_t cake_int2;  // -32768 - 32767
typedef int_fast32_t cake_int4;  // -2.1b - 2.1b
typedef int_fast64_t cake_int8;  // -9e18 - 9e18

// typedef _Decimal32   dec4;
// typedef struct {
//     cake_int1 num, exp;
// } dec2;

static void cake_class_base_RefAdd(struct cake_class_base *this) {
    this->refc += 1;
}
static void cake_class_base_RefRem(struct cake_class_base *this) {
    if (this->refc > 0)
        this->refc -= 1;
}
static struct cake_class_base new(void) {
    static cake_int8 id = 0;
    return (struct cake_class_base){.id=id++, .refc=0, .RefAdd=&cake_class_base_RefAdd, .RefRem=&cake_class_base_RefRem};
}
const struct _cake_class_base cake_class_base={.new=&new};

void print(const char *text) {
    printf("%s\n", text);
}

int main(int argc, char *argv[]) {
    print("hello world");

    // cake_bool b = false;

    // cake_int2 j = 0;
    // j += 32767;
    // j++;
    // printf("%d", j);

    // cake_int4 i = 0;
    // i += 2'147'483'647;
    // i++;
    // printf("%d\n", i);

    // dec4 d = 1.23;
    // d.
    // printf("%.3f", d);

    struct cake_class_base b = cake_class_base.new();
    printf("%d\n", b.id);
    struct cake_class_base b2 = cake_class_base.new();
    printf("%d\n", b2.id);
    // printf("%d\n", b.refc);
    // b.RefAdd(&b);
    // printf("%d\n", b.refc);
    // b.RefRem(&b);
    // printf("%d\n", b.refc);

    // cake_base_RefAdd(&b);
    // printf("%d", b.refc);

    return 0;
}
