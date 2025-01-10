# &#127874; cake &#127874;

cake is a statically-typed, garbage-collected programming language that is designed to be fast and easy to use. The name "cake" and its components are always lowercase. The language is still in very early development - there is currently no support for classes, language interoperability, and many other features. *If you haven't made your own language, can you really call yourself a programmer?*

## Classes
A class is a struct that lets you define methods to act on its variables. All classes implicitly inherit from the `base` type. This allows for polymorphism by expecting a `base` type and being able to use any class.
```cpp
class MyClass {
    int i;
    str name;

    MyClass() {}   // default constructor
    ~MyClass() {}  // default destructor

    void print() {
        std::print(name);
    }
}
```

### Casting
If two classes share inheritance, one may be casted into the type of the other. You must do so if a target is expecting another type - there are no implicit casts.
```cpp
MyClass m;
base n = cast<base>(m);
```

### Inheritance
Classes may inherit from structs, but only classes may inherit from classes.
```cpp
class AnotherClass : MyClass {
    override void print() {
        std::print("bye loser");
    }
}

struct MyStruct {
    str type;
}

class YetAnother : AnotherClass, MyStruct {}  // multiple inheritance
```

### Operator Overloads


## Compilation
cake is a transpiled language. This means that cake code (`.cake`) is first converted into C code (`.cake.c`), which is then compiled into an executable using [GCC](https://gcc.gnu.org/). This is done to ease development of the language and to maintain cross-platform support. The cake compiler is called "bake." *Get it? You bake a cake? I'm very funny, I know.*

Download the [bake installer]() to start baking some delicious, wonderful, even extraordinary cake!

## Conventions
cake has several style conventions. As with any other language, these are optional.
```cpp
// aligned columns when reasonable
int       myNumber;         // camelCase variables
class     MyClass {}        // PascalCase classes
enum      MyEnum {}         // PascalCase enums
void      my_function() {}  // snake_case functions
namespace MyNamespace {}    // PascalCase namespaces
struct    MyStruct {}       // PascalCase structs

int i = 2**3;   // no spaces around exponentiation
i++;            // no spaces around incrementation/decrementation
int j = 2 + 3;  // spaces around all other operators

void another_function() {  // same-line opens
    return null;           // indent 4 spaces
}
```

## Functions
By default, function parameters in cake are passed by value. To override this and pass by reference instead, prepend a parameter with `&`.
```cpp
str s = "hello";
std::print(s);   // value
std::print(&s);  // reference
```

## Ignored Symbols
bake will ignore certain bits of code including empty lines and whitespace.
```cpp
#directives from C/C++
// comments on their own line
int i;  // comments beside code
```

## Literals
Literal values in cake have some rules.
```cpp
bool  b = true;         // booleans are true or false

float f = 1.0;          // floats have at least a unit digit, a decimal, and a tenths digit
float g = 5.2e3;        // scientific notation (5.2 * 10**3 or 5200.0)
float h = 1'234.567'8;  // single quotes can be used as separators

int   i = 3;            // integers are just digits
int   j = 2e71;         // scientific notation (2 * 10**71 or really big)
int   k = 1'234;        // single quotes can be used as separators

ptr   p = null;         // pointers can be null or hold a memory address as an int8

str   s = "<3";         // strings are in "double quotes"

void  v = null;         // void can only be null
```

## Logical Binary Operators
cake supports the following operations on `bool` types which can each be written one of two ways:
- `and` / `&&`
- `nand` / `!&`
- `or` / `||`
- `nor` / `!|`
- `xor` / `^^`
- `nox` / `!^`
```cpp
bool a = false;
bool b = true;

a and  b;  // false (not all are true)
a nand b;  // true
a or   b;  // true  (at least one is true)
a nor  b;  // false
a xor  b;  // true  (values are different)
a nox  b;  // false
```

## Modifiers
Variables can be customized with modifiers before the type name. Modifiers must be alphabetized when using multiple.
```cpp
const        int   i = 16;      // cannot be modified
static       int   j = 123456;  // static integer (3 bytes) with dynamic assignment
const static float f = 3.14;    // constant static float (? bytes) with dynamic assignment
static       str   s = "ono"    // static string (3 bytes) with dynamic assignment

class Example : Something {
    final    void this_is_it() {}         // mark method unable to be overriden
    override void existing_function() {}  // override a parent class' method
}
```

## Namespaces
A namespace is a nice way to further organize your code. Everything inside acts as a global, but needs the namespace prefix to access from the outside.
```cpp
namespace MyNamespace {
    int i;
    void foo() {}
}

std::print(MyNamespace::i);
MyNamespace::foo();
```

## Project Structure
Every cake project has 2 main elements: a project file and source code. *You can have more, of course. Don't limit yourself!*

The project file is named `cake.json`. Only the "name" field is required - all others are optional. The "type" field must be either "active" (generates executable) or "library".
```json
{
    "name": "cake_example",
    "type": "active",
    "author": "your_name",
    "version": "1.0.0"
}
```

bake will look for any `.cake` files in the same folder (and any subfolders) as this project file. Source code can be in any `.cake` file. This means you are free to organize your global code blocks in whichever way you desire. *The order of the ingredients doesn't really matter as long as they're all mixed in the end, right?*

There is one exception to this rule: the entry point. For any cake project, you must include this function in `main.cake`:
```cpp
void main() {
    // all code execution stems from here

    // void functions automatically return null on success - this is optional
    // return anything else for a failure
    return null;
}
```

## Reserved Keywords
cake has a number of reserved keywords that serve a special purpose so they cannot be used for variables, functions, etc.\
`and`, `arr`, `base`, `bool`, `cast`, `class`, `const`, `dec`, `decN` (any digits for `N`), `dict`, `enum`, `final`, `float`, `int`, `intN` (any digits for `N`), `namespace`, `nand`, `nor`, `not`, `nox`, `null`, `or`, `override`, `ptr`, `return`, `static`, `str`, `strN` (any digits for `N`), `struct`, `super`, `void`, `with`, `xor`

## Structs
A struct lets you keep variables of different types together. Structs may be inherited by classes or other structs.
```cpp
struct MyStruct {
    int i;
    str name;
}
```

## Sugar
cake has a lot of [syntactic sugar](https://en.wikipedia.org/wiki/Syntactic_sugar) to make your life as a developer easier. Functions and methods use a `$` symbol to indicate they also have a sugar method. *Get it? Sugar in cake?*
```cpp
int i = 0;

// incrementing an integer
i.$assign(i + 1);
i.$add(1);  // $sub, $mult, $div, $exp, $mod
i = i + 1;
i += 1;      // supports +, -, *, /, **, %
i++;         // supports +, -

// creating an array
arr<int> a = arr<int>(1, 2, 3);
int[]    b = int[1, 2, 3];

// accessing an array
int j = a.$get(0);  // index
int k = a[0];

// adding to an array
a.$add(4);
a += 4;

// creating a dictionary
dict<str> d = dict<str>("a": "hello", "b": "world");
str{}     e = str{"a": "hello", "b": "world"};

// accessing a dictionary
str s = d.$get("hello");
str t = d["hello"];

// adding to a dictionary
d.$add("very": "happy");
d["very"] = "happy";

// casting an object
base n = cast<base>(m);
base o = (base)m;
```

## Syntax
cake has a syntax very similar to C++. Lines must be terminated with semicolons, blocks are defined with curly braces,

## Types

### Primitive
cake has 8 primitive types. These always have a value, so if they are not given one at assignment, it will be their default value.
```cpp
base  b = null;   // base class from which everything inherits, default null
bool  c = false;  // boolean,                                   default false
dec   d = 2.23d;  // signed floating point base 10 number,      default 0.0d
float f = 2.236;  // signed floating point base 2 number,       default 0.0
int   i = 7;      // signed integer,                            default 0
ptr   p = null;   // pointer to memory,                         default null
str   s = "hi";   // string of ASCII characters,                default ""
void  v = null;   // returned by void functions,                default null
```

### Container
cake has 2 types for storing multiple like values together.
```cpp
arr<T>  a = arr<T>();   // arrays hold multiple elements of type T
dict<T> d = dict<T>();  // dictionaries hold key (str) - value (T) pairs
```

## Type Width
Integers and strings may be of a fixed byte width (static) or an arbitrary one (dynamic). If you don't specify a number of bytes, they will automatically resize to fit the value. Dynamic types are much less efficient than static ones because of this automatic sizing.
```cpp
int i = 0;          // dynamic integer, currently 1 byte wide (-128 - 127)
i = i + 128;        // grows to 2 bytes (-256 - 255)
i = i - 1;          // shrinks back to 1 byte

int j = 2**31 - 1;  // 4 bytes wide (-2.1B - 2.1B)
j = j + 1;          // grows to 5 bytes (-549B - 549B)

int k = 1e100;      // 334 bytes wide

int1 l = 127;       // static integer, 1 byte wide
l = l + 1;          // overflows to -128

int4 m = 1e41;      // overflows many times until it fits in 4 bytes

str  s = "hello";   // dynamic string, currently 5 bytes wide
str6 t = "world!";  // static string, 6 bytes wide
str2 u = "</3";     // only stores characters up to the specified size ("</")
```

Floating point numbers are slightly different.
```cpp
dec d = 1.0d;  //
d =

float f = 1.0;  // dynamic float, currently 4 bytes wide
f =
```

Pointers are also different. They are always static and are as many bytes wide as your CPU architecture supports.
```cpp
ptr p;  // for nearly everyone, this will be 8 bytes wide
```

\
&copy; 2025 Ezio416
