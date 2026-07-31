// this is a special cake source file for the standard library
// as much language implementation as is reasonable will live here

// there are some forbidden language features being used that may or may not be allowed in the future,
//   all of which are commented below:
//     - declaring/overriding/writing special members "u8 $size"
//     - using an ellipses for deferred implementation "{ ... }"

namespace std.json {
    enum type {
        array,
        bool,
        null,
        number,
        object,
        string
    }

    class value {
        type type;
    }

    value         array()                 { ... }  // forbidden expression
    result<value> from_file(string& path) { ... }  // forbidden expression
    value         object()                { ... }  // forbidden expression
    result<value> parse(string& s)        { ... }  // forbidden expression
}
