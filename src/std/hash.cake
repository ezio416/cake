// this is a special cake source file for the standard library
// as much language implementation as is reasonable will live here

// there are some forbidden language features being used that may or may not be allowed in the future,
//   all of which are commented below:
//     - declaring/overriding/writing special members "u8 $size"
//     - using an ellipses for deferred implementation "{ ... }"

namespace std.hash {
    string& from_base64(string& s) { ... }  // forbidden expression
    string& md5(string& s)         { ... }  // forbidden expression
    string& sha1(string& s)        { ... }  // forbidden expression
    string& sha256(string& s)      { ... }  // forbidden expression
    string& sha512(string& s)      { ... }  // forbidden expression
    string& to_base64(string& s)   { ... }  // forbidden expression
}
