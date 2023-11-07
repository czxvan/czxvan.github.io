---
title: ASLR in Windows
date: 2023-10-22 11:09:00
tags:
categories: Windows-PWN
typora-root-url: ./..\..\pic
---

众所周知，`ASLR`会使得`PE`文件的加载基址随机化，但有时候我们还是能够利用固定的地址，指向`kernel32.dll ntdll.dll`等`dll`文件中的特定指令，这是为什么呢？

参考资料：

- [ntdll 的内存加载位置](https://blog.csdn.net/weixin_43742894/article/details/105879904)

- [Why are certain DLLs required to be at the same base address system-wide? « Nynaeve](http://www.nynaeve.net/?p=198)

<!-- more -->

## 前言

`Windows`和`Linux`下的`ASLR`区别很大。

在`Linux`下，`ASLR`的实现分为两个部分

- 系统部分，根据`/proc/sys/kernel/randomize_va_space`中设置的等级，影响 `栈、库、mmap、堆`（stack .so mmap heap）基址的随机性。
- 编译器部分，由`PIE`选项决定编译得到程序是否是地址无关的，如果是，程序加载基址和全局数据地址（.text .data .bss）就可以随机化。

在`Windwos`下，`ASLR`可由 `Visual Studio` 下的一个链接器选项——随机基址（`/DYNAMICBASE`）控制。

## 开始实验

### ASLR与程序基址的关系

#### 开启ASLR

使用visual studio生成一个可执行程序`Exploime.exe`，开启随机基址

![ASLR open](../pic/ASLR-in-Windows/ASLR-YES.png)

使用windbg加载`Exploime.exe`，然后使用`lm`命令查看已加载模块的基址

![pic1](../pic/ASLR-in-Windows/pic1.png)

重启windbg，重复上面操作

![pic2](../pic/ASLR-in-Windows/pic2.png)

发现，和之前一样。

重启电脑，再来一次，得到

![pic3](../pic/ASLR-in-Windows/pic3.png)

发现各个基址出现变化。

#### 关闭ASLR

关闭随机基址，重新生成`Exploime.exe`

![ASLR open](../pic/ASLR-in-Windows/ASLR-NO.png)

使用windbg加载`Exploime.exe`，然后使用`lm`命令查看已加载模块的基址

![pic4](../pic/ASLR-in-Windows/pic4.png)

重启windbg，重复上面操作

![pic5](../pic/ASLR-in-Windows/pic5.png)

和上面一致，重启电脑，再来一次，得到

![pic6](../pic/ASLR-in-Windows/pic6.png)

发现关闭了`ASLR`的模块（`Exploitme`）基址没有变化，其余默认开启了`ASLR`的系统模块基址发生了变化。

### ASLR与堆栈基址的关系

#### 开启ASLR

开启`ASLR`后，可以看出两次运行堆栈地址的变化：

![address_aslr_1](../pic/ASLR-in-Windows/address_aslr_1.png)

![address_aslr_2](../pic/ASLR-in-Windows/address_aslr_2.png)

#### 关闭ASLR

未开启`ASLR`时，两次运行程序，查看堆栈地址结果如下，完全一致，不过可以看出其他模块的ASLR还是发挥了作用的：

![address1](../pic/ASLR-in-Windows/address1.png)

![address2](../pic/ASLR-in-Windows/address2.png)

### 静态比较

使用`Lord PE`查看开启`ASLR`与不开启`ASLR`程序节的区别，发现前者比后者多一个`.reloc`节，用于存储重定位信息。

![sections_aslr](../pic/ASLR-in-Windows/sections_aslr.png)

![section_noaslr](../pic/ASLR-in-Windows/section_noaslr.png)

## 结论

### ASLR与程序基址之间的关系

Windows（至少Win10）下的`ASLR`机制，对程序基址的影响，只在系统启动时发挥作用，系统运行过程中，各个模块的基址不会变化。

（和我预想中不太一样，本来以为只有特定的dll是这样，但是上面可以看到一个普通的可执行程序`Exploitme`也是这样）。

### ASLR与堆栈基址之间的关系

Windows（至少Win10）下，开启`ASLR`后，程序的堆栈基址每次运行时都是随机的。
