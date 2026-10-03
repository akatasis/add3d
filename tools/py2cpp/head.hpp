// 46_castle.cpp -- the castle, in C++ (see 46_castle.py)
#include <algorithm>
#include <array>
#include <cctype>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <functional>
#include <initializer_list>
#include <iostream>
#include <limits>
#include <map>
#include <memory>
#include <numeric>
#include <optional>
#include <random>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <tuple>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>
#include <charconv>
#include <cfenv>
#include <chrono>
#include <system_error>
#include <filesystem>
#include <iterator>
#include <cerrno>
#include <iomanip>
#include <locale>
#include <codecvt>
// Built with -fno-exceptions (see above), add.hpp's few try / catch / throw -- for files
// it cannot read, which the castle never asks of it -- become plain code, and a throw
// stops the program with a message (the headers it uses are all included above, first).
#if !defined(__cpp_exceptions) && !defined(__EXCEPTIONS)
namespace castle_noexc {                    // (what a throw does here: says so and stops)
[[noreturn]] inline bool fail() {
    std::fputs("46_castle: add.hpp failed (an error it would throw)\n", stderr);
    std::abort();
}
}  // namespace castle_noexc
#define try if (true)
#define catch(...) if (false)
#define throw while (::castle_noexc::fail())
#endif
#include "add.hpp"
#if !defined(__cpp_exceptions) && !defined(__EXCEPTIONS)
#undef try
#undef catch
#undef throw
#endif
#include "castle_rt.hpp"
