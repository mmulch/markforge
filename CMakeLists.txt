cmake_minimum_required(VERSION 3.16)

project(MarkdownEditor
    VERSION 1.0.0
    DESCRIPTION "PyQt6-based Markdown editor with live preview"
    LANGUAGES NONE
)

# ── Python ────────────────────────────────────────────────────────────────────
find_package(Python3 REQUIRED COMPONENTS Interpreter)

message(STATUS "Python found: ${Python3_EXECUTABLE}  (${Python3_VERSION})")

if(Python3_VERSION VERSION_LESS "3.8")
    message(FATAL_ERROR
        "Python 3.8 or newer required (found: ${Python3_VERSION})")
endif()

# ── Virtual Environment ───────────────────────────────────────────────────────
set(VENV_DIR "${CMAKE_BINARY_DIR}/venv")
set(VENV_PYTHON "${VENV_DIR}/bin/python3")
set(VENV_PIP    "${VENV_DIR}/bin/pip")

message(STATUS "Virtual environment: ${VENV_DIR}")

# ── Source files ──────────────────────────────────────────────────────────────
set(PYTHON_SOURCES
    src/main.py
    src/mainwindow.py
    src/editor_widget.py
    src/highlighter.py
    src/preview_widget.py
)

# ── Targets ───────────────────────────────────────────────────────────────────

# Create virtual environment and install dependencies
add_custom_target(install_deps
    COMMAND ${Python3_EXECUTABLE} -m venv "${VENV_DIR}"
    COMMAND ${VENV_PIP} install --upgrade pip
    COMMAND ${VENV_PIP} install -r "${CMAKE_SOURCE_DIR}/requirements.txt"
    WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}"
    COMMENT "Creating venv and installing Python dependencies ..."
    VERBATIM
)

# Launch the application via the venv
add_custom_target(run
    COMMAND ${VENV_PYTHON} "${CMAKE_SOURCE_DIR}/src/main.py"
    WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}/src"
    COMMENT "Starting Markdown editor ..."
    VERBATIM
)

# Generate launcher script
configure_file(
    "${CMAKE_SOURCE_DIR}/cmake/launcher.sh.in"
    "${CMAKE_BINARY_DIR}/markdown-editor"
    @ONLY
)

# ── Installation ──────────────────────────────────────────────────────────────
if(NOT CMAKE_INSTALL_LIBDIR)
    set(CMAKE_INSTALL_LIBDIR "lib")
endif()
include(GNUInstallDirs)

install(
    FILES ${PYTHON_SOURCES}
    DESTINATION "${CMAKE_INSTALL_LIBDIR}/markdown-editor"
)

install(
    FILES requirements.txt
    DESTINATION "${CMAKE_INSTALL_LIBDIR}/markdown-editor"
)

install(
    PROGRAMS "${CMAKE_BINARY_DIR}/markdown-editor"
    DESTINATION "${CMAKE_INSTALL_BINDIR}"
)
