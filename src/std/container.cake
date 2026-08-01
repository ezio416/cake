// this is a special cake source file for the standard library
// as much language implementation as is reasonable will live here

// there are some forbidden language features being used that may or may not be allowed in the future,
//   all of which are commented below:
//     - declaring/overriding/writing special members "u8 $size"
//     - using an ellipses for deferred implementation "{ ... }"

namespace std {
    class array : container {
        option $at(i64 index) {
            return $at(signed_index(index));
        }

        option $at(u64 index) {
            if (index >= $length) {
                return none;
            }

            ...  // forbidden expression
        }

        mut option $replace(i64 index, type& item) {
            return $replace(signed_index(index), item);
        }

        mut option $replace(u64 index, type& item) {
            if (index >= $length) {
                return none;
            }

            ...  // forbidden expression
        }

        result<array> $slice(range<i64>& r) {
            return $slice(r as range<u64>);
        }

        result<array> $slice(range<u64>& r) {
            if (r.start >= r.end or r.end >= $length) {
                return error("invalid range");
            }

            ...  // forbidden expression
        }

        array<u64>  every_index_of(type& item)  { ... }  // forbidden expression
        bool        exists(type& item)          { ... }  // forbidden expression
        option<u64> index_of(type& item)       { ... }  // forbidden expression
        mut void    insert(type& item)         { ... }  // forbidden expression
        option<u64> last_index_of(type& item)  { ... }  // forbidden expression
        mut void    reverse()                  { ... }  // forbidden expression

        u64 signed_index(i64 index) {
            return index < 0 ? $length + index : index as u64;
        }

        mut result sort(sort_func& f) {
            if ($length < 2) {
                return error("array has < 2 elements");
            }

            ...  // forbidden expression
        }

        mut result sort_asc() {
            if ($length < 2) {
                return error("array has < 2 elements");
            }

            ...  // forbidden expression
        }

        mut result sort_asc(range<i64>& r) {
            return sort_asc(r as range<u64>);
        }

        mut result sort_asc(range<u64>& r) {
            if ($length < 2) {
                return error("array has < 2 elements");
            }

            if (r.start >= r.end or r.end >= $length) {
                return error("invalid range");
            }

            ...  // forbidden expression
        }

        mut result sort_desc() { ... }  // forbidden expression

        mut result sort_desc(range<i64>& r) {
            return sort_desc(r as range<u64>);
        }

        mut result sort_desc(range<u64>& r) {
            if ($length < 2) {
                return error("array has < 2 elements");
            }

            if (r.start >= r.end or r.end >= $length) {
                return error("invalid range");
            }

            ...  // forbidden expression
        }

        mut option take(i64 index) {
            return take(signed_index(index));
        }

        mut option take(u64 index) {
            if (index >= $length) {
                return none;
            }

            ...  // forbidden expression
        }

        mut result<array> take_slice(range<i64>& r) {
            return $slice(r as range<u64>);
        }

        mut result<array> take_slice(range<u64>& r) {
            if (r.start >= r.end or r.end >= $length) {
                return error("invalid range");
            }

            ...  // forbidden expression
        }
    }

    class bytes : array {
        u64          $index;  // forbidden special declaration
        override @u8 $type;   // forbidden special override declaration

        bool finished() {
            return $index == $capacity;
        }

        bool   read_bool()                            { ... }  // forbidden expression
        bytes  read_bytes(u64 size)                   { ... }  // forbidden expression
        char   read_char()                            { ... }  // forbidden expression
        f32    read_f32()                             { ... }  // forbidden expression
        f64    read_f64()                             { ... }  // forbidden expression
        string read_hex(u64 size, bool upper = false) { ... }  // forbidden expression
        i8     read_i8()                              { ... }  // forbidden expression
        i16    read_i16()                             { ... }  // forbidden expression
        i32    read_i32()                             { ... }  // forbidden expression
        i64    read_i64()                             { ... }  // forbidden expression
        string read_string(u64 size)                  { ... }  // forbidden expression
        u8     read_u8()                              { ... }  // forbidden expression
        u16    read_u16()                             { ... }  // forbidden expression
        u32    read_u32()                             { ... }  // forbidden expression
        u64    read_u64()                             { ... }  // forbidden expression

        mut void reset() {
            seek(0);  // forbidden special write
        }

        mut void resize(u64 size) {
            ...  // forbidden expression

            $capacity = size;  // forbidden special write
        }

        mut void seek(i64 index) {
            seek(index < 0 ? $capacity + index : index as u64);
        }

        mut void seek(u64 index) {
            if (index < $capacity) {
                $index = index;  // forbidden special write
            }
        }

        mut void write(bytes& b, u64 size) { ... }  // forbidden expression
        mut void write(primitive p)        { ... }  // forbidden expression
        mut void write(string& s)          { ... }  // forbidden expression
        mut void write_hex(string& h)      { ... }  // forbidden expression
    }

    abstract class container {
        u64   $capacity;  // forbidden special declaration
        u64   $length;    // forbidden special declaration
        @type $type;      // forbidden special declaration

        mut void $init<@type T>() {
            $type = T;  // forbidden special write
        }

        mut void clear();
        bool     is_empty();
    }

    class dict : set {
        option<type&> $get(string& key)              { ... }  // forbidden expression
        mut void      $set(string& key, type& value) { ... }  // forbidden expression

        mut option<type&> take(string& key) { ... }  // forbidden expression
    }

    abstract class keyed_container : container { }

    class range : container {
        number $end;        // forbidden special declaration
        bool   $inclusive;  // forbidden special declaration
        number $start;      // forbidden special declaration

        override mut void $init<@number T>(number start, number end, bool inclusive = false) {
            $start = start;          // forbidden special write
            $end = end;              // forbidden special write
            $inclusive = inclusive;  // forbidden special write
        }
    }

    class set : keyed_container { }

    class string : array {
        override @char $type;  // forbidden special override declaration

        bool          ends_with(string& s)                                 { ... }  // forbidden expression
        bool          is_alpha()                                           { ... }  // forbidden expression
        bool          is_alphanum()                                        { ... }  // forbidden expression
        bool          is_ascii()                                           { ... }  // forbidden expression
        bool          is_base59()                                          { ... }  // forbidden expression
        bool          is_base64()                                          { ... }  // forbidden expression
        bool          is_bin()                                             { ... }  // forbidden expression
        bool          is_hex()                                             { ... }  // forbidden expression
        bool          is_num()                                             { ... }  // forbidden expression
        bool          is_octal()                                           { ... }  // forbidden expression
        bool          is_space()                                           { ... }  // forbidden expression
        string        join(array<string>& strings)                         { ... }  // forbidden expression
        string        lower()                                              { ... }  // forbidden expression
        string        mut_join(array<string>& strings)                     { ... }  // forbidden expression
        mut void      mut_lower()                                          { ... }  // forbidden expression
        mut void      mut_replace(string& old, string& new, u64 count = 1) { ... }  // forbidden expression
        mut void      mut_upper()                                          { ... }  // forbidden expression
        string        replace(string& old, string& new, u64 count = 1)     { ... }  // forbidden expression
        array<string> split(string& delimeter)                             { ... }  // forbidden expression
        bool          starts_with(string& s)                               { ... }  // forbidden expression
        mut void      trim()                                               { ... }  // forbidden expression
        string        upper()                                              { ... }  // forbidden expression
    }
}
