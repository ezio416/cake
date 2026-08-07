alias i32 int;  // a comment
alias <std.dict<int>&><i8, mut u16&, @type> func;

// class C : I, S {
//     void $init() {
//         std.print(4);
//     }
// }

enum E {
    a = 3,
    b = 5
}

int i;
auto j = 2 >> 7;

void main() {
    (6 + 7) ** 8 * -9
}

void add(i32 i, i8 j) {
    return i + j;
}

// interface I {
//     void hello();
// }

namespace N {
    alias int i;
}

struct S {
    N.i j = -42e1;
    protected final global.int g;
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
