// this is a special cake source file for the standard library
// as much language implementation as is reasonable will live here

// there are some forbidden language features being used that may or may not be allowed in the future,
//   all of which are commented below:
//     - declaring/overriding/writing special members "u8 $size"
//     - using an ellipses for deferred implementation "{ ... }"

namespace std.reflect {
    class Alias : Node {
        ;
    }

    class Class : Inheritable {
        ;
    }

    class Declaration : Node {
        ;
    }

    class Enum : Node {
        ;
    }

    class Function : container, Node {
        array<@type> $params;  // forbidden special declaration

        void $call() { ... }  // forbidden expression

        mut void $init<@type T><array<@type> P>() {
            super.$init<T>();
            $params = P;                                           // forbidden special write
            $name += #"<{", ".join($params as array<string&>)}>";  // forbidden special write
        }

        override option<json.value> $as() {
            return none;
        }
    }

    class Inheritable : Node {
        ;
    }

    class Interface : Inheritable {
        ;
    }

    class Namespace : Node {
        ;
    }

    class Node {
        ;
    }

    class Struct : Inheritable {
        ;
    }

    class traceback {
        ;
    }

    class Union : Node {
        ;
    }

    option<Node&> get_node(string& id) { ... }  // forbidden expression
    traceback&    get_traceback()      { ... }  // forbidden expression
    dict<Node>&   globals()            { ... }  // forbidden expression
    dict<Node>&   locals()             { ... }  // forbidden expression
}
