---
title: Create a Blog with Hexo
date: 2023-10-17 16:17:38
tags:
- blog
- hexo
- next
categories: else
---

`Windows`下使用 `Hexo` 和 `github pages` 快速构建个人博客，

并针对`next`主题进行如下配置：修改语言、切换小主题、添加分类标签、文章折叠、本地搜索、多端同步等。

参考链接：

- [Hexo-Next 主题博客个性化配置超详细，超全面(两万字)-CSDN博客](https://blog.csdn.net/as480133937/article/details/100138838)

- [Hexo NexT文章中标题自动编号 | 孤傲小黑的博客 (guaoxiaohei.me)](https://blog.guaoxiaohei.me/posts/Hexo-Level/)

- [Hexo搭建博客的多终端同步问题 - 知乎 (zhihu.com)](https://zhuanlan.zhihu.com/p/476603074?utm_id=0)



<!-- more -->

## 环境依赖

- [nodejs](https://nodejs.org/en)

- [git](https://git-scm.com/download/win)

从官网下载并安装好 `nodejs` 和 `git`。

执行以下命令，若返回版本号，则表明安装成功。

```powershell
node --version
git --version
```

## github仓库

仓库名最好为 `用户名.github.io`，这样访问网站时用的`URL`是

```
用户名.github.io
```

不然得使用以下域名进行访问

```shell
用户名.github.io/仓库名
```

## 设置ssh

```powershell
ssh-keygen -t rsa -C "xxx@qq.com"
```

将本地`id_rsa.pub`的内容，拷贝到github设置中的`SSH and GPG keys`。

## 安装 Hexo

```powershell
npm install -g hexo-cli
```

新建并初始化一个目录

```shell
mkdir blog
hexo init blog    # 初始化
cd blog
npm install    # 安装组件
```

本地预览：

```powershell
hexo g    # 生成页面
hexo s    # 启动预览
# 若预览端口(4000)被占用，可使用hexo server -p 5000来更改端口号
# 页面是热更新的，更改 md 文件后刷新页面，就能看到修改后的内容
```

本地博客测试成功后，将其上传到github部署

```shell
# 安装hexo-deployer-git
npm install hexo-deployer-git --save 
# 修改_config.yml文件末尾的Deployment部分为
deploy:
  type: git
  repository: git@github.com:用户名/用户名.github.io.git
  branch: main
# 使用如下命令上传到github，就可以使用https://用户名.github.io进行访问
hexo d
```

## 新建博文

### 自动创建

进入博客所在目录，执行以下命令创建博文，在source/_posts目录下能看到一个My-New-Post.md文件

```shell
hexo new "My New Post"
```

### 手动创建

在source/_posts目录下新建一个md文件，并在文件开头加入如下格式的front-matter

```markdown
---
title: Hello World # 标题
date: 2019/3/26 hh:mm:ss # 时间
categories: # 分类
- Diary
tags: # 标签
- PS3
- Games
---

摘要
<!--more-->
正文
```

## 更换主题

[hexo themes](https://hexo.io/themes/)

```shell
cd blog
git clone https://github.com/next-theme/hexo-theme-next themes/next
npm install --save hexo-renderer-pug    # 安装依赖
```

## 配置主题

在根目录创建 `_config.next.yaml` 文件，并将`themes\next\_config.yaml`文件的内容复制到里面，现在共两个配置文件

- `_config.yaml` : Hexo站点配置
- `_config.[主题名].yaml` 这里以 `_config.next.yaml` 为例 ： 主题配置

### 站点配置

打开站点配置文件

#### 修改语言

搜索 `language`，找到如下代码

```plain
author:
language:
timezone:
```

在 language 后面输入 **zh-CN**，并修改作者名

### 主题配置

打开主题配置文件

### 开启分类和标签

搜索 `menu`，找到如下代码

```
menu:
  home: / || fa fa-home
  about: /about/ || fa fa-user
  tags: /tags/ || fa fa-tags
  categories: /categories/ || fa fa-th
  archives: /archives/ || fa fa-archive
  #schedule: /schedule/ || fa fa-calendar
  #sitemap: /sitemap.xml || fa fa-sitemap
  #commonweal: /404/ || fa fa-heartbeat
```

执行以下命令，会在`source/`目录下分别创建`about` `tags` 和 `categories`目录

```shell
hexo new page about
hexo new page tags
hexo new page categories
```

分别修改以上三个目录中的`index.md`文件，添加以下语句，以标明各自用途

```markdown
type: "about"
type: "tags"
type: "categories"
```

之后就可以在文章的头部添加 `tags` 和 `categories`，`hexo`会自动进行识别，比如：

```markdown
title: Create a Blog with Hexo
date: 2023-10-17 16:17:38
tags:
- blog
- hexo
- next
categories: 其它
```

#### 切换小主题

next 主题自带**四种样式**

搜索`Schemes`，选择喜欢的样式，取消对应行前的注释

```yaml
# Schemes
# scheme: Muse
# scheme: Mist
# scheme: Pisces
scheme: Gemini
```

#### 隐藏驱动提示

```yaml
# Powered by Hexo & NexT
powered: false
```

#### 首页文章折叠

在文章中想要结束预览的位置，添加以下标签：

```markdown
<!-- more -->
```

## 功能强化

### 本地搜索

安装插件`hexo-generator-searchdb`，命令如下:

```shell
npm install --save hexo-generator-searchdb
```

在站点配置文件 `_config.yaml` 文件中增加以下内容：

```yaml
search:
  path: search.xml
  field: post
  format: html
  limit: 10000
```

在主题配置文件 `_config.next.yaml` 中启用本地搜索功能：

```yaml
local_search:
  enable: true
```

### 多端同步

本地任意一空白目录下 git clone 之前的代码

```shell
git clone git@github.com:<your rep url ,eg :name.github.io.git>
```

新建hexo分支，并同步到远程

```
git checkout -b hexo
git push --set-upstream origin hexo
```

删除.git外的所有文件夹。

将之前的博客源文件复制过来，除去.deploy_git

新建或修改`.gitnore`文件：

```
.DS_Store
Thumbs.db
db.json
*.log
node_modules/
public/
.deploy*/
```

如果你在`themes`文件夹下 clone 过其它主题文件，把其中的 `.git`文件夹删除掉

上传文件到hexo分支

```
git add .
git commit -m "backup blog source"
git push 
```

另一台电脑的操作：

```
npm install hexo-cli -g			# intall hexo

# 在该电脑的本地文件夹下clone Blog源文件
git -b hexo clone <url>
```

clone结束后，进入blog文件夹下，安装原来的插件

```
npm install
npm install hexo-deployer-git --save
npm install hexo-hexo-renderer-marked #图片
```

写了博客后，这样上传：

```shell
## 多台终端写blog ，记得先和github端 同步 ##
git pull

## 上传博客
git add .
git commit -m ""
git push 
```
