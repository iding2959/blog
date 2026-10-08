---
title: PVE 存储全盘问号复盘（下）：真凶不是 pvestatd，而是时钟跳变引爆的 Ceph 雪崩
date: 2026-09-16 10:00:00
description: 同样的全盘问号再次出现，照上一篇的 killall 流程走却完全无效。这次卡点不在 pvestatd，而在内核 D 状态的 RBD 读 I/O——顺着内核栈一路挖下去，真凶是节点 RTC 时间错乱引发的定时器风暴，以及 logrotate 对全部 Ceph 守护进程的那一记 killall。
keywords: Proxmox VE, PVE存储问号, RTC时间错误, chrony时钟跳变, logrotate killall, Ceph RBD 卡死
categories: 基础设施
tags:
  - PVE
  - Homelab
  - Linux
  - ext4
  - Ceph
---

## 引言：上一篇的结论，这次只对了一半

半年前我写过一篇[《PVE 存储全盘问号、本地盘读不到的死锁故障排查与虚拟机跨盘导出恢复》](/2026/06/pve-storage-deadlock-recovery/)，结论是：外部存储（PBS/NFS）不可达 → `pvestatd` 轮询时陷入 I/O 等待 → 管理面单线程被拖死 → 网页端全盘问号。处置手段是 `killall -9 pvesm/pvestatd/pvedaemon/pveproxy` + 给失联存储加 `disable 1` + 重启服务。

2026 年 9 月 16 日傍晚，同样的"全盘问号"再次出现。我照着那套流程走了一遍——**完全无效**。

这一次的卡点根本不在 `pvestatd`，而在内核态：Ceph RBD 设备的读 I/O 卡住了，`mount` 进程停在不可中断的 `D` 状态。`killall -9` 连信号都送不进去，杀掉 `pvestatd` 只会让它在几秒后重新卡在同一个位置。

本文是那篇的续集与**纠错**：把这次的证据链完整摆出来，并给出真正有效的排查顺序。

## 一、现象：同样全盘问号，但关键指标和上次不一样

- PVE 网页端左侧树状图里，节点、虚拟机、容器、`local`、`local-lvm` 全带灰色问号；
- `pvestatd` 日志里出现单次状态更新耗时 **806 秒 / 1163 秒 / 1217 秒**——管理面确实被拖死了十几分钟；
- 但 `pvesm status` **1.5 秒正常返回**，所有存储都是 `active`；
- `df -h`、`/etc/pve/nodes`、corosync 仲裁全部正常。

一句话总结这个差异：**管理面确实被拖死了，但它不是"死锁在 pvestatd 自己的轮询逻辑里"，而是被内核 I/O 拖住的。**

而 `pvesm status` 快不快，恰好就是区分这两种情况的第一个分水岭。

## 二、排查过程：六步定位

### Step 1：先量化现象边界，别急着 killall

```bash
# 管理面到底卡不卡？给它加超时，别把自己也卡死
time timeout 20 pvesm status

# 网页端同源的存储视图（看 status 字段）
pvesh get /cluster/resources --type storage

# 管理面的卡顿证据
journalctl -u pvestatd | grep -E "status update time|not online|got timeout|mount error"
```

本次输出：

```plaintext
Name              Type     Status           Total            Used       Available        %
BIGSTOR            nfs     active    303692830720      4116769664    299576061056    1.36%
DevStore           rbd     active     45966258717      4842885661     41123373056   10.54%
local              dir     active        98497780        11121816        82326416   11.29%
local-lvm      lvmthin     active      2965176320       507341668      2457834651   17.11%
...
real    0m1.549s
```

```plaintext
pvestatd: storage 'BIGSTOR' is not online
pvestatd: mount error: Job failed. See "journalctl -xe" for details.
pvestatd: got timeout
pvestatd: status update time (1217.621 seconds)
```

`pvesm` 不卡、`pvestatd` 报存储挂载失败——说明问题不在 PVE 自己的轮询代码里，继续往内核走。

### Step 2：抓 D 状态进程与内核栈（本次的破局点）

```bash
ps -eo stat,pid,ppid,etime,wchan:34,args --no-headers | grep -E "^D"
```

```plaintext
D  12895  4821  01:34 bh_uptodate_or_lock  mount /dev/rbd0 /var/lib/lxc/.pve-staged-mounts/rootfs
```

```bash
cat /proc/12895/stack
```

```plaintext
[<0>] bh_uptodate_or_lock+0x9b/0xa0
[<0>] jread+0xf4/0x390
[<0>] do_one_pass+0xdc/0xde0
[<0>] jbd2_journal_recover+0x89/0x130
[<0>] jbd2_journal_load+0x143/0x410
[<0>] ext4_load_and_init_journal+0x2aa/0xc60
[<0>] ext4_fill_super+0x2f89/0x30e0
[<0>] path_mount+0x4e1/0xb20
[<0>] __x64_sys_mount+0x127/0x160
```

