IF(NOT DAS_GEN_FOR_EACH_FOUND)
    SET(DAS_GEN_FOR_EACH_FOUND TRUE)

    find_package(Python3)

    SET(DAS_GEN_FOR_EACH_DIR ${PROJECT_SOURCE_DIR}/modules/dasGenForEach)
    SET(DAS_GEN_FOR_EACH_PY_DIR ${DAS_GEN_FOR_EACH_DIR}/python_modules/das_gen_for_each)

    SET(DAS_GEN_FOR_EACH_SRC
        ${DAS_GEN_FOR_EACH_PY_DIR}/__init__.py
        ${DAS_GEN_FOR_EACH_PY_DIR}/gen_for_each.py
        ${DAS_GEN_FOR_EACH_PY_DIR}/main.py
    )

    include(${DAS_GEN_FOR_EACH_DIR}/dasShared/CMakeLists.txt)
    GET_DAS_SHARED_PY_SRC(DAS_GEN_FOR_EACH_SHARED_SRC ${DAS_GEN_FOR_EACH_DIR}/dasShared)

    MACRO(DAS_GEN_FOR_EACH write_to max_args)
        IF(NOT Python3_FOUND)
            MESSAGE(STATUS "Prerequisites for dasGenForEach not found. Pre-generated files will be used.")
        ELSE()
            ADD_CUSTOM_COMMAND(
                DEPENDS ${DAS_GEN_FOR_EACH_SRC} ${DAS_GEN_FOR_EACH_SHARED_SRC}
                OUTPUT ${CMAKE_SOURCE_DIR}/${write_to}
                WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
                VERBATIM
                COMMAND ${Python3_EXECUTABLE} -B ${DAS_GEN_FOR_EACH_PY_DIR}/main.py
                    --write_to ${write_to}
                    --max_args ${max_args}
                COMMENT "Writing generated DAS_FOR_EACH macros to ${write_to}"
            )
        ENDIF()
    ENDMACRO()
ENDIF()
