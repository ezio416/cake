// this is a special cake source file for the standard library
// as much language implementation as is reasonable will live here

// there are some forbidden language features being used that may or may not be allowed in the future,
//   all of which are commented below:
//     - declaring/overriding/writing special members "u8 $size"
//     - using an ellipses for deferred implementation "{ ... }"

namespace std.net {
    namespace http {
        class request {
            string url;
        }

        request delete(string& url)                                                                                 { ... }  // forbidden expression
        request get(string& url)                                                                                    { ... }  // forbidden expression
        request head(string& url)                                                                                   { ... }  // forbidden expression
        request options(string& url, string& body = "", string& content_type = "application/x-www-form-urlencoded") { ... }  // forbidden expression
        request patch(string& url, string& body = "", string& content_type = "application/x-www-form-urlencoded")   { ... }  // forbidden expression
        request post(string& url, string& body = "", string& content_type = "application/x-www-form-urlencoded")    { ... }  // forbidden expression
        request put(string& url, string& body = "", string& content_type = "application/x-www-form-urlencoded")     { ... }  // forbidden expression
    }

    string url_decode(string& s) { ... }  // forbidden expression
    string url_encode(string& s) { ... }  // forbidden expression
}