这一段栈信息是整次排查的转折点，翻译过来就是：

> 容器 rootfs 挂在 Ceph RBD 设备（`/dev/rbd0`）上，挂载时要做 ext4 日志回放（`jbd2_journal_recover`），而读日志块（`jread` → `bh_uptodate_or_lock`）**一直等不到 I/O 返回**。

内核态 D 状态 + RBD 设备 → 矛头立刻指向 Ceph，而不是 NFS。

> **经验**：`D` 状态的进程是杀不掉的，`kill -9` 只会挂在信号队列里。看到 D 状态，第一件事是 `cat /proc/<PID>/stack`，而不是 killall。

### Step 3：检查 Ceph 集群与 RBD 锁

```bash
ceph -s
ceph health detail
ceph osd tree | head
rbd showmapped
dmesg -T | grep -iE "rbd|libceph"
```

抓到四组异常：

```plaintext
HEALTH_WARN clock skew detected on mon.cl3
            nodown flag(s) set
            Slow OSD heartbeats on back (longest 1636.017ms)
            Slow OSD heartbeats on front (longest 1509.350ms)

[WRN] MON_CLOCK_SKEW: clock skew detected on mon.cl3
    mon.cl3 clock skew 6.68564e+07s > max 0.05s

    osd: 16 osds: 16 up (since 2m), 16 in (since 17M)
```

- **`clock skew detected on mon.cl3`：偏差 6.68e7 秒，约 774 天**——有一台节点的时钟差得离谱；
- `nodown flag(s) set`：有人给 Ceph 设置了 `nodown`，OSD 永远不会被判为 down，客户端会一直 hang 而不是切换；
- `Slow OSD heartbeats`：前端/后端网络心跳最长 1.6 秒；
- `16 osds: 16 up (since 2m)`：**所有 OSD 两分钟前刚重启过**——这是最可疑的一条。

再看内核日志：

```plaintext
rbd: rbd0: no lock owners detected
rbd: rbd0: no lock owners detected
rbd: rbd0: breaking header lock owned by client464914337
rbd: rbd0: capacity 214748364800 features 0x3d
EXT4-fs warning (device rbd0): ext4_multi_mount_protect:326: MMP interval 42 higher than expected, please wait.
```

重启前的老客户端（`client464914337`）没释放 RBD 镜像锁，新挂载要反复等待、最后强制破锁——这一步会白白卡掉几十秒，正好是"挂载卡住"的表象之一。

### Step 4：回溯上一个 boot，问一句"OSD 为什么刚全部重启"

```bash
journalctl --list-boots
journalctl -b -1 | grep -iE "clock was stepped|System clock wrong|loop take too long"
journalctl -b -1 --since "19:31:30" --until "19:31:52"
```

关键三行（注意：日志前缀里的 `Jun 16` 是**错误时钟自己的时间戳**）：

```plaintext
Jun 16 17:46:15 cl4 chronyd[2153]: System clock wrong by 72927926.233466 seconds
9 月 16 日 19:31:41 cl4 chronyd[2153]: System clock was stepped by 72927926.233466 seconds
9 月 16 日 19:31:43 cl4 pve-ha-crm[2854]: loop take too long (72927931 seconds)
```

**系统时钟被 chrony 一次性向前拨了 72,927,926 秒（约 844 天）**，从错误时间直接跳到当前时间。`pve-ha-crm` 那句 `loop take too long (72927931 seconds)` 就是时钟跳变的"指纹"。

时钟一跳，systemd 的 `OnCalendar` 定时器集体补跑：

```plaintext
9 月 16 日 19:31:41 cl4 systemd[1]: Starting logrotate.service - Rotate log files...
9 月 16 日 19:31:41 cl4 systemd[1]: Starting dpkg-db-backup.service - Daily dpkg database backup service...
9 月 16 日 19:31:41 cl4 systemd[1]: Starting e2scrub_all.service - Online ext4 Metadata Check for All Filesystems...
```

另外 RRD 也会报警，因为它没法接受时间倒退/跳跃：

```plaintext
pmxcfs: RRD update error ...: illegal attempt to update using time 1699576046
        when last update time is 1791451796 (minimum one second step)
```

### Step 5：谁 HUP 了 Ceph？——logrotate 的 postrotate

紧接着的下一行日志，凶手就自己报了名：

