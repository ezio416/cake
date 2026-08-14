alias i32 int;  // a comment
alias <std.dict<int>&><i8, mut u16&, @type> func;

class C : I, S {
    override {
        private void hello() {}
    }

    i32 x = 4;

    void $init() {
        // std.print(x);
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
}

i32 add(i32 i, i8 j) {
    del i;
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
    std.string bye() { return ""; }
    final i32 world(i8 i) { return 42; }
}

final interface J : I {
    override {
        void hello() { }
    }
}

namespace N {
    alias int i;
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
    std.array<std.dict<N.i>> s,
    @type                    T
> {
    a,
    b(i),
    c(e),
    d(j),
    e(s),
    f,
    g(T),
    h,
}
