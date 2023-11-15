---
title: redfish
date: 2023-11-14 21:14:30
tags:
categories: Fuzz
---

`redfish`协议模拟执行环境搭建。

参考资料：

- [【精选】Redfish 模型工具：Redfish Mockup Creator 和 Redfish Mockup Server_redfish模拟器-CSDN博客](https://blog.csdn.net/yeiris/article/details/122827845)
- [DMTF/Redfish-Mockup-Creator: A Python3 program that creates a Redfish Mockup folder structure from a real live Redfish service. (github.com)](https://github.com/DMTF/Redfish-Mockup-Creator)

- [DMTF/python-redfish-library: Python3 library for interacting with devices that support a Redfish service (github.com)](https://github.com/DMTF/python-redfish-library)

<!-- more -->

## Redfish Mockup Creator

### 介绍

Redfish模型创建器是一个从已开启的红鱼服务创建红鱼模型的工具。创建的实体模型可以与Redfish实体模型服务器一起使用。

Live Redfish Service -> Redfish Mockup

### 本地运行

```shell
# 拉取代码
git clone https://github.com/DMTF/Redfish-Mockup-Creator.git
# 安装refish
pip install redfish
# 运行
python redfishMockupCreate.py -u root -p root -r 192.168.1.100 -S -D /home/user/redfish-mockup
```

### docker运行

获取容器镜像

```shell
# 从dockerhub拉取容器镜像
docker pull dmtf/redfish-mockup-creator:latest
# 使用本地源码编译容器镜像
docker build -t dmtf/redfish-mockup-creator:latest .
# 从github编译容器镜像
docker build -t dmtf/redfish-mockup-creator:latest https://github.com/DMTF/Redfish-Mockup-Creator.git
```

运行命令

```shell
# 格式
docker run --rm --user="$(id -u):$(id -g)" -v <path-to-mockup>:/mockup dmtf/redfish-mockup-creator:latest -u root -p root -r 192.168.1.100 -S
# 实例
docker run --rm  -v  ${PWD}/mockup_iris:/mockup dmtf/redfish-mockup-creator:latest -u root -p 0penBmc -r 192.168.0.123 -S
```

## Redfish Mockup Server

Redifsh模型服务器针对红鱼模型提供红鱼请求。服务器运行在指定的IP地址和端口上，默认运行在127.0.0.1:8000上。

可以在[DSP2043](https://www.dmtf.org/dsp/DSP2043)中找到DMTF发布的实例模型。

要从真实服务创建实体模型，可以使用Redfish mockup Creator。

Redfish Mockup -> Simulated Redfish Service

```shell
# 拉取代码
git clone git@github.com:DMTF/Redfish-Mockup-Server.git
# 运行默认Mockup
python .\redfishMockupServer.py -H 0.0.0.0
```

```shell
# 向redfish服务发送请求，可以使用curl,postman,也可以使用python的request库或者redfish库
curl -k -H "content-type: application/json" -X GET http://127.0.0.1:8000/redfish/v1/Managers
```

## python redfish library

```shell
# 安装
pip install redfish
```

