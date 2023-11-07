---
title: Learning-git
date: 2023-11-06 10:20:00
tags: git
categories: else
---

git学习笔记。

<!-- more -->

## 克隆

```shell
git clone <URL> <local_repo_name>(可选)
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

切换分支（切换之后，本地文件目录会变为该分支的内容）

```
git checkout <branch_name>
```

