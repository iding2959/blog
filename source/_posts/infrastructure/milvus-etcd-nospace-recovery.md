---
title: Milvus 服务异常：etcd MVCC 爆满 NOSPACE 故障排查与修复
date: 2026-07-14 10:00:00
description: Milvus 突然无法访问、集合加载失败？背后的元凶很可能是 etcd 数据库 MVCC 历史版本堆积导致 NOSPACE。本文完整复盘从定位到 compact、defrag 再到配额加固的全过程。
keywords: Milvus, etcd, NOSPACE, MVCC压缩, 向量数据库故障排查
categories: 基础设施
tags:
  - Milvus
  - etcd
  - K8s
---

## 引言

Milvus 作为热门的向量数据库，承载着 RAG 应用中关键的向量检索环节。它有一个看似不起眼却至关重要的依赖——etcd。etcd 负责存储 Milvus 的全部元数据：集合结构、分区信息、索引状态、租约等等。一旦 etcd 出问题，Milvus 轻则功能异常，重则整个服务不可用。

某天我照例检查服务状态时，发现 Milvus 查询接口报错、集合加载失败，而背后的元凶正是 etcd 的 MVCC（多版本并发控制）历史版本无限堆积，把默认 2GB 的存储配额撑爆，触发了 NOSPACE 告警。本文将完整复盘这次从"定位元凶"到"紧急止血"再到"配额加固防复发"的排查修复全过程。

## 一、故障现象

最初的表象全在 Milvus 这一层，非常具有迷惑性：

- Milvus 查询接口报错，集合加载失败；
- Milvus 日志中频繁出现 `etcdserver: mvcc: database space exceeded` 或 `request quota exceed` 相关错误；
- 新建集合、创建索引等元数据操作全部失败；
- 但 Milvus Pod 本身是 Running 状态，数据节点的向量检索在个别场景下似乎仍能工作。

此时如果只盯着 Milvus 看，很容易走弯路——问题的根源根本不在它身上，而在它背后的 etcd。

## 二、故障定位：锁定 etcd NOSPACE

### 1. 直接查看 etcd 状态

既然 Milvus 的日志指向了 etcd，先确认 etcd 的健康状态：

```bash
# 进入 etcd 容器（以 milvus 部署自带的 etcd 为例，实际容器名以 kubectl get pods 为准）
kubectl exec -it etcd-xxx -- sh

# 查看告警
etcdctl endpoint status --write-out=table
etcdctl alarm list
```

正常情况 `alarm list` 应该没有输出；如果出现 `memberID:xxxx alarm:NOSPACE`，说明 etcd 的存储配额已被耗尽，问题确认。

### 2. 查看数据库实际大小

```bash
# 查看 dbSize，对比默认 2GB 配额
etcdctl endpoint status --write-out=table
```

输出中 `DB SIZE` 一项如果显示 2.0 GB 左右且不再增长，同时 alarm 里有 NOSPACE，就实锤了：不是数据本身有多大，而是**历史版本把配额吃满了**。

### 3. 原理：MVCC 历史版本堆积

etcd 使用 MVCC 机制，每次写入都会产生新的 revision，旧版本数据不会立即删除，而是保留一段时间供 watcher 读取历史变更。Milvus 这类元数据操作频繁的系统，会持续写入和更新键值。如果没有开启自动压缩（auto-compaction），历史版本会无限累积，最终把默认 2GB 配额全部占满，触发 NOSPACE 后 etcd 拒绝一切写请求。

此时 etcd 只读不写，Milvus 的元数据操作自然全线失败。

## 三、紧急修复：compact + defrag 双管齐下

紧急修复的思路很直接：**先压缩历史版本释放逻辑空间，再整理碎片释放物理空间**。

### 1. 压缩（compact）：回收历史版本

```bash
# 获取当前最新的 revision
rev=$(etcdctl endpoint status --write-out="json" | jq -r '.[0].Status.header.revision')
echo $rev

# 压缩到这个 revision，此前的所有历史版本都会被回收
etcdctl compact $rev
```

`compact` 之后，历史版本被标记删除，但**物理空间并不会立即释放**——这部分空间只会标记为可复用。如果此时查看 dbSize，往往变化不大，这很正常，接下来需要 defrag。

### 2. 碎片整理（defrag）：释放物理空间

```bash
# 整理磁盘碎片，把 compact 后释放的逻辑空间真正归还给文件系统
etcdctl defrag

# 再次查看告警，此时 NOSPACE 应该已经消除
etcdctl alarm list

# 查看 dbSize，应已明显下降
etcdctl endpoint status --write-out=table
```

执行完 defrag 后，dbSize 会显著下降，NOSPACE 告警解除，etcd 恢复读写。此时 Milvus 的元数据操作应恢复正常，可以重新尝试之前的失败操作（加载集合、创建索引等）。

### 3. 需要重启 Milvus 的情况

如果 compact + defrag 之后，Milvus 的某些功能仍然异常（例如连接池中残留了失败的连接、租约状态错乱），可以重启 Milvus Pod 让它重新建立与 etcd 的连接：

```bash
kubectl delete pod milvus-standalone-xxxx
# 或者使用 deployment 滚动重启
kubectl rollout restart deployment milvus-standalone
```

Pod 删除后由控制器自动重建，观察状态和日志确认恢复正常：

```bash
kubectl get pods
kubectl logs -f milvus-standalone-xxxx
```

> ⚠️ 注意顺序：**先修复 etcd，再重启 Milvus**。如果 etcd 还没恢复就重启 Milvus，它起来后依然连不上、写不进，问题依旧。

## 四、防复发：etcd 配额加固

