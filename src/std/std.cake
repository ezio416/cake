// this is a special cake source file for the standard library
// as much language implementation as is reasonable will live here
// primitive types are aliased to the global namespace at the bottom

// there are some forbidden language features being used that may or may not be allowed in the future,
//   all of which are commented below:
//     - declaring/overriding/writing special members "u8 $size"
//     - using an ellipses for deferred implementation "{ ... }"

namespace std {
    union option<type& t> {
        some(t),
        none
    }

    union result<type& t, string& msg> {
        ok(t),
        error(msg)
    }

    class bool : primitive {
        castable {
            option<integer> $as() {
                return this ? 1 : 0;
            }

            option<string> $as() {
                return this ? "true" : "false";
            }
        }

        type {
            u8 $size = 1;  // forbidden special declaration
        }
    }

    interface castable {
        option $as();
    }

    interface context_manager {
        result $enter();
        void   $exit();
    }

    abstract class primitive { }

    abstract class type : castable {
        type   $data;  // forbidden special recursive declaration
        bool   $mut;   // forbidden special recursive declaration
        string $name;  // forbidden special recursive declaration
        u8     $size;  // forbidden special recursive declaration
    }

    class void : primitive {
        castable {
            final option $as() {
                return none;
            }
        }
    }
}

alias std.bool bool;
alias std.char char;
alias std.f32  f32;
alias std.f64  f64;
alias std.i8   i8;
alias std.i16  i16;
alias std.i32  i32;
alias std.i64  i64;
alias std.u8   u8;
alias std.u16  u16;
alias std.u32  u32;
alias std.u64  u64;
alias std.void void;
