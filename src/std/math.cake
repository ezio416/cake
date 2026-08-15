// this is a special cake source file for the standard library
// as much language implementation as is reasonable will live here

// there are some forbidden language features being used that may or may not be allowed in the future,
//   all of which are commented below:
//     - declaring/overriding/writing special members "u8 $size"
//     - using an ellipses for deferred implementation "{ ... }"

namespace std.math {
    f64 E           = 2.71828'18284'59045;
    f32 E_32        = 2.71828'1;
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

    f32 abs(f32 f) { return f < 0.0 ? -f : f; }
    f64 abs(f64 f) { return f < 0.0 ? -f : f; }
    i8  abs(i8  i) { return i < 0   ? -i : i; }
    i16 abs(i16 i) { return i < 0   ? -i : i; }
    i32 abs(i32 i) { return i < 0   ? -i : i; }
    i64 abs(i64 i) { return i < 0   ? -i : i; }
    u8  abs(u8  u) { return u; }
    u16 abs(u16 u) { return u; }
    u32 abs(u32 u) { return u; }
    u64 abs(u64 u) { return u; }

    f32 acos(f32 f) { ... }  // forbidden expression
    f64 acos(f64 f) { ... }  // forbidden expression

    f32 asin(f32 f) { ... }  // forbidden expression
    f64 asin(f64 f) { ... }  // forbidden expression

    f32 atan(f32 f) { ... }  // forbidden expression
    f64 atan(f64 f) { ... }  // forbidden expression

    f32 ceil(f32 f) { ... }  // forbidden expression
    f64 ceil(f64 f) { ... }  // forbidden expression

    f32 cos(f32 f) { ... }  // forbidden expression
    f64 cos(f64 f) { ... }  // forbidden expression

    f32 floor(f32 f) { ... }  // forbidden expression
    f64 floor(f64 f) { ... }  // forbidden expression

    f32 log(f32 f, i32 base) { ... }  // forbidden expression
    f64 log(f64 f, i64 base) { ... }  // forbidden expression

    f32 max(f32 f, f32 g) { return f >= g ? f : g; }
    f64 max(f64 f, f64 g) { return f >= g ? f : g; }
    i8  max(i8  i, i8  j) { return i >= j ? i : j; }
    i16 max(i16 i, i16 j) { return i >= j ? i : j; }
    i32 max(i32 i, i32 j) { return i >= j ? i : j; }
    i64 max(i64 i, i64 j) { return i >= j ? i : j; }
    u8  max(u8  u, u8  v) { return u >= v ? u : v; }
    u16 max(u16 u, u16 v) { return u >= v ? u : v; }
    u32 max(u32 u, u32 v) { return u >= v ? u : v; }
    u64 max(u64 u, u64 v) { return u >= v ? u : v; }

    f32 min(f32 f, f32 g) { return f <= g ? f : g; }
    f64 min(f64 f, f64 g) { return f <= g ? f : g; }
    i8  min(i8  i, i8  j) { return i <= j ? i : j; }
    i16 min(i16 i, i16 j) { return i <= j ? i : j; }
    i32 min(i32 i, i32 j) { return i <= j ? i : j; }
    i64 min(i64 i, i64 j) { return i <= j ? i : j; }
    u8  min(u8  u, u8  v) { return u <= v ? u : v; }
    u16 min(u16 u, u16 v) { return u <= v ? u : v; }
    u32 min(u32 u, u32 v) { return u <= v ? u : v; }
    u64 min(u64 u, u64 v) { return u <= v ? u : v; }

    f32 pow(f32 x, f32 y) { ... }  // forbidden expression
    f64 pow(f64 x, f64 y) { ... }  // forbidden expression

    f32 rand(range<f32>& r) { ... }  // forbidden expression
    f64 rand(range<f64>& r) { ... }  // forbidden expression
    i8  rand(range<i8>& r)  { ... }  // forbidden expression
    i16 rand(range<i16>& r) { ... }  // forbidden expression
    i32 rand(range<i32>& r) { ... }  // forbidden expression
    i64 rand(range<i64>& r) { ... }  // forbidden expression
    u8  rand(range<u8>& r)  { ... }  // forbidden expression
    u16 rand(range<u16>& r) { ... }  // forbidden expression
    u32 rand(range<u32>& r) { ... }  // forbidden expression
    u64 rand(range<u64>& r) { ... }  // forbidden expression

    f32 round(f32 f, i8 decimals = 0) { ... }  // forbidden expression
    f64 round(f64 f, i8 decimals = 0) { ... }  // forbidden expression

    f32 sin(f32 f) { ... }  // forbidden expression
    f64 sin(f64 f) { ... }  // forbidden expression

    f32 sqrt(f32 f) { return pow(f, 0.5); }
    f64 sqrt(f64 f) { return pow(f, 0.5); }

    f32 tan(f32 f) { ... }  // forbidden expression
    f64 tan(f64 f) { ... }  // forbidden expression

    f32 to_deg(f32 rad) { ... }  // forbidden expression
    f64 to_deg(f64 rad) { ... }  // forbidden expression

    f32 to_rad(f32 deg) { ... }  // forbidden expression
    f64 to_rad(f64 deg) { ... }  // forbidden expression
}