```plaintext
9 月 16 日 19:31:42 cl4 ceph-mon[2323]: received signal: Hangup from
  killall -q -1 ceph-mon ceph-mgr ceph-mds ceph-osd ceph-fuse radosgw rbd-mirror cephfs-mirror
  (PID: 2879) UID: 0
9 月 16 日 19:31:42 cl4 systemd[1]: ceph-osd@12.service: Deactivated successfully.
9 月 16 日 19:31:42 cl4 systemd[1]: ceph-mgr@cl4.service: Deactivated successfully.
9 月 16 日 19:31:42 cl4 systemd[1]: ceph-mds@cl4-cl4-mate.service: Deactivated successfully.
```

追这条 `killall` 的出处：

```bash
grep -rn "killall" /etc/logrotate.d/
```

```plaintext
/etc/logrotate.d/ceph-common:7:
    killall -q -1 ceph-mon ceph-mgr ceph-mds ceph-osd ceph-fuse radosgw rbd-mirror cephfs-mirror \
      || pkill -1 -x "ceph-mon|ceph-mgr|ceph-mds|ceph-osd|ceph-fuse|radosgw|rbd-mirror|cephfs-mirror" || true
```

**这是 logrotate 轮转 Ceph 日志后，让守护进程重新打开日志文件的常规 postrotate 动作。** 平时它人畜无害（每天轮转一次，发个 SIGHUP 让 Ceph 换日志句柄而已）；但在时钟跳变的那一秒，它和其它定时任务一起被"补跑"，于是这一记 SIGHUP 精准地砸在了刚起身、还没稳住的 Ceph 守护进程上。

至此链条完全闭合：

```plaintext
RTC 时间错乱
  → 节点开机后 chrony 大步长 step 系统时钟
  → systemd OnCalendar 定时器集体补跑
  → logrotate 轮转 Ceph 日志并执行 postrotate: killall -q -1 ceph-*
  → 本节点 Ceph 守护进程相继退出/重载，OSD 全部重启
  → RBD 读 I/O 停摆、旧客户端锁未释放
  → 各节点 mount /dev/rbdN /var/lib/lxc/.pve-staged-mounts/rootfs 卡在内核 D 状态
  → pvestatd 单线程被拖死 800~1200 秒
  → 网页端全盘问号
```

### Step 6：另一条独立病因——硬挂载 NFS 撞上后端重启

```bash
mount | grep -E "nfs"
journalctl -b -1 | grep "nfs: server"
```

```plaintext
192.168.0.108:/mnt/bigstor/DS01  on /mnt/pve/BIGSTOR type nfs4 (...,soft,timeo=10,retrans=2,...)
192.168.0.108:/mnt/bigstor/kstor on /mnt/pve/Kstor   type nfs4 (...,hard,timeo=600,retrans=2,...)
192.168.0.108:/mnt/bigstor/DSEtc on /mnt/pve/DS01    type nfs4 (...,hard,timeo=600,retrans=2,...)
```

```plaintext
cl2 kernel: nfs: server 192.168.0.252 not responding, timed out
cl2 kernel: nfs: server 192.168.0.252 not responding, timed out
cl2 kernel: nfs: server 192.168.0.252 not responding, timed out
```

- 一台节点在 17:29–17:32 被 `192.168.0.252` 的 NFS 超时刷屏，之后日志直接中断（没能留下正常关机记录）；
- 存储服务器（192.168.0.108）当天重启了多次，重启后 PVE 立刻报 `storage 'BIGSTOR' is not online`；
- 三个 NFS 存储里，只有 `BIGSTOR` 加固成了 `soft,timeo=10,retrans=2,retry=0`，`DS01` 和 `Kstor` 仍是默认的 `hard,timeo=600,retrans=2`。

**结论：NFS 是这次的"引信"，Ceph 是"炸药"。** 两者都会把 `pvestatd` 拖死，但处置方式完全不同。

## 三、根因总结

| 链条 | 触发 | 传导 | 结果 |
| ---- | ---- | ---- | ---- |
| 时钟链条 | RTC/BIOS 时间错（实测三台节点分别偏 1063 / 774 / 844 天） | chrony 大步长 step → 定时器补跑 → logrotate 对全部 Ceph 守护进程 `killall -1` | OSD 集体重启 → RBD I/O 停摆 → 挂载卡 D 状态 → `pvestatd` 被拖死 800~1200 秒 |
| NFS 链条 | 存储服务器重启、`192.168.0.252` 失联 | `hard,timeo=600` 挂载进入不可中断等待 | 同样是 D 状态、同样拖死管理面 |

## 四、与上一篇的差异（更正）

