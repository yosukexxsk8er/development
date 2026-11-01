cmake_minimum_required(VERSION 3.0)
project(my_project)

# ソースファイルの追加
set(SOURCES
    main.cpp
)

# ヘッダーファイルの追加
set(HEADERS
)

# 実行可能ファイルのビルド
add_executable(my_executable ${SOURCES} ${HEADERS})
