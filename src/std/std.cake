namespace std.array {
    ;
}

namespace std.bool {
    u8  BITS = 8;
    u64 MAX  = 0x01;
    i64 MIN  = 0;

    bool $true(bool b) {
        return b;
    }
}

namespace std.char {
    u8  BITS = 8;
    u64 MAX  = 0xFF;
    i64 MIN  = 0;

    bool $true(char c) {
        return c != 0;
    }
}

namespace std.csv {
    tree from_file(string& path);
    tree parse(string& s);
}

namespace std.dict {
    ;
}

namespace std.error {
    array<string&> get_last_messages(u64 count = 1);
}

namespace std.generic {
    ;
}

namespace std.hash {
    string& md5(string& s);
    string& sha1(string& s);
    string& sha256(string& s);
    string& sha512(string& s);
}

namespace std.i8 {
    u8  BITS = 8;
    u64 MAX  = 0x7F;
    i64 MIN  = 0xFF;

    bool $true(i8 i) {
        return i != 0;
    }
}

namespace std.i16 {
    u8  BITS = 16;
    u64 MAX  = 0x7FFF;
    i64 MIN  = 0xFFFF;

    bool $true(i16 i) {
        return i != 0;
    }
}

namespace std.i32 {
    u8  BITS = 32;
    u64 MAX  = 0x7FFF'FFFF;
    i64 MIN  = 0xFFFF'FFFF;

    bool $true(i32 i) {
        return i != 0;
    }
}

namespace std.i64 {
    u8  BITS = 64;
    u64 MAX  = 0x7FFF'FFFF'FFFF'FFFF;
    i64 MIN  = 0xFFFF'FFFF'FFFF'FFFF;

    bool $true(i64 i) {
        return i != 0;
    }
}

namespace std.io {
    void create_dir(string& path);
    void create_file(string& path);
    void copy(string& path, string& target);
    void delete(string& path);
    bool dir_exists(string& path);
    bool exists(string& path);
    bool file_exists(string& path);
    array<string> index_dir(string& path);
    void move(string& path, string& target);
    file open(string& path);
    string read(string& path);
    void set_clipboard(string& text);
    tree walk(string& path);
}

namespace std.json {
    value array();
    value from_file(string& path);
    value object();
    value parse(string& s);
}

namespace std.math {
    f64 E           = 2.71828'18284'59045'2;  // TODO find actual precision
    f32 E_32        = 2.71828'18284'59045'2;  // TODO find actual precision
    f64 NEG_INF     = 0xFFF0'0000'0000'0000;
    f32 NEG_INF_32  = 0xFF80'0000;
    f64 NEG_ZERO    = 0x8000'0000'0000'0000;
    f32 NEG_ZERO_32 = 0x8000'0000
    f64 PI          = 3.14159'26535'89793;
    f32 PI_32       = 3.14159'2;
    f64 POS_INF     = 0x7FF0'0000'0000'0000;
    f32 POS_INF_32  = 0x7F80'0000;
    f64 TAU         = PI * 2.0;
    f32 TAU_32      = P_32 * 2.0;

    f32 abs(f32 f) { return f < 0.0 ? f * -1.0 : f; }
    f64 abs(f64 f) { return f < 0.0 ? f * -1.0 : f; }
    i8  abs(i8  i) { return i < 0   ? i * -1   : i; }
    i16 abs(i16 i) { return i < 0   ? i * -1   : i; }
    i32 abs(i32 i) { return i < 0   ? i * -1   : i; }
    i64 abs(i64 i) { return i < 0   ? i * -1   : i; }
    u8  abs(u8  u) { return u; }
    u16 abs(u16 u) { return u; }
    u32 abs(u32 u) { return u; }
    u64 abs(u64 u) { return u; }

    f32 acos(f32 f);
    f64 acos(f64 f);

    f32 asin(f32 f);
    f64 asin(f64 f);

    f32 atan(f32 f);
    f64 atan(f64 f);

    f32 ceil(f32 f);
    f64 ceil(f64 f);

    f32 cos(f32 f);
    f64 cos(f64 f);

    f32 exp(f32 f);
    f64 exp(f64 f);

    f32 floor(f32 f);
    f64 floor(f64 f);

    f32 log(f32 f, i32 base);
    f64 log(f64 f, i64 base);

