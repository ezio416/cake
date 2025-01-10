@echo off
rem c 2025-01-06
rem m 2025-01-06

gcc cake.c -o cake.o -std=gnu23 -c
gcc -o cake cake.o
cake
