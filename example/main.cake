// c 2025-01-02
// m 2025-01-03

#directive
void main() {//hola
    // a comment
    std::print("hello world");  // lmao
}//adios

namespace MyNamespace {
    int4 num = 2**31 - 1;

    bool IsOkay(int4 n) {
        std::print(std::tostr(n));
        return true;
    }
}

class ClassA {
    ClassA() {}
    void Try() {}
}

class ClassB : ClassA {
    ClassB() {
        super();
    }
}

struct Struct1 {
    bool okay;
}

class ClassC : ClassB, Struct1 {
    override void Try() {
        std::print(okay ? "hello" : "world");
    }
}
