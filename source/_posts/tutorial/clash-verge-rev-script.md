---
title: Clash Verge Rev 脚本实现多个指纹浏览器环境对应不同的节点
date: 2025-07-22 19:30:00
index_img: /img/tutorial/clashvert.png
categories:
  - 教程
tags:
  - Clash
  - 代理
  - 指纹浏览器
---

## 背景介绍

使用指纹浏览器可以同时注册登录多个账号，但是多个账号使用同一个IP地址可能会出现风控问题，所以我们需要为每个浏览器用户配置不同的代理IP。通过Clash Verge Rev的脚本功能，我们可以轻松实现这一需求。

## 实现原理

Clash Verge Rev支持通过监听不同端口来分配不同的代理节点或节点分组。我们可以通过配置`listeners`参数，为每个指纹浏览器环境分配独立的端口和对应的节点或节点分组。

### 基本配置示例

以下是一个简单的配置示例，当访问端口10001时走美国地区分组：

```yaml
listeners:
- name: 📡 美国分组
  type: mixed
  port: 10001
  proxy: 🇺🇸 美国节点
```

其中：
- `name`: 监听器名称，可以自定义
- `type`: 监听器类型，`mixed`表示支持HTTP和SOCKS5协议
- `port`: 监听的端口号
- `proxy`: 指定使用的代理节点或节点分组名称

## 使用全局脚本实现多环境配置

Clash Verge Rev支持使用JavaScript脚本动态修改配置。我们可以编写一个全局脚本来批量设置多个监听端口，每个端口对应不同的节点或节点分组。

### 脚本示例

```javascript
function main(config, profileName) {
  // proxy 为 Clash Verge Rev 中节点名称 port为暴露端口 
  // type 为暴露类型    name 为自定义的名称
  const listeners = [{
    "name": "新加坡IP",
    "type": "mixed",
    "port": 40011,
    "proxy": "新加坡-优化1" // 节点对应的名称
  },
    {
      "name": "香港IP",
      "type": "mixed",
      "port": 40018,
      "proxy": "香港-优化1" // 节点对应的名称
    }
  ]
  config["listeners"] = listeners;
  return config;
}
```

这个脚本会：
1. 创建两个监听器配置
2. 第一个监听器使用端口40011，代理为"🇸🇬 新加坡节点"分组
3. 第二个监听器使用端口40018，代理为"香港(HK)节点"
4. 将这两个监听器配置应用到Clash配置中

## 在指纹浏览器中配置代理

配置好Clash Verge Rev后，我们需要在指纹浏览器的不同环境中分别配置代理：

1. 新加坡IP环境：
   ```
   协议: HTTP
   地址: localhost
   端口: 40011
   ```

2. 香港IP环境：
   ```
   协议: HTTP
   地址: localhost
   端口: 40018
   ```

## 实际效果展示

配置完成后，我们可以在指纹浏览器中检测IP地址，验证不同环境是否成功使用了不同的代理节点。以下是使用比特浏览器检测的效果图：

### 新加坡节点效果

![新加坡IP检测效果](/img/tutorial/clashverxiaoguo2.png)

可以看到，使用端口40011配置后，IP地址显示为新加坡(SG)，经纬度为103.8/1.3667。

### 香港节点效果

![香港IP检测效果](/img/tutorial/clashverxiaoguo1.png)

使用端口40018配置后，IP地址显示为香港(HK)，经纬度为114.1657/22.2578。

通过这种方式，我们可以为不同的指纹浏览器环境分配不同的IP地址，有效避免多账号使用同一IP导致的风控问题。

## 扩展配置

你可以根据需要扩展脚本，添加更多的监听器配置，例如：

```javascript
function main(config, profileName) {
  const listeners = [
    {
      "name": "新加坡IP",
      "type": "mixed",
      "port": 40011,
      "proxy": "🇸🇬 新加坡节点"
    },
    {
      "name": "香港IP",
      "type": "mixed",
      "port": 40018,
      "proxy": "香港(HK)节点"
    },
    {
      "name": "美国IP",
      "type": "mixed",
      "port": 40022,
      "proxy": "🇺🇸 美国节点"
    },
    {
      "name": "日本IP",
      "type": "mixed",
      "port": 40033,
      "proxy": "🇯🇵 日本节点"
    }
  ]
  config["listeners"] = listeners;
  return config;
}
```

## 注意事项

1. 确保你的Clash Verge Rev版本支持`listeners`配置和脚本功能
2. 节点名称和分组名称必须与你的Clash配置中的名称完全一致
3. 端口号不要与系统其他应用使用的端口冲突
4. 如果使用HTTP代理，可以将指纹浏览器中的代理协议改为HTTP

## 参考文档

- [Clash Meta 官方文档 - Listeners配置](https://wiki.metacubex.one/config/inbound/listeners) 