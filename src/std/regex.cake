// this is a special cake source file for the standard library
// as much language implementation as is reasonable will live here

// there are some forbidden language features being used that may or may not be allowed in the future,
//   all of which are commented below:
//     - declaring/overriding/writing special members "u8 $size"
//     - using an ellipses for deferred implementation "{ ... }"

namespace std.regex {
    enum flags {
        ECMA = 1
    }

    bool          contains(string& s, string& pattern, i64 flags = flags.ECMA)             { ... }  // forbidden expression
    bool          is_match(string& s, string& pattern, i64 flags = flags.ECMA)             { ... }  // forbidden expression
    array<string> match(string& s, string& pattern, i64 flags = flags.ECMA)                { ... }  // forbidden expression
    string        replace(string& s, string& pattern, string& new, i64 flags = flags.ECMA) { ... }  // forbidden expression
    array<string> search(string& s, string& pattern, i64 flags = flags.ECMA)               { ... }  // forbidden expression
}
