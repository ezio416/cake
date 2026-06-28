// comment
void main() {
    i32 i = 0xc;
    i &= 3;
    if (i == 3) {
        return 0;  // another comment
    }
    i++;
    i >> 4;
    bool b = true || false nox true;
    i64 j = 1e23 + 4.5e6 - 7e-89;
    std::assert(j >= 0);
}
