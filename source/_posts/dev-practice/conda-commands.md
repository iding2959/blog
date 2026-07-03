---
title: Conda基础命令指南
date: 2025-05-31 14:30:00
description: Conda 环境管理常用命令速查表：环境创建、包管理、配置优化等实用技巧。
keywords: Conda, Python, 环境管理, 包管理, Miniconda, Anaconda
categories: 开发实践
tags:
  - Python
  - Conda
---

## 环境：Win10 64bit with conda 4.3.14

以下命令均在Windows命令行中输入。一般来讲，无论是在Linux，OS X还是在Windows系统中，在命令行窗口中输入的conda命令基本是一致的，除非有特别标注。

### 1. 获取版本号

```bash
conda --version
```

或

```bash
conda -V
```


查看某一命令的帮助，如update命令及remove命令：

```bash
conda update --help
conda remove --help
```

同理，以上命令中的`--help`也可以换成`-h`。

### 2. 环境管理

查看环境管理的全部命令帮助：

```bash
conda env -h
```

创建环境：

```bash
conda create --name your_env_name
```

输入y确认创建。

创建指定Python版本的环境：

```bash
conda create --name your_env_name python=2.7
conda create --name your_env_name python=3
conda create --name your_env_name python=3.5
```

创建包含某些包的环境：

```bash
conda create --name your_env_name numpy scipy
```

创建指定Python版本下包含某些包的环境：

```bash
conda create --name your_env_name python=3.5 numpy scipy
```

列举当前所有环境：

```bash
conda info --envs
conda env list
```

进入某个环境：

```bash
activate your_env_name
```

退出当前环境：

```bash
deactivate
```

复制某个环境：

```bash
conda create --name new_env_name --clone old_env_name
```

删除某个环境：

```bash
conda remove --name your_env_name --all
```

### 3. 分享环境

如果你想把你当前的环境配置与别人分享，这样他人可以快速建立一个与你一模一样的环境（同一个版本的Python及各种包）来共同开发/进行新的实验。一个分享环境的快速方法就是给ta一个你的环境的.yml文件。

首先通过`activate target_env`进入要分享的环境target_env，然后输入下面的命令会在当前工作目录下生成一个environment.yml文件：

```bash
conda env export > environment.yml
```

小伙伴拿到environment.yml文件后，将该文件放在工作目录下，可以通过以下命令从该文件创建环境：

```bash
conda env create -f environment.yml
```

当然，你也可以手写一个.yml文件用来描述或记录你的Python环境。

### 4. 包管理

列举当前活跃环境下的所有包：

```bash
conda list
```

列举一个非当前活跃环境下的所有包：

```bash
conda list -n your_env_name
```

为指定环境安装某个包：

```bash
conda install -n env_name package_name
```

如果不能通过conda install来安装，可以从Anaconda.org安装，但我们更习惯用pip直接安装。pip在Anaconda中已安装好，不需要单独为每个环境安装pip。如需要用pip管理包，activate环境后直接使用即可。 