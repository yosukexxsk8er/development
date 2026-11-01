#include <stdio.h>

// __declspec(dllexport) を定義する
#define EXPORT __attribute__((visibility("default")))

// 足し算を行う関数
EXPORT int add(int a, int b) {
    return a + b;
}

// メッセージを出力する関数
EXPORT void print_message(const char* message) {
    printf("Message from DLL: %s\n", message);
}
