// this is a special cake source file for the standard library
// as much language implementation as is reasonable will live here

// there are some forbidden language features being used that may or may not be allowed in the future,
//   all of which are commented below:
//     - declaring/overriding/writing special members "u8 $size"
//     - using an ellipses for deferred implementation "{ ... }"

namespace std {
    class char : u8 { }

    class f32 : float {
        f32 abs()      { return math.abs(this); }
        f32 acos()     { return math.acos(this); }
        f32 asin()     { return math.asin(this); }
        f32 atan()     { return math.atan(this); }
        f32 ceil()     { return math.ceil(this); }
        f32 cos()      { return math.cos(this); }
        f32 floor()    { return math.floor(this); }
        f32 pow(f32 e) { return math.pow(this, e); }
        f32 sin()      { return math.sin(this); }
        f32 sqrt()     { return math.sqrt(this); }
        f32 tan()      { return math.tan(this); }
        f32 to_deg()   { return math.to_deg(this); }
        f32 to_rad()   { return math.to_rad(this); }
    }

    class f64 : float {
        f64 abs()      { return math.abs(this); }
        f64 acos()     { return math.acos(this); }
        f64 asin()     { return math.asin(this); }
        f64 atan()     { return math.atan(this); }
        f64 ceil()     { return math.ceil(this); }
        f64 cos()      { return math.cos(this); }
        f64 floor()    { return math.floor(this); }
        f64 pow(f64 e) { return math.pow(this, e); }
        f64 sin()      { return math.sin(this); }
        f64 sqrt()     { return math.sqrt(this); }
        f64 tan()      { return math.tan(this); }
        f64 to_deg()   { return math.to_deg(this); }
        f64 to_rad()   { return math.to_rad(this); }
    }

    abstract class float : number { }

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

    abstract class number : primitive { }

    class u8 : integer {
        override u64 $max  = 0xFF;  // forbidden special override declaration
        override i64 $min  = 0;     // forbidden special override declaration
        override u8  $size = 1;     // forbidden special override declaration
    }

    class u16 : integer {
        override u64 $max  = 0xFFFF;  // forbidden special override declaration
        override i64 $min  = 0;       // forbidden special override declaration
        override u8  $size = 2;       // forbidden special override declaration
    }

    class u32 : integer {
        override u64 $max  = 0xFFFF'FFFF;  // forbidden special override declaration
        override i64 $min  = 0;            // forbidden special override declaration
        override u8  $size = 4;            // forbidden special override declaration
    }

    class u64 : integer {
        override u64 $max  = 0xFFFF'FFFF'FFFF'FFFF;  // forbidden special override declaration
        override i64 $min  = 0;                      // forbidden special override declaration
        override u8  $size = 8;                      // forbidden special override declaration
    }
}
