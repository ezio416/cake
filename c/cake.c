// c 2025-01-02
// m 2025-01-05

#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include "cake.h"

static double Complex_abs(struct Complex *this) {
    return sqrt(this->re * this->re + this->im * this->im);
}
static struct Complex Complex_new(double real, double imag) {
    return (struct Complex){.re=real, .im=imag, .abs=&Complex_abs};
}
const struct ComplexClass Complex={.new=&Complex_new};

void print(const char *text) {
    printf("%s\n", text);
}

int main(int argc, char *argv[]) {
    print("hello world");

    struct Complex c=Complex.new(3., -4.);
    printf("%.3f, %.3f\n", c.re, c.im);
    printf("%.3f\n", c.abs(&c));

    return 0;
}
