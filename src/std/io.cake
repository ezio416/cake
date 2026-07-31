// this is a special cake source file for the standard library
// as much language implementation as is reasonable will live here

// there are some forbidden language features being used that may or may not be allowed in the future,
//   all of which are commented below:
//     - declaring/overriding/writing special members "u8 $size"
//     - using an ellipses for deferred implementation "{ ... }"

namespace std.io {
    enum mode {
        append = 1,
        read   = 2,
        write  = 4
    }

    class dir {
        array<dir> dirs;
        string     path;
    }

    class file : context_manager {
        mode   mode;
        string path;

        override option<file> $enter() {
            { ... }  // forbidden expression

            return this;
        }

        override void $exit() {
            close();
        }

        void           close()      { ... }  // forbidden expression
        result<string> read()       { ... }  // forbidden expression
        result<bytes>  read_bytes() { ... }  // forbidden expression
    }

    result copy_dir(string& path, string& target) {
        if (!dir_exists(path)) {
            return error("dir not found: " + path);
        }

        { ... }  // forbidden expression
    }

    result copy_file(string& path, string& target) {
        if (!file_exists(path)) {
            return error("file not found: " + path);
        }

        { ... }  // forbidden expression
    }

    result create_dir(string& path) {
        if (dir_exists(path)) {
            return error("dir already exists: " + path);
        }

        { ... }  // forbidden expression
    }

    result create_file(string& path) {
        if (file_exists(path)) {
            return error("file already exists: " + path);
        }

        switch (open(path, mode.append)) {
            case (ok as f) {
                f.close();
                return ok;
            }

            default {
                return error("failed to create file: " + path);
            }
        }
    }

    result delete_dir(string& path, bool recursive = false) {
        if (!dir_exists(path)) {
            return error("dir not found: " + path);
        }

        { ... }  // forbidden expression
    }

    result delete_file(string& path) {
        if (!file_exists(path)) {
            return error("file not found: " + path);
        }

        { ... }  // forbidden expression
    }

    bool   dir_exists(string& path)   { ... }  // forbidden expression
    bool   exists(string& path)       { ... }  // forbidden expression
    bool   file_exists(string& path)  { ... }  // forbidden expression
    string input(string& prompt = "") { ... }  // forbidden expression

    result<array<string>> index_dir(string& path) {
        if (!dir_exists(path)) {
            return error("dir not found: " + path);
        }

        { ... }  // forbidden expression
    }

    result move_dir(string& path, string& target) {
        if (!dir_exists(path)) {
            return error("dir not found: " + path);
        }

        { ... }  // forbidden expression
    }

    result move_file(string& path, string& target) {
        if (!file_exists(path)) {
            return error("file not found: " + path);
        }

        { ... }  // forbidden expression
    }

    result<file> open(string& path, i64 mode = mode.read) {
        if (mode & mode.read and !file_exists(path)) {
            return error("file not found: " + path);
        }

        { ... }  // forbidden expression
    }

    void print(type& t) {
        return t as string;
    }

    void printf(string& format, type& t) { ... }  // forbidden expression

    result<string> read(string& path) {
        with (open(path)?) as f {
            return f.read();
        }
    }

    void set_clipboard(string& text) { ... }  // forbidden expression

    result<dir> walk(string& path) {
        if (!dir_exists(path)) {
            return error("dir not found: " + path);
        }

        { ... }  // forbidden expression
    }
}
