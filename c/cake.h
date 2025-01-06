// c 2025-01-05
// m 2025-01-05

#ifndef CAKE_TEST_MAIN
#define CAKE_TEST_MAIN

struct Complex {
    double re, im;
    double (*abs)(struct Complex *this);
};
extern const struct ComplexClass {
    struct Complex (*new)(double real, double imag);
} Complex;

#endif
