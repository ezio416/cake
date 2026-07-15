alias i32 int;  // alias

class C : I, S {  // cls
    override void $init() {
        std.print(4);
    }
}

int i;  // decl

enum E {  // enum
    a, b = 2, c
}

void $main() {  // func
    (6 + 7) ** 8 * -9
}

interface I {  // intf
    void hello();
}

namespace N {  // ns
    alias int i;
}

struct S {  // strc
    N.i j = -42e1;
}
