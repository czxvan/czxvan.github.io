---
title: Learning-git
date: 2023-11-06 10:20:00
tags:
categories: Learning-git
---

git学习笔记。

<!-- more -->

## 克隆

```shell
git clone <URL>
```



## 分支管理

产看本地分支

```shell
git branch
```

删除本地分支

```shell
git branch -d <branch_name>
```

新建本地分支并推送到远程

```shell
git checkout -b <branch_name>
git push --set-upstream origin <branch_name>
```

