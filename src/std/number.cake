// this is a special cake source file for the standard library
// as much language implementation as is reasonable will live here

// there are some forbidden language features being used that may or may not be allowed in the future,
//   all of which are commented below:
//     - declaring/overriding/writing special members "u8 $size"
//     - using an ellipses for deferred implementation "{ ... }"

namespace std {
    class char : u8 { }

    class f32 : float {
        override f32 abs()                  { return math.abs(this); }
        override f32 acos()                 { return math.acos(this); }
        override f32 asin()                 { return math.asin(this); }
        override f32 atan()                 { return math.atan(this); }
        override f32 ceil()                 { return math.ceil(this); }
        override f32 cos()                  { return math.cos(this); }
        override f32 floor()                { return math.floor(this); }
        override f32 max(f32 other)         { return math.max(this, other); }
        override f32 min(f32 other)         { return math.min(this, other); }
        override f32 pow(f32 exp)           { return math.pow(this, exp); }
        override f32 round(i8 decimals = 0) { return math.round(this, decimals); }
        override f32 sin()                  { return math.sin(this); }
        override f32 sqrt()                 { return math.sqrt(this); }
        override f32 tan()                  { return math.tan(this); }
        override f32 to_deg()               { return math.to_deg(this); }
        override f32 to_rad()               { return math.to_rad(this); }
    }

    class f64 : float {
        override f64 abs()                  { return math.abs(this); }
        override f64 acos()                 { return math.acos(this); }
        override f64 asin()                 { return math.asin(this); }
        override f64 atan()                 { return math.atan(this); }
        override f64 ceil()                 { return math.ceil(this); }
        override f64 cos()                  { return math.cos(this); }
        override f64 floor()                { return math.floor(this); }
        override f64 max(f32 other)         { return math.max(this, other); }
        override f64 min(f32 other)         { return math.min(this, other); }
        override f64 pow(f64 exp)           { return math.pow(this, exp); }
        override f64 round(i8 decimals = 0) { return math.round(this, decimals); }
        override f64 sin()                  { return math.sin(this); }
        override f64 sqrt()                 { return math.sqrt(this); }
        override f64 tan()                  { return math.tan(this); }
        override f64 to_deg()               { return math.to_deg(this); }
        override f64 to_rad()               { return math.to_rad(this); }
    }

    abstract class float : number {
        float acos();
        float asin();
        float atan();
        float ceil();
        float cos();
        float floor();
        float round(i8 decimals);
        float sin();
        float tan();
        float to_deg();
        float to_rad();
    }

    class i8 : integer {
        override u64 $max  = 0x7F;  // forbidden special override declaration
        override i64 $min  = 0xFF;  // forbidden special override declaration
        override u8  $size = 1;     // forbidden special override declaration
    }

    class i16 : integer {
        override u64 $max  = 0x7FFF;  // forbidden special override declaration
        override i64 $min  = 0xFFFF;  // forbidden special override declaration
        override u8  $size = 2;       // forbidden special override declaration
    }

    class i32 : integer {
        override u64 $max  = 0x7FFF'FFFF;  // forbidden special override declaration
        override i64 $min  = 0xFFFF'FFFF;  // forbidden special override declaration
        override u8  $size = 4;            // forbidden special override declaration
    }

    class i64 : integer {
        override u64 $max  = 0x7FFF'FFFF'FFFF'FFFF;  // forbidden special override declaration
        override i64 $min  = 0xFFFF'FFFF'FFFF'FFFF;  // forbidden special override declaration
        override u8  $size = 8;                      // forbidden special override declaration
    }

    abstract class integer : number {
        u64 $max;  // forbidden special recursive declaration
        i64 $min;  // forbidden special recursive declaration

        override option<bool> $as() {
            return this != 0;
        }
    }

    abstract class number : primitive {
        number abs();
        number max(number other);
        number min(number other);
        number pow(number exp);
        number sqrt();
    }

    abstract class unsigned_integer : integer {
        override i64 $min = 0;  // forbidden special override declaration
    }

    class u8 : unsigned_integer {
        override u64 $max  = 0xFF;  // forbidden special override declaration
        override u8  $size = 1;     // forbidden special override declaration
    }

    class u16 : unsigned_integer {
        override u64 $max  = 0xFFFF;  // forbidden special override declaration
        override u8  $size = 2;       // forbidden special override declaration
    }

    class u32 : unsigned_integer {
        override u64 $max  = 0xFFFF'FFFF;  // forbidden special override declaration
        override u8  $size = 4;            // forbidden special override declaration
    }

    class u64 : unsigned_integer {
        override u64 $max  = 0xFFFF'FFFF'FFFF'FFFF;  // forbidden special override declaration
        override u8  $size = 8;                      // forbidden special override declaration
    }
}
