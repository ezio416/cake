alias i32 int;

class C : I, S {
    void $init() {
        std.print(4);
    }
}

enum E {
    a = 3,
    b = 5
}

int i;

void main() {
    (6 + 7) ** 8 * -9
}

interface I {
    void hello();
}

namespace N {
    alias int i;
}

struct S {
    N.i j = -42e1;
}

union U<i32 i, E e, N.i j> {
    a,
    b(i),
    c(e),
    d(j),
    e
}
