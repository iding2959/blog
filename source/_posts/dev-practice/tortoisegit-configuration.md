---
title: 小乌龟的配置 github SSHkey
date: 2025-07-10 19:00:00
description: TortoiseGit 配置与使用教程：SSH 密钥设置、中文界面、常用操作技巧。
keywords: TortoiseGit, Git, Windows, SSH, 版本控制
tags:
  - Git
  - GitHub
  - TortoiseGit
  - SSH
categories: 开发实践
---

## 概述
在配置新的开发环境时，git的配置必不可少，配置SSHkey能让我们免密进行pull/push等操作，由于个人习惯使用可视化的界面，小乌龟(git版)是可视化界面的不二之选。

## 文章目录
- 概述
- 文章目录
- SSH key 配置
  - 生成key
  - 配置user and email
  - 配置key
  - 验证key
  - 总结
- tortoisegit(小乌龟)配置
  - tortoisegit
  - 配置
- 结束语

## SSH key 配置
首先需要安装 Git，可以从 [Git 官方网站](https://git-scm.com/downloads) 下载最新版本。

### 生成key
```bash
// 安装git后，在你电脑上打开cmd或 git bash,输入
ssh-keygen -t rsa -C yourEmail  // yourEmail为登录GitHub仓库的邮箱

//输入后会询问是否以输出额外文件去保存，这里推荐直接回车，
//直接回车会在.ssh文件 默认生成id_rsa 和id_rsa.pub两个文件
//如果选择额外输出同样会生成类似的两个文件
Enter file in which to save the key (/c/Users/username/.ssh/id_rsa):

// 如果你曾经配置过,现在要重新生成,会询问你是否覆盖，如果你第一次配置，则不会出现此询问
/c/Users/username/.ssh/id_rsa already exists.
Overwrite (y/n)?
// 接下来它会询问是否需要密码，建议直接回车
Enter passphrase (empty for no passphrase):
// 再次输入密码，建议直接回车
Enter same passphrase again:
// 提示生成成功，请在C盘>用户>你的用户名>.ssh 去查看
Your identification has been saved in /c/Users/username/.ssh/id_rsa
Your public key has been saved in /c/Users/bingq/.ssh/id_rsa.pub
SHA256:略
The key's randomart image is:略
```

### 配置user and email
```bash
// 打开 git bash 输入
git config --global user.name "yourname" // GitHub名称
git config --global user.email  "youremail" // GitHub邮箱
```

### 配置key
1. 记事本打开刚才生成的id_rsa.pub,复制
2. 登录GitHub网站，点击右上角自己的头像,点击Settings,进入设置页面
3. 选择SSH and GPG keys
4. 选择 New SSH key
5. Title：起个名
6. Key: 将id_rsa.pub的内容粘贴至此
7. 选择 Add SSH key
8. 页面自动跳转后，你会发现你多了一个灰色的钥匙，这是因为你从未使用过这个Key

![GitHub SSH Key设置](../../../img/tortoisegit/hykey1.png)

### 验证key
```bash
// 打开git bash 输入以下内容，通过该地址验证key
//git@github.com不用改成你的邮箱地址，验证地址就是这个
ssh -T git@github.com
// 询问你是否继续连接，输入yes
The authenticity of host 'github.com (xx.xxx.xxx.xx)' can't be established.
RSA key fingerprint is SHA256:略.
Are you sure you want to continue connecting (yes/no/[fingerprint])? 
// 如果成功,他会发出以下内容
// 如果失败,请尝试在GitHub上删除生成的key，然后重新添加，注意复制时末尾不要有空格（可能会影响）
// 如果还是失败，请复制你的错误留言
Warning: Permanently added 'github.com,xx.xxx.xxx.xx' (RSA) to the list of known hosts
Hi yourname! You've successfully authenticated, but GitHub does not provide shell access.
```

### 总结
到这一步，便完成了sshkey的配置，你可以到Setting>SSH and GPG keys看到钥匙变绿，在GitHub仓库中复制仓库ssh地址进行克隆尝试，如果你不使用小乌龟，那么本文看到这里便可以了。

## tortoisegit(小乌龟)配置
### tortoisegit
使用过SVN的同学一定对小乌龟不陌生吧，实际上git也有小乌龟，操作页面和这个一模一样，是一款好用的可视化git界面，想尝试的同学可以在[TortoiseGit官方网站](https://tortoisegit.org/download/)下载。

### 配置
在配置之前，我仍需强调一件事，我们配置的是sshkey，所以只能使用ssh仓库地址去操作。

打开小乌龟设置页面，选择Network页面。默认情况下，他选择的是Git\bin\ssh.exe，由于我们配置sshkey，所以选择GIt\usr\bin\ssh.exe 点击确定便配置完成。

![TortoiseGit SSH设置](../../../img/tortoisegit/xwg2.png)

## 结束语
通过以上步骤，我们完成了GitHub SSH密钥的配置以及TortoiseGit的设置。这样在使用TortoiseGit进行Git操作时就可以免密码进行pull/push等操作，大大提高了开发效率。 