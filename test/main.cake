alias i32 int;  // a comment
alias <std.dict<int>&><i8, mut u16&, @type> func;

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

union U<i32 i, E e, N.i j, std.array<std.dict<N.i>> s, @type T> {
    a,
    b(i),
    c(e),
    d(j),
    e(s),
    f,
    g(T),
    h,
}