到这一步只是"止血"，如果不改配置，历史版本很快又会堆满配额，同样的故障会再次上演。防复发需要做三件事：**开启自动压缩、调高配额、定期整理碎片**。

### 1. 修改 etcd.yaml：通过环境变量注入参数

我当时的 etcd 部署原本没有 `args` 字段，数据目录是靠环境变量 `ETCD_DATA_DIR` 指定的。经过反复踩坑，最终采用的方案是**继续沿用环境变量方式**新增参数，而不是新增 `args` 块。

原因在于：etcd 镜像支持将启动参数转成环境变量传入（规则：`--auto-compaction-mode` → `ETCD_AUTO_COMPACTION_MODE`）。用环境变量**不会覆盖镜像默认的启动命令**，风格与现有配置统一，风险最小；而一旦新增 `args`，它会完全替换镜像默认参数，基础参数（如 `etcd`、`--name`）漏写就会直接启动失败。

修改前：

```yaml
containers:
- name: etcd
  image: quay.io/coreos/etcd:v3.5.5
  env:
    - name: ETCD_DATA_DIR
      value: /var/lib/etcd
  ports:
  - containerPort: 2379
  volumeMounts:
  - name: etcd-data
    mountPath: /var/lib/etcd
```

修改后（新增三个环境变量）：

```yaml
containers:
- name: etcd
  image: quay.io/coreos/etcd:v3.5.5
  env:
    - name: ETCD_DATA_DIR
      value: /var/lib/etcd
    # ===== 新增：自动压缩 + 配额调高 =====
    - name: ETCD_AUTO_COMPACTION_MODE
      value: revision
    - name: ETCD_AUTO_COMPACTION_RETENTION
      value: "1000"
    - name: ETCD_QUOTA_BACKEND_BYTES
      value: "8000000000"
  ports:
  - containerPort: 2379
  volumeMounts:
  - name: etcd-data
    mountPath: /var/lib/etcd
```

三个参数的含义：

| 环境变量 | 对应启动参数 | 作用 |
| --- | --- | --- |
| `ETCD_AUTO_COMPACTION_MODE` | `--auto-compaction-mode=revision` | 按 revision 号自动压缩历史版本 |
| `ETCD_AUTO_COMPACTION_RETENTION` | `--auto-compaction-retention=1000` | 只保留最近 1000 个 revision 历史，防止 MVCC 无限堆积 |
| `ETCD_QUOTA_BACKEND_BYTES` | `--quota-backend-bytes=8000000000` | 后端配额从默认 2GB 调到 8GB（单位是字节，不是 8G） |

小坑提醒：

- `ETCD_QUOTA_BACKEND_BYTES` 的值必须是**纯数字字节**，不能写成 `8G`，不要加引号以外的任何单位（yaml 中字符串数值建议加引号防止被解析为数字溢出）；
- `ETCD_AUTO_COMPACTION_RETENTION` 不要设太小（比如 10），否则必要的历史版本会被过早压缩，Milvus 元数据可能异常，1000 是稳妥值；
- 如果原本是走 Helm 管理的部署，不要直接改 yaml，应该在 values.yaml 中配置后 `helm upgrade`。

### 2. apply 并验证生效

```bash
kubectl apply -f etcd.yaml
```

apply 后 etcd Deployment 会滚动更新，Pod 自动重建，Milvus 会短暂断连 etcd，属于正常现象。

验证参数是否生效：

```bash
# 找到新的 etcd Pod
kubectl get pods

# 查看环境变量
kubectl describe pod etcd-xxx
```

在 `Environment` 区域确认三个新增环境变量全部存在。另外可以进入容器用 `ps` 查看进程参数，或执行 `etcdctl endpoint status` 确认配额数字已变化。

### 3. 定期 defrag（可选）

自动压缩解决的是"历史版本堆积"问题，但 defrag 不会自动执行。如果写入频繁，建议设置一个周期任务定期执行碎片整理：

```bash
# 例如配置一个 cron 定时执行（在 etcd 容器内）
etcdctl defrag
```

数据量不大的场景下，开启自动压缩后碎片增长缓慢，半年一年手动 defrag 一次也完全够用。

### 4. 重启 Milvus 验证

etcd Pod 正常 Running 之后，重启 Milvus 让它重新建立连接：

```bash
kubectl delete pod milvus-standalone-xxxx
kubectl get pods
kubectl logs -f milvus-standalone-xxxx
```

确认 Milvus 正常 Running、集合加载和查询恢复后，整个修复闭环才算完成。

## 五、总结

这次故障的完整链路可以归结为：**etcd 未开启自动压缩 → MVCC 历史版本无限堆积 → 超过默认 2GB 配额 → NOSPACE 只读 → Milvus 元数据操作全线失败**。

复盘下来有几个经验值得记下：

1. **Milvus 报错不一定是 Milvus 的锅**。它依赖 MinIO、etcd、Pulsar 等多个组件，排查时先顺着日志往下游找，本例的问题根源就在 etcd。
2. **NOSPACE 的修复顺序是 compact → defrag**。compact 回收历史版本、defrag 释放物理空间，只做 compact 不 defrag，dbSize 不会下降，效果不明显。
3. **防复发才是真正意义上的修复**。开启自动压缩 + 调高配额 + 定期 defrag，三件事缺一不可，否则故障会周期性重演。
4. **改 etcd 配置优先考虑环境变量而非 args**。args 会整体覆盖镜像默认启动参数，容易因漏写基础参数导致启动失败；环境变量方案不覆盖默认命令，风格统一且风险更小。

向量数据库是 RAG 应用的命脉，而 etcd 是 Milvus 的命脉。把这个"幕后组件"的配置做好，才能让 Milvus 稳定地跑下去。
