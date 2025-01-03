# &#127874; cake &#127874;

cake is a programming language designed to be fast and easy to use. The name "cake" and its components are always lowercase. The language is still in very early development - there is currently no support for imports/includes, classes, enums, C/C++ interoperability, and many other features. *If you haven't made your own language, can you really call yourself a programmer?*

## Compilation
cake is a transpiled language. This means that cake code (`.cake`) is first converted into C code (`.cake.c`), which is then compiled into an executable with [GCC](https://gcc.gnu.org/). This is done to ease development of the language and to maintain cross-platform support. The cake compiler is called "bake." *Get it? You bake a cake? I'm very funny, I know.*

## Project Structure
Every cake project has 2 main elements: a project file and source code. *You can have more, of course. Don't limit yourself!*

The project file is named `cake.json`. Only the "name" field is required, all others are optional.
```json
{
    "name": "cake_example",
    "author": "your_name",
    "version": "1.0.0"
}
```

bake will look for any `.cake` files in the same folder (and any subfolders) as this project file. Source code can be in any `.cake` file. This means you are free to organize your global code blocks in whichever way you desire. *The order of the ingredients doesn't really matter as long as they're all mixed in the end, right?*

There is one exception to this rule: the entry point. For any cake project, you must include this in `main.cake`:
```c++
void main() {
    // all code execution stems from here

    // void functions automatically return null on success - this is optional
    // return anything else for a failure
    return null;
}
```

## Conventions
cake has several style conventions. As with any other language, these are optional.
```c++
int    myNumber;         // camelCase variables
class  MyClass {}        // PascalCase classes
enum   MyEnum {}         // PascalCase enums
void   my_function() {}  // snake_case functions
struct MyStruct {}       // PascalCase structs
```

## Types

### Primitive
cake has 5 types for storing a single value in a variable. Primitives always have a value, so if they are not given one at assignment, it will be their default value.
```c++
bool  b = false;  // boolean,                    default false
float f = 2.236;  // floating point real number, default 0.0
int   i = 7;      // signed integer,             default 0
str   s = "hi";   // string of ASCII characters, default ""
void  v = null;   // returned by void functions, default null
```

### Container
cake has 2 types for storing multiple values in a variable.
```c++
arr<T>  a = arr<T>();   // arrays hold multiple elements of type T
dict<T> d = dict<T>();  // dictionaries hold key (str) - value (T) pairs
```

## Literals
Literal values in cake have some rules.
```c++
bool  b = true;         // booleans are true or false

float f = 1.0;          // floats have at least a unit digit, a decimal, and a tenths digit
float g = 5.2e3;        // engineering notation (5.2 * 10^3 or 5200.0)
float h = 1'234.567'8;  // single quotes can be used as separators

int   i = 3;            // integers are just digits
int   j = 2e71;         // engineering notation (2 * 10^71 or really big)
int   k = 1'234;        // single quotes can be used as separators

str   s = "<3";         // strings are in "double quotes"

void  v = null;         // void can only be null
```

## Type Width
Integers and strings in cake may be of a fixed byte width (explicit) or a dynamic one (arbitrary). If you don't specify a number of bytes, they will resize to fit the value. Arbitrary types are much less efficient than explicit ones because of this dynamic sizing.
```c++
int i = 0;          // arbitrary integer, currently 1 byte wide (-128 - 127)
i = i + 128;        // grows to 2 bytes (-256 - 255)
i = i - 1;          // shrinks back to 1 byte

int j = 2^31 - 1;   // 4 bytes wide (-2.1B - 2.1B)
j = j + 1;          // grows to 5 bytes (-549B - 549B)

int k = 1e100;      // 334 bytes wide

int1 l = 127;       // explicit integer, 1 byte wide
l = l + 1;          // overflows to -128

int4 m = 1e41;      // overflows many times until it fits in 4 bytes

str  s = "hello";   // arbitrary string, currently 5 bytes wide
str6 t = "world!";  // explicit string, 6 bytes wide
str1 u = "hi";      // only stores characters up to the specified size ("h")
```

Floating point numbers are slightly different.
```c++
float f = 1.0;
```

## Modifiers
Variables can be further customized with modifiers before the type name. Modifiers must be alphabetized when using multiple.
```c++
const          int   i = 16;      // cannot be modified
explicit       int   j = 123456;  // explicit integer (3 bytes) with arbitrary assignment
const explicit float f = 3.14;    // explicit float () with arbitrary assignment
```

## Logical Binary Operators
cake supports the following operations on `bool` types which can each be written one of two ways:
- `and` / `&&`
- `nand` / `!&`
- `or` / `||`
- `nor` / `!|`
- `xor` / `^^`
- `nox` / `!^`
```c++
bool a = false;
bool b = true;

a and  b;  // false (not all are true)
a nand b;  // true
a or   b;  // true  (at least one is true)
a nor  b;  // false
a xor  b;  // true  (values are different)
a nox  b;  // false
```

## Classes
A class is a way to keep variables of different types together, define methods to act on these variables, and serve as a basis for inheritance. Default constructors/destructors exist, but will do nothing if you don't define them yourself.
```c++
class MyClass {
    int i;
    str name;

    void print() {
        std::print(name);
    }
}
```

## Functions
By default, function parameters in cake are passed by value. To override this and pass by reference instead, prepend a parameter with `&`.
```c++
str s = "hello";
std::print(s);   // value
std::print(&s);  // reference
```

## Structs
A struct is a way to keep variables of different types together.
```c++
struct MyStruct {
    int i;
    str name;
}
```

## Sugar
cake has a lot of [syntactic sugar](https://en.wikipedia.org/wiki/Syntactic_sugar) to make your life as a developer easier. *Get it? Sugar in cake?*
```c++
int i = 0;

// incrementing an integer
i.OpAssign(i + 1);
i.OpAdd(1);  // OpSub, OpMul, OpExp, OpDiv, OpMod
i = i + 1;
i += 1;      // supports +, -, *, ^, /, %
i++;         // supports +, -

// creating an array
arr<int> a = arr<int>(1, 2, 3);
int[]    b = int[1, 2, 3];

// accessing an array
int j = a.Get(0);  // index
int k = a[0];

// adding to an array
a.Add(4);
a += 4;

// creating a dictionary
dict<str> d = dict<str>("a": "hello", "b": "world");
str{}     e = str{"a": "hello", "b": "world"};

// accessing a dictionary
str s = d.Get("hello");
str t = d["hello"];

// adding to a dictionary
d.Add("very": "happy");
d["very"] = "happy";
```

## Standard Library
Access cake's standard library with the `std::` namespace. The purpose of this is to cut down on the number of reserved keywords cake uses.
```c++
std::error(str s);  // raises an error
std::print(str s);  // prints to the console
```

## Reserved Keywords
cake has a number of reserved keywords that serve a special purpose so they cannot be used for variables, functions, etc.\
`and`, `arr`, `bool`, `class`, `const`, `dict`, `enum`, `explicit`, `float`, `int`, `intN` (any digits for `N`), `nand`, `nor`, `not`, `nox`, `null`, `or`, `return`, `std`, `str`, `strN` (any digits for `N`), `struct`