| 对比项 | 上一篇的结论 | 本次实测 |
| ---- | ---- | ---- |
| 现象 | `pvesm status` 卡死、无响应 | `pvesm status` **1.5 秒正常返回**，存储全 `active`，问号照样出现 |
| 卡点层级 | `pvestatd` 轮询外部存储陷入 I/O 等待 | **内核态 RBD 日志回放读 I/O**（`jbd2_journal_recover` → D 状态） |
| `killall -9 pvesm/pvestatd` | 有效，能解开死锁 | **无效**：D 状态进程送不进信号；杀掉 `pvestatd` 只是让它几秒后重新卡在同一处 |
| 处置顺序 | 先杀进程 → 禁用存储 → 重启服务 | 先救后端（Ceph/NFS）→ 对不可达存储 `disable 1` → 必要时重启节点 → **最后**才动管理面服务 |
| 排查入口 | 检查 `storage.cfg` 外置存储 | 先 `ps` 抓 D 状态进程 + `cat /proc/<PID>/stack`，再按设备类型分流 |

上一篇的核心逻辑并没有错——外置存储不可达确实会拖死管理面，这次也再次验证了（NFS 那条链条）。错的是**把"killall 管理进程"当成了通用解法**：它只对"管理面自己的轮询死循环"有效，对内核 D 状态 I/O 完全无能为力。

## 五、更新后的应急处置顺序（Runbook）

```bash
# 1) 先定位卡在哪一层：管理面 还是 内核
time timeout 20 pvesm status
ps -eo stat,pid,etime,wchan:30,args --no-headers | grep -E "^D"
cat /proc/<PID>/stack | head -12
ceph -s; ceph health detail

# 2) 若 D 状态卡在 NFS 挂载点：后端救不回来就先禁用该存储
#    编辑 /etc/pve/storage.cfg，在对应存储块末尾加一行 disable 1
mount -f -l /mnt/pve/<storage>   # 或直接重启该节点

# 3) 若 D 状态卡在 /dev/rbdN：先救 Ceph，别碰 PVE 管理服务
ceph -s
ceph osd unset nodown            # 清掉残留的 nodown，让 OSD 能正常判 down
systemctl restart ceph.target    # 必要时（单节点）

# 4) 校时：这一步经常被忽略，但本次就是它引发的
timedatectl; hwclock -r
chronyc tracking

# 5) 最后才重启管理面服务
systemctl restart pvestatd pvedaemon pveproxy
```

顺序原则：**先数据面（Ceph/NFS 后端），再存储配置，再节点，最后管理面。** 反过来做，只会反复卡在同一个位置。

## 六、预防措施

1. **修 RTC/CMOS（最高优先级）**：本次三台节点开机时 RTC 时间分别错误 1063 / 774 / 844 天。只要 RTC 不修，每次重启都会重演"时钟跳变 → 定时器风暴 → logrotate HUP Ceph"这套组合拳。换主板电池、进 BIOS 校时，并用 `hwclock -r` 与 `timedatectl` 复核。
2. **加固 chrony**：
   ```bash
   grep -E "makestep|rtcsync" /etc/chrony/chrony.conf
   # 建议保留 makestep（让时钟尽快对齐），但更关键的是 rtcsync——
   # 让 chrony 把正确时间写回 RTC，避免下次开机又从头错起
   ```
3. **收敛 logrotate 的 Ceph 段**：确认 `/etc/logrotate.d/ceph-common` 的 postrotate 是否必须对**所有** Ceph 守护进程发信号；可以缩小到必要进程，或改为夜间固定时段执行，避免与开机时的时间跳变撞车。
4. **统一 NFS 挂载参数**：至少不要让 `timeo=600` 的 `hard` 挂载对着一个会重启的存储服务器。`soft,timeo=10,retrans=2,retry=0` 的代价是写失败会返回 `EIO`（需要应用层重试），但对 PVE 管理面稳定性收益明显。注意 NFS 选项写在 `storage.cfg` 里才持久。
5. **清理 Ceph 的 `nodown`**：这个 flag 会让 OSD 永不判 down，客户端一直 hang 而不切换。确认无正在进行的维护后执行 `ceph osd unset nodown`。
6. **盯住 PBS 容量**：本次检查发现备份 datastore 已用 **81.97%**（14.76 TiB 只剩 1.92 TiB），且裁剪策略是 `keep-all=1`（**永不裁剪**）。要么改保留策略，要么扩容，否则备份迟早写失败。
7. **四类告警信号**（任一出现都值得立刻看）：
   - `pvestatd: status update time (N seconds)`，N 超过几十秒；
   - 内核 `nfs: server X not responding`；
   - `chronyd: System clock was stepped`；
   - `ceph health` 不再是 `HEALTH_OK`。

## 七、一句话总结

> PVE 的"全盘问号"只是一个**症状**。真正要问的是两个问题：**问号出现时，`pvesm status` 还跑得动吗？D 状态进程卡在哪个设备上？**
>
> 前者决定管理面是不是自己死锁（那就 killall + 重启服务），后者决定你是该去救 Ceph、还是该去修时钟。

只要 SSH 还能连上、`df` 还能跑，数据大概率是安全的——但"遇事不慌"的前提是**知道该看哪个指标**，而不是背一套固定的命令。
