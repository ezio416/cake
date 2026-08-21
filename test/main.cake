alias i32 int;  // a comment
// alias <std.dict<int>&><i8, mut u16&, @type> func;
// alias std.dict<std.array<i8>> dai;

class C : I, S {
    override {
        void hello() {
            // std.string s = "ha";
            // std.string t = #"yes";
            // std.string u = "hello\b\f\n\r\t\v\0\12\345\x67\u89ab\Ucdef0123world";
            // std.string v = "😀";
        }
    }

    mut i32 x = 4;
    // auto y;

    void $init() {
        i32 m = 2;
        // x >>= 2;
    }
}

enum E {
    a = 3,
    b = 5
}

int i;
auto j = 2 >> 7;

void main() {
    // (6 + 7) ** 8 * -9

    if (true) {
        i8 a;
    } else if (false) {
        u8 b;
    } else if (0) {
        char c;
    } else {
        f64 d;
    }

    for (i8 i in 0..5) {
        f32 f;
    }

    while (true) {
        del std;
    }

    do {
        i8 o;
    }

    do {
        i16 p;
    } while (1);

    do {
        i32 q;
    }

    while (42) {
        u8 u;
    }

    with (std.math.PI) as pi {
        f64 tau = pi * 2.0;
    }

    switch (num) {
        case (0) {
            break;
        }
        case (2) {
            continue;
        }
        default {
            return;
        }
    }
}

i32 add(i32 i, i8 j) {
    del i;
    i8 k;
    try {
        break 4;
        continue;
    } catch {
        continue 3.14;
        break;
    }
    return i + j;
}

interface I {
    void hello() { }
    // std.string bye() { return ""; }
    final i32 world(i8 i) { return 42; }
}

final interface J : I {
    override {
        void hello() {
            // std.string s = "ham";
        }
    }
}

namespace N {
    alias int i;

    class D {
        ;
    }

    class Nc : global.C {
        ;
    }

    enum Ne {
        foo = 42,
        bar = 69,
        baz = 1337,
    }

    enum Ne2 {
        abc = 3,
        def,
        ghi = 12,
    }

    i32 v = 5;
}

class Nd : N.D {
    ;
}

struct S {
    N.i j = -42e1;
    protected final global.int g;
}

abstract struct AS {
    ;
}

final struct FS : S, AS {
    override {
        N.i j;
    }

    i8 i;
}

union U<
    i32                      i,
    E                        e,
    N.i                      j,
    // std.array<std.dict<N.i>> s,
    // @type                    T
> {
    a,
    b(i),
    c(e),
    d(j),
    // e(s),
    f,
    // g(T),
    h,
}
