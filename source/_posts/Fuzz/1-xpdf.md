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

### 简单测试

创建工作目录

```
mkdir fuzzing_xpdf && cd fuzzing_xpdf/
```

配置测试目标

```shell
wget https://dl.xpdfreader.com/old/xpdf-3.02.tar.gz
tar -xvzf xpdf-3.02.tar.gz
./configure --prefix="<fuzzing_xpdf绝对路径>/install/"
make -j7	# 或者别的数字
make install
```

创建测试文件目录

```shell
mkdir pdf_examples && cd pdf_examples
# 下载测试文件
wget https://github.com/mozilla/pdf.js-sample-files/raw/master/helloworld.pdf
wget http://www.africau.edu/images/default/sample.pdf
wget https://www.melbpc.org.au/wp-content/uploads/2017/10/small-example-pdf-file.pdf
```

简单测试

```shell
# fuzzing_xpdf 目录下
./install/bin/pdfinfo -box -meta ./pdf_examples/helloworld.pdf
```

输出如下：

```shell
Tagged:         no
Pages:          1
Encrypted:      no
Page size:      200 x 200 pts
MediaBox:           0.00     0.00   200.00   200.00
CropBox:            0.00     0.00   200.00   200.00
BleedBox:           0.00     0.00   200.00   200.00
TrimBox:            0.00     0.00   200.00   200.00
ArtBox:             0.00     0.00   200.00   200.00
File size:      678 bytes
Optimized:      no
PDF version:    1.7
```

### 源码Fuzz

重新编译

```shell
# 清除残留
rm -r $HOME/fuzzing_xpdf/install
cd $HOME/fuzzing_xpdf/xpdf-3.02/
make clean
# 重新配置
CC=afl-clang CXX=afl-clang++ ./configure --prefix="/mnt/d/Users/czx/NativeFiles/Desktop/blog/code/Fuzz/fuzzing_xpdf/install/"
# afl编译
make -j7
make install
```

源码fuzz

```shell
# 设置随机数种子
export AFL_RANDOM=123
afl-fuzz -i ./pdf_examples/ -o ./out/ -- ./install/bin/pdftotext @@ ./output
```