    i8  max(i8  i, i8  j) { return i >= j ? i : j; }
    i16 max(i16 i, i16 j) { return i >= j ? i : j; }
    i32 max(i32 i, i32 j) { return i >= j ? i : j; }
    i64 max(i64 i, i64 j) { return i >= j ? i : j; }
    u8  max(u8  u, u8  v) { return u >= v ? u : v; }
    u16 max(u16 u, u16 v) { return u >= v ? u : v; }
    u32 max(u32 u, u32 v) { return u >= v ? u : v; }
    u64 max(u64 u, u64 v) { return u >= v ? u : v; }

    i8  min(i8  i, i8  j) { return i <= j ? i : j; }
    i16 min(i16 i, i16 j) { return i <= j ? i : j; }
    i32 min(i32 i, i32 j) { return i <= j ? i : j; }
    i64 min(i64 i, i64 j) { return i <= j ? i : j; }
    u8  min(u8  u, u8  v) { return u <= v ? u : v; }
    u16 min(u16 u, u16 v) { return u <= v ? u : v; }
    u32 min(u32 u, u32 v) { return u <= v ? u : v; }
    u64 min(u64 u, u64 v) { return u <= v ? u : v; }

    f32 pow(f32 x, f32 y);
    f64 pow(f64 x, f64 y);

    f32 rand(f32 min, f32 max);
    f64 rand(f64 min, f64 max);
    i8  rand(i8  min, i8  max);
    i16 rand(i16 min, i16 max);
    i32 rand(i32 min, i32 max);
    i64 rand(i64 min, i64 max);
    u8  rand(u8  min, u8  max);
    u16 rand(u16 min, u16 max);
    u32 rand(u32 min, u32 max);
    u64 rand(u64 min, u64 max);

    f32 root(f32 f, f32 index);
    f64 root(f64 f, f64 index);

    f32 round(f32 f, i8 decimals = 0);
    f64 round(f64 f, i8 decimals = 0);

    f32 sin(f32 f);
    f64 sin(f64 f);

    f32 sqrt(f32 f);
    f64 sqrt(f64 f);

    f32 tan(f32 f);
    f64 tan(f64 f);

    f32 to_deg(f32 rad);
    f64 to_deg(f64 rad);

    f32 to_rad(f32 deg);
    f64 to_rad(f64 deg);
}

namespace std.net {
    namespace http {
        request delete(string& url);
        request get(string& url);
        request head(string& url);
        request options(string& url, string& body = "", string& content_type = "application/x-www-form-urlencoded");
        request patch(string& url, string& body = "", string& content_type = "application/x-www-form-urlencoded");
        request post(string& url, string& body = "", string& content_type = "application/x-www-form-urlencoded");
        request put(string& url, string& body = "", string& content_type = "application/x-www-form-urlencoded");
    }

    string url_decode(string& s);
    string url_encode(string& s);
}

namespace std.reflect {
    dict<var>& globals();
    dict<var>& locals();
}

namespace std.regex {
    bool contains(string& s, string& pattern, i32 flags = FLAGS.ECMA);
    bool is_match(string& s, string& pattern, i32 flags = FLAGS.ECMA);
    array<string> match(string& s, string& pattern, i32 flags = FLAGS.ECMA);
    string replace(string& s, string& pattern, string& new, i32 flags = FLAGS.ECMA);
    array<string> search(string& s, string& pattern, i32 flags = FLAGS.ECMA);
}

namespace std.set {
    ;
}

namespace std.sql {
    database open(string& path);
}

namespace std.string {
    string join(array<string>& a, string& delimeter = "");
    string repeat(string& s, u64 count);
}

namespace std.sys {
    os& get_os();
    user& get_user();
}

namespace std.time {
    i64 stamp();
}

namespace std.toml {
    tree from_file(string& path);
    tree parse(string& s);
}

namespace std.u8 {
    u8  BITS = 8;
    u64 MAX  = 0xFF;
    i64 MIN = 0;

    bool $true(u8 u) {
        return u != 0;
    }
}

namespace std.u16 {
    u8  BITS = 16;
    u64 MAX  = 0xFFFF;
    i64 MIN  = 0;

    bool $true(u16 u) {
        return u != 0;
    }
}

namespace std.u32 {
    u8  BITS = 32;
    u64 MAX  = 0xFFFF'FFFF;
    i64 MIN  = 0;

    bool $true(u32 u) {
        return u != 0;
    }
}

namespace std.u64 {
    u8  BITS = 64;
    u64 MAX  = 0xFFFF'FFFF'FFFF'FFFF;
    i64 MIN  = 0;

    bool $true(u64 u) {
        return u != 0;
    }
}

namespace std.xml {
    document from_file(string& path);
    document parse(string& s);
}
