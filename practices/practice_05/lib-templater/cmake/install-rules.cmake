include(GNUInstallDirs)
include(CMakePackageConfigHelpers)

install(
    TARGETS __PROJECT_NAME__
    EXPORT __PROJECT_NAME__Targets
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
)

install(
    DIRECTORY ${PROJECT_SOURCE_DIR}/include/
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)

install(
    EXPORT __PROJECT_NAME__Targets
    NAMESPACE __PROJECT_NAME__::
    FILE __PROJECT_NAME__Targets.cmake
    DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/__PROJECT_NAME__
)

write_basic_package_version_file(
    "${CMAKE_CURRENT_BINARY_DIR}/__PROJECT_NAME__ConfigVersion.cmake"
    VERSION ${PROJECT_VERSION}
    COMPATIBILITY SameMajorVersion
)

configure_package_config_file(
    "${PROJECT_SOURCE_DIR}/cmake/__PROJECT_NAME__Config.cmake.in"
    "${CMAKE_CURRENT_BINARY_DIR}/__PROJECT_NAME__Config.cmake"
    INSTALL_DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/__PROJECT_NAME__
)

install(
    FILES
        "${CMAKE_CURRENT_BINARY_DIR}/__PROJECT_NAME__Config.cmake"
        "${CMAKE_CURRENT_BINARY_DIR}/__PROJECT_NAME__ConfigVersion.cmake"
    DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/__PROJECT_NAME__
)