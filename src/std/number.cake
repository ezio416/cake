// this is a special cake source file for the standard library
// as much language implementation as is reasonable will live here

// there are some forbidden language features being used that may or may not be allowed in the future,
//   all of which are commented below:
//     - declaring/overriding/writing special members "u8 $size"
//     - using an ellipses for deferred implementation "{ ... }"

namespace std {
    class char : u8 { }

    class f32 : float {
        float {
            f32 acos()                 { return math.acos(this); }
            f32 asin()                 { return math.asin(this); }
            f32 atan()                 { return math.atan(this); }
            f32 ceil()                 { return math.ceil(this); }
            f32 cos()                  { return math.cos(this); }
            f32 floor()                { return math.floor(this); }
            f32 round(i8 decimals = 0) { return math.round(this, decimals); }
            f32 sin()                  { return math.sin(this); }
            f32 tan()                  { return math.tan(this); }
            f32 to_deg()               { return math.to_deg(this); }
            f32 to_rad()               { return math.to_rad(this); }
        }

        number {
            f32 abs()          { return math.abs(this); }
            f32 max(f32 other) { return math.max(this, other); }
            f32 min(f32 other) { return math.min(this, other); }
            f32 pow(f32 exp)   { return math.pow(this, exp); }
            f32 sqrt()         { return math.sqrt(this); }
        }
    }

    class f64 : float {
        float {
            f64 acos()                 { return math.acos(this); }
            f64 asin()                 { return math.asin(this); }
            f64 atan()                 { return math.atan(this); }
            f64 ceil()                 { return math.ceil(this); }
            f64 cos()                  { return math.cos(this); }
            f64 floor()                { return math.floor(this); }
            f64 round(i8 decimals = 0) { return math.round(this, decimals); }
            f64 sin()                  { return math.sin(this); }
            f64 tan()                  { return math.tan(this); }
            f64 to_deg()               { return math.to_deg(this); }
            f64 to_rad()               { return math.to_rad(this); }
        }

        number {
            f64 abs()          { return math.abs(this); }
            f64 max(f32 other) { return math.max(this, other); }
            f64 min(f32 other) { return math.min(this, other); }
            f64 pow(f64 exp)   { return math.pow(this, exp); }
            f64 sqrt()         { return math.sqrt(this); }
        }
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
        integer {
            range<i8> $range = 0xFF..=0x7F;  // forbidden special declaration
        }

        type {
            u8 $size = 1;  // forbidden special declaration
        }
    }

    class i16 : integer {
        integer {
            range<i16> $range = 0xFFFF..=0x7FFF;  // forbidden special declaration
        }

        type {
            u8 $size = 2;  // forbidden special declaration
        }
    }

    class i32 : integer {
        integer {
            range<i32> $range = 0xFFFF'FFFF..=0x7FFF'FFFF;  // forbidden special declaration
        }

        type {
            u8 $size = 4;  // forbidden special declaration
        }
    }

    class i64 : integer {
        integer {
            range<i64> $range = 0xFFFF'FFFF'FFFF'FFFF..=0x7FFF'FFFF'FFFF'FFFF;  // forbidden special declaration
        }

        type {
            u8 $size = 8;  // forbidden special declaration
        }
    }

    abstract class integer : number {
        castable {
            option<bool> $as() {
                return this != 0;
            }
        }

        range<integer> $range;  // forbidden special recursive declaration
    }

    abstract class number : primitive {
        number abs();
        number max(number other);
        number min(number other);
        number pow(number exp);
        number sqrt();
    }

    class u8 : integer {
        integer {
            range<u8> $range = 0..=0xFF;  // forbidden special declaration
        }

        type {
            u8 $size = 1;  // forbidden special declaration
        }
    }

    class u16 : integer {
        integer {
            range<u16> $range = 0..=0xFFFF;  // forbidden special declaration
        }

        type {
            u8 $size = 2;  // forbidden special declaration
        }
    }

    class u32 : integer {
        integer {
            range<u32> $range = 0..=0xFFFF'FFFF;  // forbidden special declaration
        }

        type {
            u8 $size = 4;  // forbidden special declaration
        }
    }

    class u64 : integer {
        integer {
            range<u64> $range = 0..=0xFFFF'FFFF'FFFF'FFFF;  // forbidden special declaration
        }

        type {
            u8 $size = 8;  // forbidden special declaration
        }
    }
}
