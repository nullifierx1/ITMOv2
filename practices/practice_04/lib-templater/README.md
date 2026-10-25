# C++ Library Template

Modern C++ library template with:

- CMake (install + `find_package` support)
- Unit tests (GoogleTest + CTest)
- Optional `bin/` target for quick testing
- CI (GitHub Actions)
- Code style configuration (`.clang-format`, `.editorconfig`)
- Bootstrap script for instant project setup

---

## 🚀 Quick start

```bash
python tools/bootstrap.py project_name
````

This will:

* rename project (`mylib` → `project_name`)
* update namespace
* configure code style
* optionally remove `bin/`
* prepare project structure

---

## 📁 Project structure

```txt
├─ include/project_name/   # Public API
├─ src/               # Library implementation
├─ bin/               # Executable (optional, for local testing)
├─ tests/             # Unit tests
├─ cmake/             # CMake modules (install, dependencies)
├─ tools/             # Bootstrap script
└─ CMakeLists.txt
```

---

## 🔧 Build

Requirements:

```txt
- CMake ≥ 3.20
- C++ compiler (C++20+)
```

```bash
cmake -S . -B build
cmake --build build
```

---

## ▶️ Run binary

```bash
./build/bin/main
```

(Windows: `build/bin/main`)

---

## 🧪 Run tests

```bash
ctest --test-dir build --output-on-failure
```

---

## 📦 Install

```bash
cmake --install build --prefix /usr/local
```

---

## 🔗 Use as dependency

```cmake
find_package(project_name CONFIG REQUIRED)

add_executable(app main.cpp)
target_link_libraries(app PRIVATE project_name::project_name)
```

---

## ⚙️ Configuration options

```cmake
BUILD_TESTS     # ON/OFF
BUILD_BIN       # ON/OFF
ENABLE_INSTALL  # ON/OFF
```

---

## 🧠 Notes

* `bin/` is intended for quick local testing (not examples)
* Tests use `FetchContent` (no external setup required)
* Install rules generate a proper CMake package

---

## 🛠 Development

To preview changes without modifying files:

```bash
python tools/bootstrap.py project_name --dry-run
```