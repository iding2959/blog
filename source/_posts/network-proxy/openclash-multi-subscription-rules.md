---
title: OpenClash 多订阅聚合与分流规则配置指南
date: 2026-06-19 11:47:00
description: 将多个机场订阅聚合到 OpenClash 中，通过 proxy-provider 合并节点池、rule-provider 实现精细化分流，打造高可用、自动故障切换的科学上网方案。
keywords: OpenClash, proxy-provider, rule-provider, 订阅聚合, 分流规则, Clash, 旁路由, 软路由, 自动故障切换
categories: 网络与代理
tags:
  - OpenClash
  - Clash
  - Proxy
  - OpenWrt
---

## 为什么需要多订阅聚合？

玩软路由的朋友或多或少都经历过——机场跑路、节点失联、线路绕路、晚高峰爆炸。单靠一家机场，稳定性永远是个玄学问题。

**多订阅聚合**的核心思路很简单：把你的几个机场订阅合在一起，配合自动测速切换策略，死一个订阅其他依旧能用。

但 OpenClash 默认订阅面板只支持**单链接**。想实现多机场聚合 + 精细化分流，需要手动编辑 `config.yaml`，用上 `proxy-providers` 和 `rule-providers` 两个高级功能。

这篇文章以两个机场为例，从零讲清楚如何配置，直接对着改就行。

---

## 整体架构一览

```
┌──────────────────────────────────┐
│         proxy-providers          │
│  ┌────────────┐ ┌────────────┐  │
│  │   机场A    │ │   机场B    │  │
│  └─────┬──────┘ └─────┬──────┘  │
│        │               │         │
│        └───────┬───────┘         │
│                │                 │
│                ▼                 │
│  ┌─────────────────────┐        │
│  │  ♻️ 自动选择        │        │
│  │  (url-test)         │        │
│  └─────────┬───────────┘        │
│            │                    │
│            ▼                    │
│  ┌─────────────────────┐        │
│  │  🌍 国外兜底        │        │
│  │  (select)           │        │
│  └─────────┬───────────┘        │
│            │                    │
│            ▼                    │
│  ┌─────────────────────┐        │
│  │  🚀 手动选择        │        │
│  │  (select)           │        │
│  └─────────────────────┘        │
└──────────────────────────────────┘
                  │
                  ▼
      ┌─────────────────────┐
      │   rule-providers    │
      │  ┌─────────────────┐│
      │  │ OpenAI 规则集    ││
      │  │ Proxy 规则集     ││
      │  └─────────────────┘│
      └─────────────────────┘
                  │
                  ▼
            分流规则引擎
     (GEOIP → DIRECT / MATCH → 国外兜底)
```

三层策略：

1. **proxy-providers** — 聚合多个机场的节点
2. **proxy-groups** — 按策略组织节点（手动选 / 自动测速 / 兜底故障转移）
3. **rule-providers + rules** — 精细控制哪些流量走代理、哪些直连

---

## 第一步：proxy-providers — 聚合多个机场

OpenClash 中，`proxy-providers` 相当于"动态节点来源"。把你的机场订阅链接填进去，Clash 会定期拉取并合并所有节点。

```yaml
proxy-providers:
  机场A:
    type: http
    url: https://你的机场A订阅链接
    interval: 3600        # 每小时更新一次
    proxy: DIRECT         # 订阅请求走直连（不走代理）
    path: ./providers/机场A.yaml
    exclude-filter: (?i)(距离下次重置)|(到期)|(流量)|(套餐)|(官网)
    health-check:
      enable: true
      url: https://cp.cloudflare.com/generate_204
      interval: 300       # 每5分钟检测节点可用性
    override:
      skip-cert-verify: false

  机场B:
    type: http
    url: https://你的机场B订阅链接
    interval: 3600
    proxy: DIRECT
    path: ./providers/机场B.yaml
    exclude-filter: (?i)(距离下次重置)|(到期)|(流量)|(套餐)|(官网)
    health-check:
      enable: true
      url: https://cp.cloudflare.com/generate_204
      interval: 300
    override:
      skip-cert-verify: true   # 如果机场证书有问题就设为true
```

### 关键参数说明

| 参数 | 作用 | 推荐值 |
|------|------|--------|
| `type: http` | 订阅来源为 HTTP(S) URL | 必填 |
| `interval` | 自动更新间隔（秒） | 3600（1小时） |
| `proxy` | 拉取订阅时走哪个出站 | `DIRECT` 即可 |
| `health-check.url` | 节点存活检测地址 | `https://cp.cloudflare.com/generate_204` |
| `health-check.interval` | 检测间隔（秒） | 300（5分钟） |
| `override.skip-cert-verify` | 跳过证书验证 | 大部分机场 `false`；证书有问题的填 `true` |

