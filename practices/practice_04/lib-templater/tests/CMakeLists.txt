include(FetchContent)

FetchContent_Declare(
    googletest
    GIT_REPOSITORY https://github.com/google/googletest.git
    GIT_TAG v1.15.2
)

set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)

FetchContent_MakeAvailable(googletest)

add_executable(__PROJECT_NAME_TESTS__
    test_foo.cpp
)

target_link_libraries(__PROJECT_NAME_TESTS__
    PRIVATE
        __PROJECT_NAME__::__PROJECT_NAME__
        GTest::gtest_main
)

include(GoogleTest)
gtest_discover_tests(__PROJECT_NAME_TESTS__)
