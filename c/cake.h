// c 2025-01-05
// m 2025-01-06

#ifndef cake_h
#define cake_h

void print(const char *text);
int main(int argc, char *argv[]);

static void cake_class_base_RefAdd(struct cake_class_base *this);
static void cake_class_base_RefRem(struct cake_class_base *this);
struct cake_class_base {
    int id, refc;
    void (*RefAdd)(struct cake_class_base *this);
    void (*RefRem)(struct cake_class_base *this);
};
extern const struct _cake_class_base {
    struct cake_class_base (*new)(void);
} cake_class_base;

#endif
