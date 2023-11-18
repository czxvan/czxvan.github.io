---
title: xpdf
date: 2023-11-13 20:55:41
tags:
categiries: Fuzz
---

Fuzz实验1——xpdf

参考资料：

- [Fuzzing101/Exercise 1 at main · antonio-morales/Fuzzing101 (github.com)](https://github.com/antonio-morales/Fuzzing101/tree/main/Exercise 1)
- [AFL++ (PlusPlus) 介绍与实践 - WelkinChan - 博客园 (cnblogs.com)](https://www.cnblogs.com/welkinchan/p/15930226.html#一afl简介)

<!-- more -->

## 环境准备

创建工作目录

```
mkdir fuzzing_xpdf && cd fuzzing_xpdf/
```

创建测试文件目录

```shell
mkdir pdf_examples && cd pdf_examples
# 下载测试文件
wget https://github.com/mozilla/pdf.js-sample-files/raw/master/helloworld.pdf
wget http://www.africau.edu/images/default/sample.pdf
wget https://www.melbpc.org.au/wp-content/uploads/2017/10/small-example-pdf-file.pdf
```

源码插桩编译

```shell
# 配置
CC=afl-clang-fast CXX=afl-clang-fast++ ./configure --prefix="/mnt/d/Users/czxvan/Desktop/fuzz/fuzzing_xpdf/install/"
# afl编译
make -j7
make install
```

源码fuzz

```shell
# -s 设置随机数种子
afl-fuzz -i ./pdf_examples/ -o ./out/ -s 123 -- ./install/bin/pdftotext @@ ./output
```

