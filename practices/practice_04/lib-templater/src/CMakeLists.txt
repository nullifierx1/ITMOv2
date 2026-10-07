# Needs to be supplemented with other files
add_library(__PROJECT_NAME__
    foo.cpp
)

target_include_directories(__PROJECT_NAME__
    PUBLIC
        $<BUILD_INTERFACE:${PROJECT_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:include>
)

# C++20 standart
target_compile_features(__PROJECT_NAME__ PUBLIC cxx_std_20)

# Warnings
if (MSVC)
    target_compile_options(__PROJECT_NAME__ PRIVATE /W4 /permissive-)
else()
    target_compile_options(__PROJECT_NAME__ PRIVATE -Wall -Wextra -Wpedantic)
endif()

# Alias
add_library(__PROJECT_NAME__::__PROJECT_NAME__ ALIAS __PROJECT_NAME__)