### exclude-filter — 排除杂项节点

机场订阅里常常混入一堆无用信息节点——"剩余流量"、"到期时间"、"官网链接"。不去掉的话会在面板里显示成假节点。

用正则一键过滤：

```yaml
exclude-filter: (?i)(距离下次重置)|(到期)|(流量)|(套餐)|(官网)
```

`(?i)` 表示不区分大小写。你也可以按自己机场的实际命名加减关键词。

---

## 第二步：proxy-groups — 策略组设计

三个策略组，各司其职：

```yaml
proxy-groups:
  # 第一层：手动主控
  - name: 🚀 手动选择
    type: select
    use:
      - 机场A
      - 机场B
    proxies:
      - ♻️ 自动选择
      - 🌍 国外兜底
      - DIRECT

  # 第二层：自动测速选优
  - name: ♻️ 自动选择
    type: url-test
    url: http://www.gstatic.com/generate_204
    interval: 300        # 每5分钟重新测速
    tolerance: 50        # 延迟差在50ms以内不切换
    use:
      - 机场A
      - 机场B

  # 第三层：兜底保底
  - name: 🌍 国外兜底
    type: select
    use:
      - 机场A
      - 机场B
    proxies:
      - ♻️ 自动选择
      - DIRECT
```

### 策略组职责

| 策略组 | 类型 | 作用 |
|--------|------|------|
| 🚀 手动选择 | `select` | 手动指定走哪个订阅或哪个具体节点，最高优先级 |
| ♻️ 自动选择 | `url-test` | 自动测速，选**延迟最低**的节点 |
| 🌍 国外兜底 | `select` | 当其他节点全挂时兜底，可切回 `DIRECT` |

### url-test 的工作方式

`url-test` 策略组每隔 `interval` 秒向所有节点发送一次 HTTP 请求，测量延迟，然后自动把流量切到**延迟最低**的那个节点。

`tolerance: 50` 意味着：当前节点延迟 200ms，另一个节点 160ms——差距超过 50ms，就切换过去。避免"因为 2ms 的微小差异就频繁跳切"。

### 为什么国外兜底要包含 DIRECT？

如果所有机场同时挂掉（虽然概率不大但玩路由久了就知道什么妖魔鬼怪都有），`🌍 国外兜底` 可以手动切到 `DIRECT`，至少保证国内网站正常访问，不会整个网络瘫痪。

---

## 第三步：rule-providers — 规则集

规则集决定了**哪些流量走代理，哪些直连**。OpenClash 自带大量规则集，你也可以自定义。

```yaml
rule-providers:
  OpenAI:
    type: file
    behavior: classical
    path: ./rule_provider/OpenAI
    interval: 86400      # 每天更新一次

  Proxy:
    type: file
    behavior: classical
    path: ./rule_provider/Proxy
    interval: 86400
```

- **OpenAI 规则集** — 包含 OpenAI / ChatGPT 相关域名，保证 AI 服务走代理
- **Proxy 规则集** — 包含所有需要代理的常见域名（Google / YouTube / Twitter 等）

`behavior: classical` 表示经典域名匹配模式。一般用 `classical` 就够了，性能最好。

### 内置规则集位置

