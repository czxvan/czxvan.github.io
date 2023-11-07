---
title: Learning-C++
date: 2023-10-29 16:45:50
categories: C++
---

c++学习笔记。

<!-- more -->

## 基础新特性

- 命名空间 namespace

- 类型增强

  - 常量
    - const

      - 常量指针

        ```c
        const char* p = "hello world"; // const char* == char const*
        p[0] = 'H'; // 出错，常量指针，指向的是常量，无法通过常量指针修改所指内容
        ```

      - 指针常量

        ```c
        char* const p = "hello world";
        p++; // 出错，指针常量，无法修改p的值
        p[0] = 'H'; // 但可以修改所指向的内容
        ```

    - constexpr: 编译时求值

  - bool

  - enum

  - - 

- 运算符重载
  - 方便混合处理多种类型不同的值

- 变量初始化

  - 除了“=”，还可以使用 `{}`和`()`进行初始化

- auto

  - 编译期，自动类型推断

- 范围for语句

  - ```c
    for(auto x : v) {} // 存在内存复制操作
    for(auto &x : v) {} // 省去了内存复制操作
    ```

- new/delete

  - ```
    指针变量名 = new 类型名; // delete p;
    指针变量名 = new 类型名(初值); // delete p;
    指针变量名 = new 类型名[变量个数];	// delete[] p;
    ```

- nullptr
  - NULL : int 0
  - nullptr : std::nullptr_t | void * 0
  - nullptr == NULL == 0 √

- 强制类型转换

  - static_cast
  - dynamic_cast
  - const_cast
  - reinterpret_cast


## 引用

- 不占用内存，编译时转换为寄存器赋值

- 变量与引用的隐式转换

  ```
  int a = 10;
  int &a1 = a; // 同一个变量，一般不额外占内存：变量->引用
  int &a2 = a1; // 仍是同一个变量
  int b = a; // 创建新变量：变量->变量
  int b1 = a1; // 创建新变量：引用->变量
  ```

- 普通引用和常量引用

  - 不能通过常量引用修改变量
  - 作函数参数时，常量引用可以接收普通引用，但普通引用不能接收常量引用(常量)

## 结构体和类

- 结构体struct

  - 除了成员变量，还可以拥有成员函数

- 权限修饰符

  - public
  - protected
  - private

- 类class

  - 和结构体十分类似
  - 区别：结构体各成员默认public 类各成员默认private

- 代码组织结构

  ```plain
  student.h ：类Student的定义
  student.cpp ：#include "student.h" + 类Student的定义
  other.cpp : #include "student.h"
  ```

## 函数新特新

- 后置返回类型

  ```
  auto func(int, int);
  auto func(int, int) -> int {
  	return 0;
  }
  ```

- inline内联函数

  - 普通函数的定义一般放在.cpp文件，inline函数可以直接放在.h文件中（普通函数只能定义一次，但内联函数可以多次定义(得一致)）
  - 函数体代替函数调用，节省简单函数的调用开销

- 函数参数

  - 默认参数

  - 空参，空着或者 void

- 函数重载

  - 函数允许同名，但函数类型或参数要有明显区别

  - 比较函数类型时，const关键字会被忽略
  
- 成员函数修饰

  ```c++
  class XXX {
  	int param;
  	virtual int getParam() const { // const 表示该函数执行过程中不会修改类的成员变量
      return param;
      }
  }
  ```

## 标准库

### string

> 可变长字符串

- 初始化

  ```
  string s1;
  string s2 = "hello world";
  string s3 = s2; // 存在拷贝
  string s4("hello world");
  string s5(6, 'a'); // 连续6个'a'
  ```

- 常用方法

  ```
  .empty()
  .size() .length()
  .c_str() // 返回一个指向string对象内部内容（正规c字符串，以'\0'结尾）的指针
  for(auto c : s) // 支持范围for，c的类型是char
  for(auto &c : s) // 可以修改s中的字符
  ```

- 其它用法

  ```
  [] == > < + >> <<
  + 存在隐式类型转换，可以处理混合类型
    s1+'a' s1+"a"+“b" 允许
    "abc" + "def" + s2 不允许，先执行前两项的相加，但他们现在的类型无法相加
    
  .touppper() // 针对char?
  ```

### vector

> 可变长数组

- 不能装引用

  ```
  vector<int &> v; // 出错，引用在需要的时候加载到寄存器中，不占用内存
  ```

- 初始化

  ```c
  vector<string> strv1; // string默认初值为“”，int默认初值为0
  vector<string> strv2(strv1); // 存在内容拷贝 ()内部是vector时尝试拷贝，是整数时，认为是元素个数
  vector<string> strv3(10); // 10个空字符串
  vector<string> strv3 = str1; // 存在内容拷贝
  vector<string> strv3 = {"aaa", "bbb", "ccc"}; // c++11，使用初始化列表 {}内部数据一般被认为初始化列表，如果失败，可能会尝试认为它是元素个数。
  vector<string> strv3(10, "abc"); // 10个”abc
  ```

  

- 常用方法

  ```
  .empty()
  .size()
  .push_back()
  .insert(place_iter, value) // 返回一个指向被插入元素的迭代器，可能和第一个参数已经不一样了
  
  .clear()
  for(auto x : v) // 支持范围for
  for(auto &x : v) // 注意不要在范围for中改变vector对象的大小
  ```

- 其它用法

  ```
  [] == !=
  ```

### 迭代器

> 标准库中的每一个容器内都定义了相应的迭代器类型（包括iterator, reverse_iterator, const_iterator)
>
> 能够取代部分指针的作用，且更安全和优雅

- 成员函数

  ```
  .begin() // 返回一个指向容器第一个元素的iter  vector<xxx>::iterator
  .end() // 返回一个指向容器最后一个元素的后面的iter,不指向元素
  // 如果容器为空。则.begin() = .end(())
  .rbegin() // 返回一个指向容器最后一个元素的iter vector<xxx>::reverse_iterator
  .rend() // 返回一个指向容器第一个元素的前面的iter,不指向元素
  .cbegin() // 返回常量迭代器
  .cend() // c++ 11
  ```

- 其它用法

  ```c
  * -> ++ -- == !=
  *iter : 返回iter所指向元素的 引用
  (*iter).num == iter->num : 类似指针，当迭代器iter指向结构体时，可以使用*iter返回结构提的引用，也可以直接使用iter-> 访问结构体成员
  ```




## 类

- 继承

  ```c++
  class Mutator {
  protected:
  	int param;
  public:
  	Mutator(int param) : param(param) {}
  	virtual int getParam() const {
  		return param;
  	}
  	virtual void mutate(void *data, int size) const = 0;
  };
  class Multiplier : public Mutator {
  	int reserved[40]; // 现在没用到!
  public:
  	Multiplier(int multiplier = 0) : Mutator(multiplier) {}
  	virtual void mutate(void *data, int size) const {
  		int *ptr = (int *)data;
  		for (int i = 0; i < size / 4; ++i)
  			ptr[i] *= getParam();
  	}
  };
  ```

- 虚函数、虚表与多态

## Tricks

- 函数指针数组

  ```c++
  typedef void(*funcPtr)(); // 定义函数指针类型
  funcPtr functions[] = {...};
  ```

