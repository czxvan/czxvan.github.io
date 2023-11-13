---
title: AFL
date: 2023-11-08 14:04:34
tags:
categories: Fuzz
---

AFL和Fuzz学习笔记。

参考链接：

- https://blingblingxuanxuan.github.io/2020/06/30/afl/
- [liyansong2018/fuzzing-tutorial: Curated list of classic fuzzing books, papers about fuzzing at information security top conferences over the years, commonly used fuzzing tools, and resources that can help us use fuzzer easily. (github.com)](https://github.com/liyansong2018/fuzzing-tutorial)
- [antonio-morales/Fuzzing101: An step by step fuzzing tutorial. A GitHub Security Lab initiative](https://github.com/antonio-morales/Fuzzing101)
- [CS研究生如何入门模糊测试方向？ - 知乎 (zhihu.com)](https://www.zhihu.com/question/388240608)

<!-- more -->

## 安装

安装clang和llvm

```shell
sudo apt-get install clang
sudo apt-get install llvm
```

下载并安装AFL

```shell
wget http://lcamtuf.coredump.cx/afl/releases/afl-latest.tgz
tar -xzvf afl-2.52b.tgz
cd afl-2.52b
make
sudo make install
```

支持无源码Fuzz

```shell
# 在afl目录下
cd qemu_mode
./build_qemu_support.sh
cd ..
make install 
```



### 常用命令

```shell
# 编译插桩
afl-gcc test.c -g -o test
# fuzz，指定输入和输出文件夹
afl-fuzz -i testcase/ -o output/ ./test
# 继续已停止的fuzz测试
afl-fuzz -i- -o output ./test
# 文件fuzz
# 有源码插桩
afl-fuzz -i in/ -o out/ ./readelf -a @@
# 无源码fuzz -Q 慢
afl-fuzz -i in/ -o out/ -Q ./readelf -a @@
```

```shell
# 分析crash结果
```