OpenClash 预置了很多规则集文件，通常在 `/etc/openclash/rule_provider/` 下。你也可以从 [Loyalsoldier/clash-rules](https://github.com/Loyalsoldier/clash-rules) 下载自定义规则集。

---

## 第四步：rules — 分流规则

最后一步，把所有策略串起来：

```yaml
rules:
  # OpenAI 相关流量 → 手动选择策略组
  - RULE-SET,OpenAI,🚀 手动选择

  # 需要代理的常见域名 → 手动选择策略组
  - RULE-SET,Proxy,🚀 手动选择

  # 中国大陆 IP → 直连
  - GEOIP,CN,DIRECT

  # 以上都没命中 → 国外兜底
  - MATCH,🌍 国外兜底
```

### 规则匹配顺序（从上到下，命中即停止）

```
请求进入
    │
    ▼
┌─ RULE-SET,OpenAI ──→ 🚀 手动选择（命中则走代理）
├─ RULE-SET,Proxy  ──→ 🚀 手动选择（命中则走代理）
├─ GEOIP,CN         ──→ DIRECT（国内 IP 直连）
└─ MATCH            ──→ 🌍 国外兜底（兜底走代理）
```

**设计原则**：白名单思维——明确知道需要代理的走代理（OpenAI + Proxy 规则集），明确知道国内的走直连（GEOIP），剩下的也走代理兜底。比"黑名单"更不容易漏网，也更安全。

---

## 第五步：在 OpenClash 中加载配置

### 方法一：直接替换配置文件

1. 将上述配置合并成完整的 YAML 文件
2. 放置到 `/etc/openclash/config/` 目录下
3. 在 OpenClash 面板中切换到该配置

### 方法二：OpenClash 面板分段编辑

OpenClash 的 Luci 页面提供了**配置文件管理**界面，你可以在"配置文件订阅"中添加 proxy-provider 订阅，在"规则附加"中修改 rules。

但多订阅聚合建议直接用方法一——手动编辑 YAML 更灵活可控，不会被面板的模板语法限制。

### 完整的 config.yaml 骨架

为了方便你快速上手，这里给出一个可直接使用的完整配置。替换订阅链接即可。

```yaml
port: 7890
socks-port: 7891
allow-lan: true
mode: rule
log-level: info
external-controller: 127.0.0.1:9090

proxy-providers:
  机场A:
    type: http
    url: https://你的机场A订阅链接
    interval: 3600
    proxy: DIRECT
    path: ./providers/机场A.yaml
    exclude-filter: (?i)(距离下次重置)|(到期)|(流量)|(套餐)|(官网)
    health-check:
      enable: true
      url: https://cp.cloudflare.com/generate_204
      interval: 300
    override:
      skip-cert-verify: false

  机场B:
    type: http
    url: https://你的机场B订阅链接
    interval: 3600
    proxy: DIRECT
    path: ./providers/机场B.yaml
    exclude-filter: (?i)(距离下次重置)|(到期)|(流量)|(套餐)|(官网)
    health-check:
      enable: true
      url: https://cp.cloudflare.com/generate_204
      interval: 300
    override:
      skip-cert-verify: true

rule-providers:
  OpenAI:
    type: file
    behavior: classical
    path: ./rule_provider/OpenAI
    interval: 86400
  Proxy:
    type: file
    behavior: classical
    path: ./rule_provider/Proxy
    interval: 86400

proxy-groups:
  - name: 🚀 手动选择
    type: select
    use:
      - 机场A
      - 机场B
    proxies:
      - ♻️ 自动选择
      - 🌍 国外兜底
      - DIRECT

  - name: ♻️ 自动选择
    type: url-test
    url: http://www.gstatic.com/generate_204
    interval: 300
    tolerance: 50
    use:
      - 机场A
      - 机场B

  - name: 🌍 国外兜底
    type: select
    use:
      - 机场A
      - 机场B
    proxies:
      - ♻️ 自动选择
      - DIRECT

rules:
  - RULE-SET,OpenAI,🚀 手动选择
  - RULE-SET,Proxy,🚀 手动选择
  - GEOIP,CN,DIRECT
  - MATCH,🌍 国外兜底
```

---

## 常见问题排查

### 1. 节点列表为空 / 订阅拉取失败

- 检查机场订阅链接是否有效（在浏览器里直接访问看能不能下载）
- 检查 `proxy: DIRECT` — 部分网络下拉取订阅本身可能需要走代理，换成 `proxy: 🚀 手动选择` 试试
- OpenClash 日志里看具体报错：`log-level: debug`

### 2. url-test 频繁跳切

- 调大 `tolerance` 值（比如 100-150ms），减少微小延迟波动导致的切换
- 加大 `interval`（比如 600 秒），降低测速频率

### 3. 规则不生效

- 确认 `rule-providers` 的 `path` 文件真实存在
- 确认 `behavior` 类型与规则集文件格式匹配
- 检查 OpenClash 面板中是否勾选了"禁用规则"

### 4. 部分机场节点证书报错

- 把对应 `proxy-provider` 的 `override.skip-cert-verify` 设为 `true`

---

## 总结

这套配置的核心优势：

- **高可用** — 多个机场节点池，自动测速选最优，一个挂了不影响全局
- **精细分流** — OpenAI 单独规则集，国内 IP 直连，国外流量走代理
- **低维护** — proxy-provider 每小时自动更新，rule-provider 每天更新，基本不用手动管
- **灵活切换** — 🚀 手动选择 → ♻️ 自动测速 → 🌍 兜底保底，三层故障转移

折腾完这一套，自此告别"机场又挂了"的烦恼。
