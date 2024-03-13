# Function Design

This is nebula-ng's function design document. It describes concept and design choice to achieve two main goals of
function layer.

- **Flexible**: Based on Function Framework using c++ template and metaprogramming, a simple function interface is
  possible, make it easy to add new function implementation into the function system.

- **Efficiency**: An ExecFunction interface is defined, which wrapped underling kernel function implementations, it
  employs following technologies to make the execution efficient.
    - **Auto/Manual Vectorization**: enabling tight loop and cache-friendly computing
    - **Function Traits**: using template expansion of metaprogramming.

> NOTE: Main idea of this design is inspired by velox, simplified some routines which are not need currently.
> - https://facebookincubator.github.io/velox/develop/scalar-functions.html
> - https://velox-lib.io/blog/simple-functions-1/

## How to add a function

This section introduced a general function interface, with this interface, developer of function (who add new functions)
can easily implement and register a function into the system, without concerning too much about underling vectorization
and batching. From this perspective, we achieve the goal of `Flexible`.

### `function traits`

A function implementation, can define one or more multiple `callxxx` to declare its behavior at compile time.

| function traits               | Input                                                                                | Output                            |
|-------------------------------|--------------------------------------------------------------------------------------|-----------------------------------|
| udf_has_call_return_bool      | Reference, only accept not-null input                                                | bool (return false indicate null) |
| udf_has_call_return_void      | Reference, only accept not-null input                                                | void (always return not-null)     |
| udf_has_callAscii_return_bool | Input is reference, and content of the input are is all within Ascii codepoint range | bool (return false indicate null) |
| udf_has_callAscii_return_void | Input is reference, and content of the input are is all within Ascii codepoint range | void (always return not-null)     |

> **default null behavior**: a null value in any of the arguments produces a null result.

#### Why need these function traits ?

At compile time, with function traits got, framework can generate vectorized version of each `callxxx` at compile time.
At runtime, data(row batch) that need to be processed will be checked to see if that bach has any potential to invoke
any faster version of `callxxx`;

#### Examples

- call()
    - function define call, indicate it only handle not null input, null input should be handled by framework, and
      produce null result without invoke any `callXXX`. It is `default null behavior`;
    - e.g. PlusFunction for floating pointer numbers;

  ```c++
  template <typename T>
  struct PlusFunction {
      template <typename TInput>
      void call(TInput& result, const TInput& a, const TInput& b) {
          result = a + b;
      }
  };
  ```

- callAscii()
    - General string function need handle unicode strings (use utf8proc to handle unicode encoding), when input string
      is ascii encoded only, a fast path can be defined to compute for only ascii string input;

  ```c++
  template <typename T>
  struct Substring {
      // ASCII input always produces ASCII result.
      static constexpr bool is_default_ascii_behavior = true;
  
      template <typename I>
      bool call(String& result,
                                    const String& input,
                                    I start,
                                    I length = std::numeric_limits<I>::max()) {
          // should handle all conditions
      }
  
      template <typename I>
      bool callAscii(String& result,
                                         const String& input,
                                         I start,
                                         I length = std::numeric_limits<I>::max()) {
          // can assume input is ascii, use input.substr(...), much faster
      }
  ```

> `callNullable()` and `callNullFree()` is used in very rare case, only support them when needed in the future.

## Function Framework

Functions following the previous defined principle will to be executed at runtime. While these function have no runtime
polymorphism like virtual functions calls (virtual function call in row level can hurt cpu cache which should be
avoided).

Function framework is introduced to tackle this problem. As the underling execution framework, it gets traits from those
registered functions, wraps and inlines them in for loop. Combine with runtime knowledge of data to process, it can
dispatch to different `callxxx`. With bach processing and optimization from compiler, e.g. loop unrolling, loop
vectorize, achieve the goal of `Efficiency`

### UDFHolder

Internally, function is Wrapped in an UDFHolder. An UDFHolder extracts the defined function's traits using template
expansion. With knowledge of these `function traits`, the framework specialize each function with an UDFHolder.

### Function Registry

All predefined functions are registered with as built-in functions into the global function register.
`Function signature` is the key to register (system startup) and resolve (find function to execute in a specific query).
function signature is constructed with information got from function metadata.

`function metadata` store information used during registration, resolving and execution, those metadata includes:

- Function name
- ArgTypes(InputTypes)
- ReturnType(OutputType)
- isDeterministic
- isDefaultNullBehavior
- isAscii
- etc

> NOTE: UDFHolder inherit FunctionMetadata.

### ExecFunction

ExecFunction is the top public interface of the function architecture. It exposes necessary information to the
user of function (mostly expression), like: isDeterministic, isDefaultNullBehavior, isAscii.

The most important interface is the apply function, define how data to passed in and returned.

- A SelectionVector is used as a row filter to specify which rows to process.
- Input/Output are represent in Vector class, Vector should support access each field by row index;
  > NOTE: Function layer do not assume memory layout of the input/output Vector, it uses c++ operator[] to retrieve
  data, while the efficiency of this retrieval should have great influence on cache locality. 

```c++
    virtual void apply(EvalCtx& context,
                       const SelectionVector& rows,
                       std::vector<VectorPtr>& inputs,
                       VectorPtr& result) const = 0;
```

Currently, ExecFunction is defined as pure virtual interface. This virtual function call slowness is amortized by rows
in that batch. FuncExecAdaptor is the real implementation that connect the ExecFunction interface to the underling
components.

> Why don't we make ExecFunction as a concrete class?
>
> This is because, with this simple row-based function interface and function framework, we can implement most of normal
> functions. While there are exceptions may exist. For instance, if a function need read data cross multiple rows, or
> even
> the whole batch, currently function interface paradigm is not enough. For those functions, they need inherit
> ExecFunction
> themselves, and implement their special purpose logic (just for future design possibility).
