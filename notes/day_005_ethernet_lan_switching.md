
# Day 5: Ethernet LAN Switching (Part 1)

## 学习目标

学完本日内容后，你应该能够：

1. 解释以太网局域网交换（Ethernet LAN Switching）为什么属于 OSI 第 1 层和第 2 层的内容。
2. 区分物理层（Physical Layer）和数据链路层（Data Link Layer）的职责。
3. 说明局域网（Local Area Network, LAN）的基本边界：交换机扩展 LAN，路由器分隔 LAN。
4. 说出 OSI 封装过程中常见 PDU 名称：data、segment、packet、frame。
5. 画出并解释以太网帧（Ethernet frame）的主要字段、字段长度和作用。
6. 理解 MAC 地址（MAC address）的长度、格式、OUI、BIA 以及十六进制表示法。
7. 解释交换机如何通过源 MAC 地址学习 MAC 地址表。
8. 区分未知单播帧（unknown unicast frame）和已知单播帧（known unicast frame）。
9. 解释 flooding 与 forwarding 的区别，以及交换机为什么不会从收到帧的端口再发回去。
10. 完整解析本视频 5 道 Quiz，掌握 Day 5 的高频考点。

---

## 核心概念与原理

### 1. Ethernet LAN Switching 的位置

以太网（Ethernet）同时涉及 OSI 第 1 层和第 2 层：

* 第 1 层：物理层（Physical Layer）

  * 负责线缆、接口、电信号、光信号、无线信号等。
  * 例如 UTP 铜缆、光纤、RJ45 接头、100 米传输距离限制。
* 第 2 层：数据链路层（Data Link Layer）

  * 负责节点到节点（node-to-node）的数据传输。
  * 负责把第 3 层 packet 封装成第 2 层 frame。
  * 使用 MAC 地址，而不是 IP 地址。
  * 交换机主要工作在第 2 层。

本节重点不是“网线怎么传信号”，而是“交换机收到 Ethernet frame 后如何处理”。

---

### 2. LAN 的边界

局域网（Local Area Network, LAN）可以先简单理解为一个相对小范围内的网络，比如家庭网络、办公室楼层网络。

本节最重要的规则是：

* 交换机不会分隔 LAN。
* 增加交换机通常是在扩展同一个 LAN。
* 路由器用于连接并分隔不同 LAN。

例如：

```text
PC1 --- SW1 --- R1 interface
PC2 ---/
PC3 ---/
```

这些 PC、交换机、以及它们连接的路由器接口，可以看作一个 LAN。

如果两个交换机直接互连：

```text
PC1 --- SW1 --- SW2 --- PC3
PC2 ---/          \--- PC4
```

这仍然可以是同一个 LAN，因为交换机只是扩展了二层网络。

但如果两个交换机分别接到路由器的不同接口：

```text
PC1 --- SW1 --- R1 G0/0

PC2 --- SW2 --- R1 G0/1
```

这通常表示两个不同的 LAN，因为路由器接口之间分隔二层网络。

---

### 3. OSI 封装与 PDU

协议数据单元（Protocol Data Unit, PDU）是指不同 OSI 层对数据的叫法。

封装顺序如下：

```text
上层数据
  ↓ 加 Layer 4 header
Segment
  ↓ 加 Layer 3 header
Packet
  ↓ 加 Layer 2 header + Layer 2 trailer
Frame
  ↓ 转成物理信号发送
Bits / Signals
```

Day 5 关注的是第 2 层 PDU：帧（Frame），更具体地说是以太网帧（Ethernet frame）。

---

### 4. Ethernet frame 字段总览

以太网帧由 header、payload 和 trailer 组成。本节重点关注 header 与 trailer。

```text
+----------+-----+-----------------+------------+-------------+-----+
| Preamble | SFD | Destination MAC | Source MAC | Type/Length | FCS |
+----------+-----+-----------------+------------+-------------+-----+
| 7 bytes  | 1B  | 6 bytes         | 6 bytes    | 2 bytes     | 4B  |
+----------+-----+-----------------+------------+-------------+-----+
```

字段作用：

| 字段            |    长度 | 作用                                   |
| --------------- | ------: | -------------------------------------- |
| Preamble        | 7 bytes | 接收端时钟同步                         |
| SFD             |  1 byte | 标记 preamble 结束、真正帧内容开始     |
| Destination MAC | 6 bytes | 目标二层地址                           |
| Source MAC      | 6 bytes | 源二层地址                             |
| Type/Length     | 2 bytes | 表示上层协议类型，或表示被封装数据长度 |
| FCS             | 4 bytes | 使用 CRC 检测传输错误                  |

Header 加 trailer 合计：

```text
7 + 1 + 6 + 6 + 2 + 4 = 26 bytes
```

注意：这里的 26 bytes 是视频中统计的这些字段总和。考试中如果问标准 Ethernet frame header，有时不把 Preamble 和 SFD 计入 Ethernet frame header 的一部分，要根据题目语境判断。本视频按 Jeremy 的讲解，把 Preamble、SFD、Destination、Source、Type/Length 与 FCS 一起作为整体来看。

---

### 5. MAC 地址与交换机转发

MAC 地址（Media Access Control address）是二层地址，通常烧录在网卡或设备接口上，也叫 burned-in address（BIA）。

基本规则：

* MAC 地址长度：48 bits = 6 bytes。
* 通常写成 12 个十六进制字符。
* Cisco 常见格式：`AAAA.AA00.0001`
* 前 24 bits，也就是前 3 bytes，是 OUI（Organizationally Unique Identifier）。
* 后 24 bits，也就是后 3 bytes，用于标识厂商生产的具体设备。

交换机处理帧的核心规则：

1. 交换机看 source MAC 来学习 MAC 地址表。
2. 交换机看 destination MAC 来决定如何转发。
3. 如果 destination MAC 已知，执行 forwarding。
4. 如果 destination MAC 未知，执行 flooding。
5. Flooding 会从除入接口以外的所有接口发出。
6. Cisco 交换机动态 MAC 地址默认 5 分钟无活动后老化删除。

---

## 分章节详细讲解

## [0:00] Introduction

### 先建立直觉

前几天课程介绍了网络模型、线缆、接口和基础概念。Day 5 开始进入“数据到底怎么在局域网里走”的细节。

这节课只看一个较小范围：主机、交换机和路由器接口之间，在同一个 LAN 内部，Ethernet frame 如何被接收、学习、泛洪和转发。

本节不深入讨论路由器如何把数据转发到其他网络。跨网络通信会在后续课程讲。

### 详细讲解

假设有一个简单网络：

```text
PC1 ----\
PC2 ----- SW1 ----- R1 ----- Internet
PC3 ----/
```

Day 5 重点不是 Internet，也不是路由器到外网的过程，而是：

* PC 发出的 Ethernet frame 到达交换机后，交换机会做什么？
* 交换机怎样知道某个 MAC 地址在哪个端口？
* 当交换机不知道目标在哪时，为什么会把帧发到多个端口？
* 当交换机知道目标在哪时，为什么只发到一个端口？

这就是 Ethernet LAN Switching 的核心。

### 配置或示例（如适用）

本视频没有实际 Cisco IOS 配置演示，也没有 Packet Tracer Lab。视频结尾明确说明，本视频没有单独 practice lab，Packet Tracer lab 会留到 Ethernet LAN Switching Part 2 之后。

### 必须掌握

* Day 5 是 Ethernet LAN Switching Part 1。
* 重点是同一个 LAN 内，交换机如何处理 Ethernet frame。
* 跨 LAN、跨路由器通信不是本视频重点。

### 常见误区

* 误以为交换机负责把数据“路由”到 Internet。普通二层交换机不做路由决策。
* 误以为只要有路由器出现在图中，本节就要讨论 IP 路由。Day 5 主要还是二层交换。

### 主动回忆

1. Ethernet LAN Switching 主要研究哪一类设备的行为？
2. 本视频为什么先不讨论路由器转发到其他网络？
3. 同一个 LAN 内通信和跨 LAN 通信最大的设备边界是什么？

---

## [0:59] OSI Model - Physical Layer review

### 先建立直觉

要理解 Ethernet，先要分清楚第 1 层和第 2 层。

第 1 层像“道路和电信号”：线是什么、接头是什么、电压怎么变、能传多远。

第 2 层像“这条路上的车辆格式和本地投递规则”：frame 怎么长、MAC 地址怎么写、交换机怎么投递。

### 详细讲解

物理层（Physical Layer）定义传输介质的物理特性，包括：

* 电压等级（voltage levels）
* 最大传输距离（maximum transmission distance）
* 物理连接器（physical connectors）
* 线缆规格（cable specifications）
* 有线网络中的电信号
* 无线网络中的无线电信号

例如，Ethernet UTP cable 常见最大距离是 100 米。这就是 Layer 1 的知识。

数字比特（bits）最终要变成某种物理信号：

* 铜缆：电信号
* 光纤：光信号
* 无线：无线电信号

Day 2 学过的 UTP、光纤、RJ45、线序等都属于 Layer 1。

### 配置或示例（如适用）

本章没有配置命令。

可以用下面的方式理解：

```text
应用数据
  ↓
网络协议封装
  ↓
Ethernet frame
  ↓
转换为电信号 / 光信号 / 无线信号
  ↓
在物理介质上传输
```

Layer 1 不关心 MAC 地址表，也不关心目的 MAC 是谁。它只负责把 bit 变成信号、把信号传过去。

### 必须掌握

* Layer 1 负责物理介质和信号。
* Ethernet 的线缆、接口、距离限制属于 Layer 1。
* Day 5 会从 Layer 1 复习过渡到 Layer 2 交换。

### 常见误区

* 把 RJ45、线序、光纤类型和 MAC 地址表混在一起。前者是 Layer 1，后者是 Layer 2。
* 认为物理层能识别目标设备。物理层只传信号，不做二层转发表判断。

### 主动回忆

1. UTP 线缆 100 米限制属于 OSI 哪一层？
2. 铜缆中比特通常转换成什么形式传输？
3. Layer 1 是否关心 MAC 地址？

---

## [1:54] OSI Model - Data Link Layer review

### 先建立直觉

如果 Layer 1 是“把信号送过去”，Layer 2 就是“把这一跳的数据包装好，并送到本地链路上的正确节点”。

数据链路层（Data Link Layer）提供节点到节点（node-to-node）的连接和数据传输。

这里的 node-to-node 可以是：

* PC 到 switch
* switch 到 router
* router 到 router
* switch 到 switch

### 详细讲解

Layer 2 的职责包括：

1. 定义数据如何在物理介质上传输前进行格式化。

   * 在 Ethernet 中，就是封装成 Ethernet frame。
2. 检测并可能纠正物理层错误。

   * Ethernet frame 中的 FCS 字段用于错误检测。
3. 使用 Layer 2 addressing。

   * Ethernet 使用 MAC 地址。
4. 与 Layer 3 addressing 分开。

   * IP 地址是 Layer 3 地址，不是 Layer 2 地址。
5. 交换机主要运行在 Layer 2。

   * 交换机根据 MAC 地址表转发 Ethernet frame。

Ethernet 本身涉及：

* Layer 1：线缆、接口、信号。
* Layer 2：Ethernet frame、MAC 地址、switching。

本视频重点是 Ethernet 的 Layer 2 部分。

### 配置或示例（如适用）

本章无配置命令。

可以这样对比：

| 层级    | 地址        | 设备关注点                |
| ------- | ----------- | ------------------------- |
| Layer 2 | MAC address | 交换机根据 MAC 转发 frame |
| Layer 3 | IP address  | 路由器根据 IP 转发 packet |

### 必须掌握

* IP 地址是 Layer 3 地址。
* MAC 地址是 Layer 2 地址。
* 交换机使用 MAC 地址表转发 frame。
* 本节重点是 Ethernet frame 在 LAN 内如何被交换机处理。

### 常见误区

* 说“交换机根据 IP 地址转发”。普通二层交换机根据 MAC 地址转发。
* 说“MAC 地址就是 IP 地址”。二者完全不同，属于不同层级。
* 把 frame 和 packet 混用。Layer 2 是 frame，Layer 3 是 packet。

### 主动回忆

1. 交换机主要工作在 OSI 哪一层？
2. IP 地址属于 Layer 2 还是 Layer 3？
3. Ethernet 的 Layer 2 部分主要研究什么？

---

## [3:04] Local Area Networks (LANs)

### 先建立直觉

LAN 可以先理解为“同一个本地二层网络范围”。交换机可以把这个范围扩大，但路由器接口通常会把不同 LAN 分开。

Jeremy 在这里用图说明：判断 LAN 数量时，不是看有几台交换机，而是看是否被路由器接口分隔。

### 详细讲解

局域网（Local Area Network, LAN）是一个相对小范围的网络，比如：

* 家庭网络
* 办公室一层楼
* 小型公司内部网络

本节给出的关键规则：

```text
Switches expand LANs.
Routers separate LANs.
```

也就是：

* 交换机用于扩展 LAN。
* 路由器用于连接不同 LAN。

#### 示例 1：一个交换机连接多台 PC 和一个路由器接口

```text
PC1 ----\
PC2 ----- SW1 ----- R1 G0/0
PC3 ----/
```

这是一 个 LAN。

原因：

* PC1、PC2、PC3 在同一台交换机上。
* 它们连接到同一个路由器接口。
* 中间没有另一个路由器接口把它们隔开。

#### 示例 2：两个交换机互连

```text
PC1 ---- SW1 ---- SW2 ---- PC3
PC2 ----/          \------ PC4
              |
            R1 G0/0
```

这仍然可以是一个 LAN。

原因：

* SW1 和 SW2 只是扩展同一个二层网络。
* 交换机本身不分隔 LAN。

#### 示例 3：两个交换机分别连接不同路由器接口

```text
PC1 ---- SW1 ---- R1 G0/0

PC2 ---- SW2 ---- R1 G0/1
```

这是两个 LAN。

原因：

* SW1 这边连接到 R1 的一个接口。
* SW2 这边连接到 R1 的另一个接口。
* 不同路由器接口通常代表不同三层网络，也就是不同 LAN。

### 配置或示例（如适用）

本章没有配置命令。

但理解时可以用下面的边界判断法：

```text
看到交换机：通常是在扩展 LAN
看到路由器接口：通常是在分隔 LAN
```

### 必须掌握

* LAN 是相对小范围的本地网络。
* 交换机不会天然分隔 LAN。
* 路由器接口通常分隔 LAN。
* 本视频只讨论同一个 LAN 内的通信，不讨论不同 LAN 之间的路由。

### 常见误区

* 误区 1：一个交换机就是一个 LAN。

  * 错。多个交换机互连也可以属于同一个 LAN。
* 误区 2：交换机越多，LAN 越多。

  * 错。交换机通常扩展二层范围。
* 误区 3：两个不同路由器接口下的主机仍是一个 LAN。

  * 通常错。它们通常属于不同 LAN。

### 主动回忆

1. 两台交换机直接相连时，一定是两个 LAN 吗？
2. 为什么路由器接口通常被看作 LAN 边界？
3. 判断 LAN 数量时，应该优先观察交换机数量还是路由器接口？

---

## [4:46] OSI Model PDUs review

### 先建立直觉

数据在网络中传输时，每一层都会给它加上本层需要的信息。这个过程叫封装（encapsulation）。

每一层封装后的数据都有自己的名字，这些名字叫协议数据单元（Protocol Data Units, PDUs）。

### 详细讲解

封装过程如下：

```text
Upper-layer data
    ↓
Layer 4 header + data = Segment
    ↓
Layer 3 header + segment = Packet
    ↓
Layer 2 header + packet + Layer 2 trailer = Frame
```

对应关系：

| OSI 层  | PDU 名称 |
| ------- | -------- |
| 上层    | Data     |
| Layer 4 | Segment  |
| Layer 3 | Packet   |
| Layer 2 | Frame    |

Day 5 关注的是 Layer 2 PDU，也就是 frame。

更准确地说，本节研究的是 Ethernet frame，因为 Ethernet 是现代 LAN 中几乎 everywhere 使用的 Layer 2 协议。

### 配置或示例（如适用）

无配置命令。

可以用寄快递来类比：

```text
原始内容 = data
装进快递袋并写运输信息 = segment / packet / frame
最后交给运输系统 = physical transmission
```

Layer 2 frame 的 header 和 trailer 是为了让本地链路上的设备知道：

* 这个 frame 发给谁？
* 这个 frame 来自谁？
* 里面封装的是什么上层协议？
* 传输过程中有没有损坏？

### 必须掌握

* Layer 2 PDU 是 frame。
* Layer 3 PDU 是 packet。
* Layer 4 PDU 是 segment。
* Ethernet switching 处理的是 frame。

### 常见误区

* 把 packet 和 frame 当成同一个东西。

  * Packet 是 Layer 3。
  * Frame 是 Layer 2。
* 认为交换机直接处理 Layer 4 segment。

  * 普通二层交换机主要处理 Layer 2 frame。

### 主动回忆

1. Layer 2 的 PDU 叫什么？
2. Packet 是哪一层的 PDU？
3. Ethernet switching 主要处理 packet 还是 frame？

---

## [5:48] Ethernet Frame

### 先建立直觉

交换机要转发 frame，就必须能读懂 Ethernet frame 的格式。

Ethernet frame 就像一个本地投递信封：

* 前面写目的地址。
* 前面也写来源地址。
* 中间放真正要传的数据。
* 后面附一个校验信息，检查运输过程中有没有坏。

### 详细讲解

视频中介绍的 Ethernet frame 字段如下：

```text
Ethernet Header                                      Ethernet Trailer
+----------+-----+-----------------+------------+-------------+-----+
| Preamble | SFD | Destination MAC | Source MAC | Type/Length | FCS |
+----------+-----+-----------------+------------+-------------+-----+
```

Header 中有 5 个字段：

1. Preamble
2. SFD
3. Destination
4. Source
5. Type/Length

Trailer 中有 1 个字段：

1. FCS

#### Preamble 与 SFD

Preamble 和 SFD 主要帮助接收端准备接收 frame。

* Preamble：同步接收端时钟。
* SFD：告诉接收端 preamble 结束，真正 frame 内容开始。

#### Destination MAC

目标 MAC 地址，表示 frame 要发给哪个二层设备。

#### Source MAC

源 MAC 地址，表示 frame 是哪个二层设备发出的。

#### Type/Length

表示：

* 被封装的 Layer 3 packet 类型，例如 IPv4 或 IPv6。
* 或者在某些 Ethernet 版本中表示被封装数据长度。

#### FCS

帧校验序列（Frame Check Sequence, FCS）用于检测传输错误。

### 配置或示例（如适用）

无 Cisco IOS 配置命令。

示例 frame：

```text
Destination MAC: AAAA.AA00.0002
Source MAC:      AAAA.AA00.0001
Type:            0x0800
Payload:         IPv4 packet
FCS:             CRC value
```

含义：

* 这是从 `AAAA.AA00.0001` 发往 `AAAA.AA00.0002` 的 Ethernet frame。
* `0x0800` 表示里面封装的是 IPv4 packet。
* FCS 用于让接收端判断 frame 是否在传输中损坏。

### 必须掌握

* Ethernet frame 有 header 和 trailer。
* Destination MAC 和 Source MAC 都是 6 bytes。
* Type/Length 是 2 bytes。
* FCS 是 trailer，长度 4 bytes。
* 本视频最重要的字段是 Source MAC 和 Destination MAC。

### 常见误区

* 以为 FCS 在 header 中。FCS 是 trailer。
* 以为 Type 字段总是表示类型。它也可能作为 Length 字段，取决于值和 Ethernet 版本。
* 以为交换机学习 Destination MAC。交换机学习 Source MAC。

### 主动回忆

1. Ethernet trailer 中唯一字段是什么？
2. 交换机用哪个字段学习 MAC 地址表？
3. Destination MAC 和 Source MAC 各有多长？

---

## [7:23] Ethernet Frame - Preamble & SFD

### 先建立直觉

Preamble 和 SFD 可以理解成接收 frame 前的“敲门声”和“正式开始信号”。

设备在高速接收 bit 流时，需要知道什么时候开始同步、什么时候真正进入 frame 内容。Preamble 和 SFD 就是为这个目的服务。

### 详细讲解

#### Preamble

前导码（Preamble）长度为：

```text
7 bytes = 56 bits
```

内容是重复的 1 和 0：

```text
10101010 10101010 10101010 10101010 10101010 10101010 10101010
```

作用：

* 让接收设备同步接收时钟（receiver clock synchronization）。
* 让接收设备准备好接收后续 frame 内容。

Quiz 1 就考这个点：提供 receiver clock synchronization 的字段是 Preamble，不是 SFD。

#### SFD

帧起始定界符（Start Frame Delimiter, SFD）长度为：

```text
1 byte = 8 bits
```

bit pattern 是：

```text
10101011
```

它和 Preamble 很像，但最后一位从 `0` 变成 `1`。

作用：

* 表示 Preamble 结束。
* 表示真正的 frame 内容即将开始。

### 配置或示例（如适用）

无配置命令。

对比：

```text
Preamble: 10101010 repeated 7 times
SFD:      10101011
```

记忆方法：

* Preamble：负责同步。
* SFD：负责分界。

### 必须掌握

* Preamble 长度 7 bytes。
* SFD 长度 1 byte。
* Preamble 用于 receiver clock synchronization。
* SFD 表示 preamble 结束、frame 开始。

### 常见误区

* 把 SFD 误认为同步字段。

  * SFD 不是同步时钟的主要字段，Preamble 才是。
* 忘记 Preamble 是 7 bytes，不是 8 bytes。

  * Preamble 7 bytes + SFD 1 byte，合起来常让人误记成 Preamble 8 bytes。

### 主动回忆

1. Preamble 的 bit pattern 是什么？
2. SFD 与 Preamble 的最后一位有什么不同？
3. 哪个字段用于 receiver clock synchronization？

---

## [8:36] Ethernet Frame - Destination & Source

### 先建立直觉

在一个 Ethernet frame 中，Destination MAC 和 Source MAC 就像信封上的收件人地址和寄件人地址。

交换机收到 frame 后，会同时关心这两个字段，但用途不同：

* Source MAC：用来学习“谁从哪个端口来”。
* Destination MAC：用来决定“这个 frame 应该往哪里发”。

### 详细讲解

Destination 和 Source 字段使用的地址是 MAC 地址（MAC address）。

MAC 全称是 Media Access Control。

MAC 地址特点：

```text
长度：6 bytes = 48 bits
```

它是物理设备地址，通常在设备制造时分配。

这和 IP 地址不同：

* MAC 地址：Layer 2 address，通常随网卡或接口而来。
* IP 地址：Layer 3 address，通常由管理员配置、DHCP 分配，或者系统自动生成。

注意，后续在真实网络中，MAC 地址并不等于“整台设备唯一身份”的所有情况，因为一台设备可以有多个网卡接口，每个接口有自己的 MAC 地址。但本视频的重点是：Ethernet frame 的源与目的二层地址是 MAC 地址。

### 配置或示例（如适用）

无配置命令。

例子：

```text
PC1 MAC: AAAA.AA00.0001
PC2 MAC: AAAA.AA00.0002

PC1 → PC2 的 frame:
Destination MAC = AAAA.AA00.0002
Source MAC      = AAAA.AA00.0001
```

PC2 回复 PC1 时，地址反过来：

```text
PC2 → PC1 的 frame:
Destination MAC = AAAA.AA00.0001
Source MAC      = AAAA.AA00.0002
```

### 必须掌握

* Destination MAC 是目标二层地址。
* Source MAC 是源二层地址。
* MAC 地址长度是 6 bytes / 48 bits。
* MAC 地址与 IP 地址不同，分别属于 Layer 2 和 Layer 3。

### 常见误区

* 以为 MAC 地址是 32 bits。

  * IPv4 地址是 32 bits，MAC 地址是 48 bits。
* 以为交换机根据 Source MAC 转发。

  * 交换机根据 Source MAC 学习，根据 Destination MAC 转发。
* 以为 Destination MAC 是最终 Internet 服务器的 MAC。

  * 在跨网络通信中，二层目的 MAC 通常是下一跳设备的 MAC，这部分后续课程会讲。本视频只讨论同一 LAN 内。

### 主动回忆

1. MAC 地址是几 bytes？几 bits？
2. Source MAC 和 Destination MAC 分别表示什么？
3. MAC 地址和 IP 地址分别属于 OSI 哪一层？

---

## [9:31] Ethernet Frame - Type/Length

### 先建立直觉

Type/Length 字段告诉接收设备：“我里面装的是什么”或者“我里面装了多长”。

这个字段只有 2 bytes，但非常重要，因为接收端需要知道如何把 frame 里面的内容交给上层协议处理。

### 详细讲解

Type/Length 字段长度：

```text
2 bytes = 16 bits
```

它可能表示两种含义：

1. Length：被封装数据的长度。
2. Type：被封装的 Layer 3 协议类型。

判断规则：

```text
值 <= 1500        → 表示 Length
值 >= 1536        → 表示 Type
1501 到 1535      → 中间保留范围，本视频未展开
```

#### 表示 Length

如果字段值是 `1400`，并且这个值小于等于 1500，那么表示里面封装的数据长度是 1400 bytes。

#### 表示 Type

如果字段值是 1536 或更大，则表示上层协议类型。

常见 EtherType：

```text
0x0800 = IPv4
0x86DD = IPv6
```

其中 `0x` 表示后面的数字是十六进制。

视频中给出：

```text
0x0800 = decimal 2048
0x86DD = decimal 34525
```

因为它们都大于 1536，所以表示 Type，而不是 Length。

### 配置或示例（如适用）

无配置命令。

示例：

```text
Type/Length = 0x0800
```

解释：

* `0x0800` 是十六进制。
* 换算成十进制是 2048。
* 2048 大于 1536。
* 所以它表示 Type。
* 该 Type 表示 payload 是 IPv4 packet。

另一个示例：

```text
Type/Length = 1400
```

解释：

* 1400 小于等于 1500。
* 所以它表示 Length。
* 表示被封装的数据长度是 1400 bytes。

### 必须掌握

* Type/Length 字段长度是 2 bytes。
* `<=1500` 表示 Length。
* `>=1536` 表示 Type。
* `0x0800` 表示 IPv4。
* `0x86DD` 表示 IPv6。

### 常见误区

* 看到 Type/Length 就默认永远是 Type。
* 忘记十六进制前缀 `0x`。
* 不知道 `0x0800` 虽然看起来像 800，但实际十进制是 2048。
* 把 1500 和 1536 的界线记反。

### 主动回忆

1. Type/Length 字段有多长？
2. 如果 Type/Length 的值是 1400，它表示 Type 还是 Length？
3. `0x0800` 表示什么协议？

---

## [11:47] Ethernet Frame - FCS

### 先建立直觉

网络传输过程中，bit 可能因为干扰、线缆问题、硬件问题而出错。

FCS 就像 frame 末尾附带的“校验码”。接收设备收到 frame 后，会根据收到的数据重新计算，然后和 FCS 对比。如果不一致，就说明 frame 可能坏了。

### 详细讲解

帧校验序列（Frame Check Sequence, FCS）是 Ethernet trailer 中唯一字段。

长度：

```text
4 bytes = 32 bits
```

作用：

* 检测传输过程中是否发生错误。
* 使用 CRC 算法。

CRC 全称：

```text
Cyclic Redundancy Check
```

中文可理解为循环冗余校验。

视频中没有要求深入掌握 CRC 算法细节。CCNA 层面重点是：

```text
Ethernet FCS uses CRC to detect errors.
```

FCS 只能检测错误，不负责决定 frame 应该发到哪个端口。交换机转发逻辑仍然依赖 MAC 地址表和 destination MAC。

### 配置或示例（如适用）

无配置命令。

可以这样理解：

```text
发送端：
原始 frame 内容 → CRC 算法 → 得到 FCS → 放到 frame 末尾

接收端：
收到 frame 内容 → 重新 CRC 计算 → 和 FCS 对比
一致：认为 frame 未检测到错误
不一致：认为 frame 损坏，丢弃
```

### 必须掌握

* FCS 是 Ethernet trailer。
* FCS 长度 4 bytes。
* FCS 使用 CRC。
* FCS 用于错误检测。

### 常见误区

* 认为 FCS 用于纠错。

  * 本视频强调的是 detect errors。不要把它理解成一定能修复错误。
* 认为 FCS 用于 MAC 学习。

  * MAC 学习使用 Source MAC。
* 认为 FCS 在 header 中。

  * FCS 是 trailer。

### 主动回忆

1. FCS 长度是多少？
2. FCS 使用什么算法？
3. FCS 的主要作用是转发、学习还是错误检测？

---

## [13:52] MAC Addresses

### 先建立直觉

MAC 地址是 Ethernet 二层通信的核心地址。交换机不需要先看 IP 就能在 LAN 内转发 frame，因为它根据 MAC 地址表工作。

MAC 地址就像网卡的“二层身份标签”。

### 详细讲解

MAC 地址（MAC address）：

```text
长度：6 bytes = 48 bits
格式：12 个十六进制字符
```

例如：

```text
E8BA.7011.2874
AAAA.AA00.0001
```

它通常在设备制造时分配，因此也叫：

```text
Burned-In Address, BIA
```

也就是烧录地址。

#### MAC 地址和 IP 地址的区别

| 项目     | MAC 地址            | IP 地址              |
| -------- | ------------------- | -------------------- |
| OSI 层级 | Layer 2             | Layer 3              |
| 常见长度 | 48 bits             | IPv4 是 32 bits      |
| 作用范围 | 本地链路 / LAN 转发 | 跨网络寻址           |
| 分配方式 | 通常制造时分配      | 管理员配置 / DHCP 等 |

#### 全局唯一与本地唯一

视频中提到，大多数情况下 MAC 地址是 globally unique，也就是全球唯一。

也存在 locally-unique MAC address，本视频没有展开。CCNA 初学阶段可以先记住：一般情况下，MAC 地址应当全球唯一。

#### OUI

组织唯一标识符（Organizationally Unique Identifier, OUI）是 MAC 地址的前 3 bytes，也就是前 24 bits。

例如：

```text
MAC: E8BA.7011.2874
OUI: E8BA.70
```

为什么是 `E8BA.70`？

因为 Cisco 格式每 4 个十六进制字符用点分隔：

```text
E8BA.7011.2874
```

每 2 个十六进制字符 = 1 byte。

拆成 bytes：

```text
E8 BA 70 11 28 74
```

前 3 bytes 是：

```text
E8 BA 70
```

写成 Cisco 点分格式就是：

```text
E8BA.70
```

后 3 bytes 用于标识具体设备：

```text
11 28 74
```

写成：

```text
11.2874
```

但常见考试只问 OUI，要快速取前 24 bits。

### 配置或示例（如适用）

无配置命令。

MAC 地址拆分示例：

```text
MAC address: E8BA.7011.2874

按 byte 拆：
E8 | BA | 70 | 11 | 28 | 74

前 3 bytes:
E8 | BA | 70

OUI:
E8BA.70
```

### 必须掌握

* MAC 地址长度是 48 bits。
* MAC 地址也可叫 BIA。
* MAC 地址通常写作 12 个十六进制字符。
* OUI 是前 24 bits / 前 3 bytes。
* 后 24 bits 标识具体设备。

### 常见误区

* 把 OUI 取成前 4 个十六进制字符。

  * 错。前 4 个十六进制字符只有 2 bytes，不够 24 bits。
* 把 `E8BA.7011` 当成 OUI。

  * 错。这是 4 bytes，不是 3 bytes。
* 认为 MAC 地址是管理员在 CLI 中配置的。

  * 通常 MAC 是制造时分配；IP 才是常见 CLI 配置对象。

### 主动回忆

1. MAC 地址的前 3 bytes 叫什么？
2. `E8BA.7011.2874` 的 OUI 是什么？
3. BIA 指的是什么？

---

## [15:24] Decimal number system

### 先建立直觉

为了理解 MAC 地址，必须先理解十六进制（hexadecimal）。但 Jeremy 先从十进制（decimal）讲起，因为我们日常使用的是十进制。

十进制的本质是“逢十进一”。

### 详细讲解

十进制数字系统（Decimal number system）使用 10 个数字：

```text
0 1 2 3 4 5 6 7 8 9
```

每一列的权重从右到左依次是：

```text
1s, 10s, 100s, 1000s ...
```

例如：

```text
9 = 9 个 1
10 = 1 个 10 + 0 个 1
11 = 1 个 10 + 1 个 1
20 = 2 个 10 + 0 个 1
100 = 1 个 100 + 0 个 10 + 0 个 1
```

为什么要讲这个？

因为十六进制也是类似的位权系统，只是它不是逢十进一，而是逢十六进一。

### 配置或示例（如适用）

无配置命令。

位权示例：

```text
十进制 347

= 3 × 100
+ 4 × 10
+ 7 × 1
```

### 必须掌握

* 十进制有 10 个数字。
* 十进制每一列是 10 的幂。
* 理解十进制是为了过渡到十六进制。

### 常见误区

* 觉得十六进制只是“多了 A-F 的奇怪写法”，没有理解位权。
* 不知道 `10` 在不同进制中含义不同。

  * 十进制 `10` 表示十。
  * 十六进制 `10` 表示十六。

### 主动回忆

1. 十进制为什么叫 decimal？
2. 十进制 `100` 中每一位分别代表什么？
3. 为什么学习 MAC 地址前要理解十六进制？

---

## [17:26] Hexadecimal number system

### 先建立直觉

十六进制（Hexadecimal）是网络学习中非常常见的数字系统，尤其用于 MAC 地址和 IPv6 地址。

十六进制的本质是“逢十六进一”。

### 详细讲解

十六进制使用 16 个符号：

```text
0 1 2 3 4 5 6 7 8 9 A B C D E F
```

其中：

```text
A = decimal 10
B = decimal 11
C = decimal 12
D = decimal 13
E = decimal 14
F = decimal 15
```

十六进制每一列的权重从右到左依次是：

```text
1s, 16s, 256s, 4096s ...
```

所以：

```text
Hex 10 = 1 × 16 + 0 × 1 = Decimal 16
Hex 11 = 1 × 16 + 1 × 1 = Decimal 17
Hex 12 = Decimal 18
Hex 13 = Decimal 19
Hex 14 = Decimal 20
Hex 15 = Decimal 21
Hex 16 = Decimal 22
Hex 17 = Decimal 23
Hex 18 = Decimal 24
Hex 19 = Decimal 25
Hex 1A = Decimal 26
Hex 1B = Decimal 27
Hex 1C = Decimal 28
```

#### 为什么 MAC 地址适合用十六进制？

因为 MAC 地址是 48 bits。如果用二进制写会很长：

```text
111010001011101001110000000100010010100001110100
```

用十六进制可以大幅缩短：

```text
E8BA.7011.2874
```

每 1 个十六进制字符正好代表 4 bits。

所以：

```text
12 hex digits × 4 bits = 48 bits
```

这正好等于 MAC 地址长度。

### 配置或示例（如适用）

无配置命令。

快速换算示例：

```text
Hex 0x0800

= 8 × 16^2
= 8 × 256
= 2048 decimal
```

所以 `0x0800` 大于 1536，表示 EtherType，并且代表 IPv4。

### 必须掌握

* 十六进制有 16 个符号。
* A-F 分别代表 10-15。
* Hex `10` 等于 decimal 16，不是 decimal 10。
* 1 个 hex digit = 4 bits。
* 12 个 hex digits = 48 bits，正好表示一个 MAC 地址。

### 常见误区

* 把 hex `10` 读成 decimal 10。
* 不知道 A-F 是数字，不是字母含义。
* 不知道 MAC 地址为什么是 12 个 hex 字符。

### 主动回忆

1. 十六进制 F 等于十进制多少？
2. 十六进制 `10` 等于十进制多少？
3. 为什么 12 个十六进制字符可以表示 48-bit MAC 地址？

---

## [19:44] MAC Addresses continued

### 先建立直觉

现在把 MAC 地址放回实际交换网络中看。每台 PC 的网卡有 MAC 地址，交换机通过观察 frame 中的 MAC 地址来学习和转发。

### 详细讲解

视频中的简化网络：

```text
          SW1
       /   |   \
    F0/1  F0/2  F0/3
     |     |     |
    PC1   PC2   PC3
```

接口名称：

```text
F0/1, F0/2, F0/3
```

其中 `F` 表示 FastEthernet，速率是 100 Mbps。

示例 MAC：

```text
PC1: AAAA.AA00.0001
PC2: AAAA.AA00.0002
PC3: AAAA.AA00.0003
```

这些 MAC 地址是为了教学简化。真实 MAC 地址通常不会这么整齐。

Cisco 常见 MAC 写法是每 4 个十六进制字符加一个点：

```text
AAAA.AA00.0001
```

也可能看到每 2 个字符加分隔符的写法：

```text
AA:AA:AA:00:00:01
AA-AA-AA-00-00-01
AA.AA.AA.00.00.01
```

不同格式表示的是同一个 48-bit 地址。

对于：

```text
AAAA.AA00.0001
```

拆成 6 bytes：

```text
AA AA AA 00 00 01
```

OUI 是前 3 bytes：

```text
AA AA AA
```

Cisco 点分格式写作：

```text
AAAA.AA
```

后 3 bytes：

```text
00 00 01
```

表示具体设备编号。

### 配置或示例（如适用）

无配置命令。

示例：

```text
PC1 sends to PC2

Destination MAC: AAAA.AA00.0002
Source MAC:      AAAA.AA00.0001
```

这就是一个从 PC1 发往 PC2 的单播 frame。

### 必须掌握

* `F0/1` 中 F 表示 FastEthernet。
* FastEthernet 是 100 Mbps。
* MAC 地址可以用 Cisco 点分格式表示。
* OUI 是 MAC 地址前半部分，即前 3 bytes。

### 常见误区

* 看到 `AAAA.AA00.0001` 不知道如何拆成 6 bytes。
* 误以为点号决定 OUI。实际上 OUI 是前 24 bits，不是“第一个点前面的全部”。
* 把 FastEthernet 和 GigabitEthernet 混淆。

### 主动回忆

1. `F0/1` 中的 F 代表什么？
2. Cisco 常见 MAC 地址写法是什么样？
3. `AAAA.AA00.0001` 的前 3 bytes 是什么？

---

## [21:00] Unicast frames

### 先建立直觉

单播帧（Unicast frame）就是发给一个明确目标设备的 Ethernet frame。

它不是“发给所有人”，也不是“发给一组人”，而是“发给某一个 MAC 地址”。

### 详细讲解

当 PC1 要发送数据给 PC2：

```text
PC1 MAC: AAAA.AA00.0001
PC2 MAC: AAAA.AA00.0002
```

PC1 发出的 frame 是：

```text
Destination MAC: AAAA.AA00.0002
Source MAC:      AAAA.AA00.0001
```

这个 frame 是 unicast frame，因为 destination 是一个单一目标。

视频中提到后面还会学习其他类型，例如 broadcast frame，但 Day 5 暂时只重点讲 unicast。

### 配置或示例（如适用）

无配置命令。

拓扑：

```text
PC1 ---- F0/1
PC2 ---- F0/2
PC3 ---- F0/3
          SW1
```

PC1 发给 PC2：

```text
src = PC1 MAC
dst = PC2 MAC
```

### 必须掌握

* Unicast frame 是发往单个目标 MAC 的 frame。
* Source MAC 是发送者。
* Destination MAC 是接收者。
* 交换机会根据 destination MAC 判断如何转发。

### 常见误区

* 误以为只要交换机 flooding 了，这个 frame 就变成 broadcast。

  * 错。Frame 的 destination MAC 仍然是某个单播 MAC，只是交换机不知道在哪，所以泛洪。
* 把 unknown unicast 和 broadcast 混为一谈。

  * unknown unicast 的目标仍是单个 MAC，只是交换机表里没有。

### 主动回忆

1. 什么是 unicast frame？
2. PC1 发给 PC2 时，source MAC 是谁？
3. Unknown unicast 是不是 broadcast？

---

## [21:40] MAC Address Table / Dynamic MAC Addresses

### 先建立直觉

交换机刚启动时，通常不知道每个 MAC 地址在哪个端口。它不是靠手动提前写好所有主机位置，而是通过收到的 frame 自动学习。

学习规则非常重要：

```text
Switch learns from Source MAC.
```

交换机从 Source MAC 学习，而不是从 Destination MAC 学习。

### 详细讲解

当 SW1 收到 PC1 发来的 frame：

```text
Destination MAC: AAAA.AA00.0002
Source MAC:      AAAA.AA00.0001
Received on:     F0/1
```

SW1 会查看 Source MAC：

```text
AAAA.AA00.0001
```

然后把它加入 MAC 地址表：

```text
MAC Address       Interface
AAAA.AA00.0001    F0/1
```

含义：

```text
如果以后我要发往 AAAA.AA00.0001，可以从 F0/1 发出去。
```

这叫动态学习 MAC 地址（dynamically learned MAC address），也叫动态 MAC 地址（dynamic MAC address）。

为什么叫动态？

因为它不是管理员手动配置的，而是交换机根据收到的 frame 自己学习的。

### 配置或示例（如适用）

本视频没有演示 IOS 命令，但实际 Cisco 交换机上常用这个命令查看 MAC 地址表：

```text
show mac address-table
```

逐行解释：

```text
show
```

表示查看设备当前状态或信息，不改变配置。

```text
mac address-table
```

表示查看交换机的 MAC 地址表，也就是 MAC 地址与接口的对应关系。

可能看到类似输出：

```text
          Mac Address Table
-------------------------------------------
Vlan    Mac Address       Type        Ports
----    -----------       --------    -----
   1    aaaa.aa00.0001    DYNAMIC     Fa0/1
```

解释：

* `Vlan 1`：该 MAC 地址属于 VLAN 1。
* `aaaa.aa00.0001`：学习到的 MAC 地址。
* `DYNAMIC`：动态学习，不是静态配置。
* `Fa0/1`：从这个端口可以到达该 MAC。

注意：视频本身没有展示该命令，这里是结合 CCNA 常见验证方式补充，便于你实际验证。

### 必须掌握

* 交换机通过 Source MAC 学习 MAC 地址表。
* MAC 表项记录的是 MAC 地址与入接口的对应关系。
* 动态 MAC 地址是交换机自动学习的。
* MAC 地址表的接口不一定表示设备直连，只表示“从这个接口出去能到达该 MAC”。

### 常见误区

* 认为交换机从 Destination MAC 学习。

  * 错。Destination MAC 是用来查表转发的。
* 认为 MAC 地址表中接口一定连接着那台终端。

  * 不一定。如果中间还有交换机，这个接口可能只是通往目标的方向。
* 认为交换机一开始就知道所有 MAC。

  * 错。它需要通过流量学习。

### 主动回忆

1. 交换机使用 Ethernet frame 中哪个字段学习 MAC 地址？
2. Dynamic MAC address 为什么叫 dynamic？
3. MAC 地址表里的 interface 字段一定表示终端直连吗？

---

## [22:58] Unknown Unicast / Flooding

### 先建立直觉

交换机收到一个单播 frame 后，如果不知道目标 MAC 地址在哪个端口，它不能直接丢弃，因为目标可能就在某个端口后面。

所以它会采取“问全场”的方式：除了收到这个 frame 的端口之外，其他端口都发一份。

这叫泛洪（flooding）。

### 详细讲解

场景：

```text
PC1 ---- F0/1
PC2 ---- F0/2
PC3 ---- F0/3
          SW1
```

MAC：

```text
PC1: AAAA.AA00.0001
PC2: AAAA.AA00.0002
PC3: AAAA.AA00.0003
```

PC1 发给 PC2：

```text
Destination MAC: AAAA.AA00.0002
Source MAC:      AAAA.AA00.0001
```

SW1 收到 frame 的动作：

#### 第一步：学习 Source MAC

收到端口是 F0/1，所以 SW1 学到：

```text
MAC Address       Interface
AAAA.AA00.0001    F0/1
```

#### 第二步：查 Destination MAC

SW1 查找：

```text
AAAA.AA00.0002
```

如果 MAC 地址表没有这个条目，这个 frame 就叫未知单播帧（unknown unicast frame）。

#### 第三步：Flooding

SW1 会把 frame 从所有其他端口发出：

```text
收到端口：F0/1
泛洪端口：F0/2, F0/3
不发回：F0/1
```

为什么不从 F0/1 发回去？

因为 frame 就是从 F0/1 进来的，发回去没有意义，还可能造成重复或环路风险。

#### 第四步：终端处理

* PC2 的 MAC 与 destination MAC 匹配，所以接收并处理。
* PC3 的 MAC 不匹配，所以丢弃。

注意：

PC2 收到 PC1 的 frame 后，如果没有回复，SW1 仍然学不到 PC2 的 MAC，因为交换机只能从收到的 frame 的 Source MAC 学习。PC2 不发 frame，SW1 就没有机会学习 PC2。

### 配置或示例（如适用）

本视频没有配置命令。

实际验证可用：

```text
show mac address-table
```

逐行说明同上一节。

如果你在 Packet Tracer 或真实交换机中清空 MAC 表，也可用：

```text
clear mac address-table dynamic
```

逐行解释：

```text
clear
```

清除某类运行状态信息。

```text
mac address-table
```

指定清除 MAC 地址表相关信息。

```text
dynamic
```

只清除动态学习到的 MAC 地址，不清除静态配置的 MAC 表项。

注意：这个命令是实际 CCNA 常见命令，本视频没有演示，属于验证和实验时可用的补充。

### 必须掌握

* Unknown unicast 是目标 MAC 不在交换机 MAC 地址表中的单播 frame。
* Unknown unicast 会被 flooding。
* Flooding 是从除入接口以外的所有接口发出。
* 终端收到不属于自己的 unicast frame 会丢弃。

### 常见误区

* 认为 unknown unicast 会被丢弃。

  * 错。交换机会 flooding。
* 认为 flooding 包括收到 frame 的端口。

  * 错。不从入接口发回。
* 认为 PC2 收到 frame 后，交换机就自动学到 PC2。

  * 错。只有 PC2 发送 frame，交换机才能从 source MAC 学到它。

### 主动回忆

1. 什么是 unknown unicast frame？
2. 交换机对 unknown unicast 做什么？
3. 为什么 PC3 收到 PC1 发给 PC2 的 frame 后会丢弃？

---

## [25:22] Known Unicast / Forwarding

### 先建立直觉

当交换机已经知道目标 MAC 地址在哪个端口时，就不需要“问全场”了。它只把 frame 发到目标所在方向。

这叫转发（forwarding）。

### 详细讲解

继续上一节。

现在 PC2 回复 PC1：

```text
Destination MAC: AAAA.AA00.0001
Source MAC:      AAAA.AA00.0002
```

SW1 收到 PC2 的 frame：

```text
Received on: F0/2
```

#### 第一步：学习 PC2 的 Source MAC

SW1 学到：

```text
MAC Address       Interface
AAAA.AA00.0002    F0/2
```

此时 MAC 表可能是：

```text
MAC Address       Interface
AAAA.AA00.0001    F0/1
AAAA.AA00.0002    F0/2
```

#### 第二步：查 Destination MAC

目的 MAC 是：

```text
AAAA.AA00.0001
```

SW1 已经知道它在 F0/1。

所以这个 frame 是已知单播帧（known unicast frame）。

#### 第三步：Forwarding

SW1 只把 frame 从 F0/1 发出去，不会发给 F0/3。

这就是 forwarding。

#### 动态 MAC 地址老化

Cisco 交换机上，动态 MAC 地址默认在 5 分钟无活动后从 MAC 地址表删除。

也就是说，如果 PC1 超过 5 分钟没有任何流量，SW1 会删除：

```text
AAAA.AA00.0001    F0/1
```

如果 PC1 后来再次发 frame，SW1 会重新学习。

### 配置或示例（如适用）

实际验证命令：

```text
show mac address-table
```

常见输出：

```text
Vlan    Mac Address       Type        Ports
----    -----------       --------    -----
   1    aaaa.aa00.0001    DYNAMIC     Fa0/1
   1    aaaa.aa00.0002    DYNAMIC     Fa0/2
```

解释：

* 如果目标是 `aaaa.aa00.0001`，交换机从 `Fa0/1` 转发。
* 如果目标是 `aaaa.aa00.0002`，交换机从 `Fa0/2` 转发。
* 不需要 flooding 给所有端口。

查看 MAC 地址老化时间的常见命令：

```text
show mac address-table aging-time
```

逐行解释：

```text
show
```

查看当前状态。

```text
mac address-table
```

查看 MAC 地址表相关信息。

```text
aging-time
```

查看动态 MAC 地址老化时间。

注意：视频中只讲到 Cisco 默认 5 分钟无活动后删除动态 MAC，没有演示该命令。这里作为验证补充。

### 必须掌握

* Known unicast 是目标 MAC 已经在 MAC 地址表中的单播 frame。
* Known unicast 会被 forwarding，而不是 flooding。
* Forwarding 是只从对应接口发出。
* Cisco 动态 MAC 地址默认 5 分钟无活动后老化。

### 常见误区

* 把 known unicast 和 unknown unicast 的处理方式记反。
* 认为动态 MAC 表项永久存在。
* 以为交换机收到 PC2 回复后不会更新 MAC 表。

  * 它会根据 PC2 的 Source MAC 学习 PC2 所在端口。

### 主动回忆

1. 什么是 known unicast frame？
2. known unicast 和 unknown unicast 的处理方式分别是什么？
3. Cisco 动态 MAC 地址默认多久无活动后老化？

---

## [26:22] MAC Learning & Frame Flooding/Forwarding review

### 先建立直觉

现在把网络扩大到两台交换机。关键点是：每台交换机都独立维护自己的 MAC 地址表。

一台交换机学到的 MAC 表，不会自动同步给另一台交换机。另一台交换机也必须通过收到 frame 的 Source MAC 自己学习。

### 详细讲解

拓扑：

```text
PC1 ---- F0/1        F0/1 ---- PC3
PC2 ---- F0/2  SW1--F0/3--SW2  F0/2 ---- PC4
```

更清晰写法：

```text
PC1 --- F0/1       F0/3 --- F0/3       F0/1 --- PC3
          SW1 ---------------- SW2
PC2 --- F0/2                         F0/2 --- PC4
```

假设：

```text
PC1 MAC: AAAA.AA00.0001
PC3 MAC: AAAA.AA00.0003
```

初始：

```text
SW1 MAC table: empty
SW2 MAC table: empty
```

#### PC1 发送给 PC3

Frame：

```text
Destination MAC: AAAA.AA00.0003
Source MAC:      AAAA.AA00.0001
```

#### SW1 收到 frame

入接口：

```text
SW1 F0/1
```

SW1 学习 Source MAC：

```text
SW1 MAC table:
AAAA.AA00.0001    F0/1
```

SW1 查 destination MAC：

```text
AAAA.AA00.0003
```

未知，所以 SW1 flooding：

```text
从 F0/2 和 F0/3 发出
不从 F0/1 发出
```

PC2 收到后发现 destination MAC 不匹配，丢弃。

SW2 从与 SW1 相连的接口收到 frame。

#### SW2 收到 frame

SW2 看到同一个 Source MAC：

```text
Source MAC: AAAA.AA00.0001
```

入接口是连接 SW1 的接口，例如 F0/3。

SW2 学习：

```text
SW2 MAC table:
AAAA.AA00.0001    F0/3
```

注意：这不代表 PC1 直接插在 SW2 F0/3 上。它只代表：

```text
SW2 如果要到达 PC1，应从 F0/3 方向出去。
```

这是一个非常容易错的点。

然后 SW2 查 destination MAC：

```text
AAAA.AA00.0003
```

未知，所以 SW2 flooding：

```text
从 F0/1 和 F0/2 发出
不从 F0/3 发出
```

PC4 收到后丢弃。

PC3 收到后，destination MAC 匹配，处理 frame。

#### PC3 回复 PC1

PC3 发送：

```text
Destination MAC: AAAA.AA00.0001
Source MAC:      AAAA.AA00.0003
```

SW2 收到后先学习 Source MAC：

```text
SW2 MAC table:
AAAA.AA00.0001    F0/3
AAAA.AA00.0003    F0/1
```

然后查 destination MAC：

```text
AAAA.AA00.0001 → F0/3
```

已知，所以 SW2 forwarding 到 F0/3。

SW1 从 F0/3 收到 PC3 回复的 frame。

SW1 学习 Source MAC：

```text
SW1 MAC table:
AAAA.AA00.0001    F0/1
AAAA.AA00.0003    F0/3
```

然后查 destination MAC：

```text
AAAA.AA00.0001 → F0/1
```

已知，所以 SW1 forwarding 到 F0/1，PC1 收到回复。

### 配置或示例（如适用）

实际验证可以在两台交换机分别执行：

```text
show mac address-table
```

逐行解释：

```text
show
```

查看运行状态。

```text
mac address-table
```

显示本交换机自己的 MAC 地址表。

重点：要分别在 SW1 和 SW2 上查看，因为每台交换机的 MAC 地址表不同。

例如 SW1 可能显示：

```text
Vlan    Mac Address       Type        Ports
----    -----------       --------    -----
   1    aaaa.aa00.0001    DYNAMIC     Fa0/1
   1    aaaa.aa00.0003    DYNAMIC     Fa0/3
```

SW2 可能显示：

```text
Vlan    Mac Address       Type        Ports
----    -----------       --------    -----
   1    aaaa.aa00.0001    DYNAMIC     Fa0/3
   1    aaaa.aa00.0003    DYNAMIC     Fa0/1
```

这里最重要的是：

```text
SW2 上 aaaa.aa00.0001 → Fa0/3
```

不表示 PC1 直连 SW2 Fa0/3，只表示从 SW2 看，去 PC1 的方向是 Fa0/3。

### 必须掌握

* 每台交换机独立维护自己的 MAC 地址表。
* 交换机从 Source MAC 学习。
* 查 Destination MAC 决定转发方向。
* Unknown unicast flooding。
* Known unicast forwarding。
* MAC 地址表中的接口表示到达该 MAC 的方向，不一定是直连终端。

### 常见误区

* 认为 SW1 学到 PC1 后，SW2 也自动知道 PC1。

  * 错。SW2 必须收到带 PC1 Source MAC 的 frame 才能学习。
* 认为 MAC 表中的端口永远是终端所在物理端口。

  * 错。可能是通往另一台交换机的上联端口。
* 认为 PC3 收到 PC1 的 frame 后，SW1 立刻知道 PC3。

  * 错。SW1 要等 PC3 发出回复，才能从 Source MAC 学 PC3。

### 主动回忆

1. 两台交换机是否共享同一张 MAC 地址表？
2. SW2 表中 `PC1 MAC → F0/3` 表示 PC1 直接连在 SW2 F0/3 吗？
3. PC3 回复 PC1 时，SW1 会学习哪个 MAC？

---

## 配置与 Lab（如适用）

本视频没有正式 Packet Tracer Lab。视频结尾说明：本主题会有 Packet Tracer lab，但留到 Ethernet LAN Switching Part 2 之后，因此 Day 5 Part 1 没有单独 practice lab。

不过，为了后续实验打基础，可以用以下小拓扑在 Packet Tracer 中自行观察 MAC 学习过程：

```text
PC1 --- Fa0/1
PC2 --- Fa0/2
PC3 --- Fa0/3
          SW1
```

### 推荐观察命令 1：查看 MAC 地址表

```text
show mac address-table
```

逐行解释：

```text
show
```

查看当前设备运行状态。

```text
mac address-table
```

显示交换机的 MAC 地址表，包括 MAC 地址、类型和端口。

典型输出：

```text
Vlan    Mac Address       Type        Ports
----    -----------       --------    -----
   1    aaaa.aa00.0001    DYNAMIC     Fa0/1
   1    aaaa.aa00.0002    DYNAMIC     Fa0/2
```

含义：

* VLAN 1 中，`aaaa.aa00.0001` 可从 `Fa0/1` 到达。
* VLAN 1 中，`aaaa.aa00.0002` 可从 `Fa0/2` 到达。
* `DYNAMIC` 表示这些表项是交换机通过收到 frame 的 Source MAC 自动学习的。

### 推荐观察命令 2：清除动态 MAC 地址表

```text
clear mac address-table dynamic
```

逐行解释：

```text
clear
```

清除某些运行状态信息。

```text
mac address-table
```

指定清除 MAC 地址表。

```text
dynamic
```

只清除动态学习到的 MAC 表项。

使用场景：

* 做实验时想重新观察交换机如何学习 MAC。
* 故障排查时怀疑 MAC 表项异常，需要临时清空动态表项重新学习。

常见错误：

* 清空后立刻查看 MAC 表，可能表是空的。
* 必须让 PC 产生流量，例如 ping，交换机才会重新学习。

### 推荐观察命令 3：查看 MAC 地址老化时间

```text
show mac address-table aging-time
```

逐行解释：

```text
show
```

查看状态。

```text
mac address-table
```

查看 MAC 地址表相关信息。

```text
aging-time
```

查看动态 MAC 地址的老化时间。

本视频知识点：

```text
Cisco switches remove dynamic MAC addresses after 5 minutes of inactivity.
```

也就是默认 300 秒。

### 小型实验流程

1. 清空动态 MAC 表：

```text
clear mac address-table dynamic
```

2. 查看 MAC 表：

```text
show mac address-table
```

此时可能为空，或只剩部分系统/管理相关表项。

3. 从 PC1 ping PC2。
4. 再查看 MAC 表：

```text
show mac address-table
```

你应该能看到 PC1 和 PC2 的 MAC 地址逐步被学习。

注意：ping 本身是 Layer 3/ICMP 行为，但为了发送 ICMP，主机需要产生二层 Ethernet frame，因此交换机会从 frame 的 Source MAC 学习。

---

## 验证与故障排查

### 1. 如何判断交换机是否学到了 MAC？

使用：

```text
show mac address-table
```

重点看：

* MAC 地址是否出现。
* Type 是否为 DYNAMIC。
* Port 是否是预期接口。

例如：

```text
Vlan    Mac Address       Type        Ports
----    -----------       --------    -----
   1    aaaa.aa00.0001    DYNAMIC     Fa0/1
```

说明交换机认为从 `Fa0/1` 可以到达 `aaaa.aa00.0001`。

### 2. 如果 MAC 地址表为空，可能原因是什么？

常见原因：

1. 交换机刚启动，还没收到任何来自主机的 frame。
2. 主机没有发送流量。
3. 接口 down。
4. 线缆或物理层有问题。
5. MAC 表项因为 5 分钟无活动被老化。
6. VLAN 不一致或接口不在同一 VLAN。
   注意：VLAN 是后续课程内容，本视频未展开，这里只是提前提醒故障排查时常见。

### 3. 如何判断 unknown unicast 是否会 flooding？

判断步骤：

```text
Step 1: 收到 frame 后，先学习 Source MAC。
Step 2: 查 Destination MAC 是否在 MAC 地址表。
Step 3: 如果不在 → unknown unicast → flooding。
Step 4: 如果在 → known unicast → forwarding。
```

### 4. Flooding 时哪些端口会发？

规则：

```text
All interfaces except the receiving interface.
```

也就是除入接口之外的所有接口。

例子：

```text
Frame received on Fa0/1
Flood out: Fa0/2, Fa0/3, Fa0/4 ...
Do not flood out: Fa0/1
```

### 5. 为什么终端会丢弃不属于自己的 unicast frame？

因为 frame 的 Destination MAC 不等于自己的 MAC 地址。

例如 PC3 收到：

```text
Destination MAC: AAAA.AA00.0002
PC3 MAC:         AAAA.AA00.0003
```

不匹配，所以 PC3 丢弃该 frame。

### 6. 常见故障思路

如果 PC1 无法与 PC2 通信，可以按层排查：

1. Layer 1：线缆、接口灯、接口状态是否正常。
2. Layer 2：交换机是否学到 PC1/PC2 的 MAC。
3. Layer 2：是否出现错误的 MAC 表项。
4. Layer 3：IP 地址是否正确。
   注意：Day 5 重点是 Layer 2，IP 排查后续课程会更深入。

---

## Quiz 逐题解析

## 第 1 题：Ethernet frame 中哪个字段提供接收端时钟同步？

### 题目还原

Which field of an Ethernet frame provides receiver clock synchronization?

A. Preamble
B. SFD
C. Type
D. FCS

### 正确答案

A. Preamble

### 推理过程

题目问的是：

```text
receiver clock synchronization
```

也就是接收端时钟同步。

Ethernet frame 开头的 Preamble 是 7 bytes，由重复的 `10101010` 组成。它的作用就是让接收设备同步接收时钟，准备好接收后续 frame 内容。

SFD 虽然紧跟在 Preamble 后面，但它的作用不是同步时钟，而是标记 Preamble 结束、真正 frame 内容开始。

所以答案是：

```text
A. Preamble
```

### 各选项解析

#### A. Preamble

正确。

Preamble 是 7 bytes 的交替 1 和 0：

```text
10101010 repeated 7 times
```

它用于 receiver clock synchronization。

#### B. SFD

错误。

SFD 是 Start Frame Delimiter，长度 1 byte，bit pattern 是：

```text
10101011
```

它表示 Preamble 结束和 frame 正文开始，不是主要用于时钟同步。

#### C. Type

错误。

Type 字段用于表示被封装的上层协议类型，例如：

```text
0x0800 = IPv4
0x86DD = IPv6
```

它不用于接收端时钟同步。

#### D. FCS

错误。

FCS 是 Frame Check Sequence，用于错误检测。它通过 CRC 检测 frame 在传输中是否损坏，不用于时钟同步。

### 考点与陷阱

考点：

* Preamble 的作用。
* SFD 与 Preamble 的区别。
* Ethernet frame 字段功能。

常见陷阱：

* 看到 SFD 在 frame 开头，就以为它负责同步。
* 混淆 Preamble 和 SFD：

  * Preamble：同步。
  * SFD：分界。

快速判断方法：

```text
看到 receiver clock synchronization → 选 Preamble
看到 end of preamble / beginning of frame → 选 SFD
看到 error detection → 选 FCS
看到 IPv4/IPv6 type → 选 Type
```

---

## 第 2 题：网络设备的物理地址有多长？

### 题目还原

How long is the physical address of a network device?

A. 32 bytes
B. 32 bits
C. 48 bytes
D. 48 bits

### 正确答案

D. 48 bits

### 推理过程

题目中的 physical address 指的是 MAC address。

MAC 地址是二层物理地址，长度为：

```text
6 bytes = 48 bits
```

因为：

```text
1 byte = 8 bits
6 bytes × 8 = 48 bits
```

所以正确答案是：

```text
D. 48 bits
```

视频还提醒：IPv4 address 是 32 bits，但 MAC address 不是 32 bits。

### 各选项解析

#### A. 32 bytes

错误。

32 bytes 等于：

```text
32 × 8 = 256 bits
```

这不是 MAC 地址长度。

#### B. 32 bits

错误。

32 bits 是 IPv4 地址长度，不是 MAC 地址长度。题目问 physical address，也就是 MAC address。

#### C. 48 bytes

错误。

48 bytes 等于：

```text
48 × 8 = 384 bits
```

MAC 地址是 48 bits，不是 48 bytes。

#### D. 48 bits

正确。

MAC 地址长度是：

```text
48 bits = 6 bytes
```

### 考点与陷阱

考点：

* MAC address 长度。
* byte 与 bit 换算。
* MAC address 与 IPv4 address 长度区分。

常见陷阱：

* 把 IPv4 的 32 bits 误选为 MAC 地址长度。
* 把 bits 和 bytes 混淆。
* 看到 48 就选 48 bytes，而不是 48 bits。

快速判断方法：

```text
MAC = 48 bits = 6 bytes
IPv4 = 32 bits = 4 bytes
```

---

## 第 3 题：给定 MAC 地址的 OUI 是什么？

### 题目还原

What is the OUI of this MAC address?

```text
E8BA.7011.2874
```

A. E8BA
B. E8BA.70
C. 7011
D. E8BA.7011

字幕中选项 A 显示为 `E8Ba`，大小写不影响十六进制含义，应理解为 `E8BA`。

### 正确答案

B. E8BA.70

### 推理过程

OUI（Organizationally Unique Identifier）是 MAC 地址的前半部分：

```text
前 24 bits = 前 3 bytes
```

MAC 地址：

```text
E8BA.7011.2874
```

先按 byte 拆分。每 2 个十六进制字符是 1 byte：

```text
E8 | BA | 70 | 11 | 28 | 74
```

前 3 bytes 是：

```text
E8 | BA | 70
```

按 Cisco 常见点分格式写成：

```text
E8BA.70
```

所以正确答案是 B。

### 各选项解析

#### A. E8BA

错误。

`E8BA` 只有 4 个十六进制字符，也就是：

```text
4 hex digits × 4 bits = 16 bits = 2 bytes
```

OUI 需要 24 bits / 3 bytes，所以不够。

#### B. E8BA.70

正确。

`E8BA.70` 等于：

```text
E8 | BA | 70
```

正好是前 3 bytes / 24 bits。

#### C. 7011

错误。

`7011` 不是 MAC 地址的前 3 bytes，而且它从中间开始取，不是 OUI。

#### D. E8BA.7011

错误。

`E8BA.7011` 是 8 个十六进制字符，也就是：

```text
8 hex digits × 4 bits = 32 bits = 4 bytes
```

OUI 只需要前 3 bytes，所以这个选项取多了。

### 考点与陷阱

考点：

* OUI 是 MAC 地址前 24 bits。
* Cisco MAC 地址点分格式的拆分。
* 1 hex digit = 4 bits。
* 2 hex digits = 1 byte。

常见陷阱：

* 按点号机械取第一段 `E8BA`。
* 取前两段 `E8BA.7011`，导致取了 4 bytes。
* 忘记 OUI 是前 3 bytes，而不是前 4 个字符。

快速判断方法：

```text
MAC: E8BA.7011.2874
按 byte: E8 BA 70 11 28 74
OUI: 前三个 byte = E8 BA 70 = E8BA.70
```

---

## 第 4 题：交换机使用 Ethernet frame 的哪个字段填充 MAC 地址表？

### 题目还原

Which field of an Ethernet frame does a switch use to populate its MAC address table?

A. Preamble
B. Length
C. Source MAC Address
D. Destination MAC Address

### 正确答案

C. Source MAC Address

### 推理过程

交换机收到 frame 后，会先看 Source MAC Address。

原因是：

```text
如果我从某个接口收到来自某个 source MAC 的 frame，
说明要到达这个 source MAC，可以从这个接口出去。
```

例如：

```text
Frame received on: Fa0/1
Source MAC:        AAAA.AA00.0001
```

交换机会学习：

```text
AAAA.AA00.0001 → Fa0/1
```

所以填充 MAC 地址表使用的是 Source MAC Address。

Destination MAC Address 用于查表决定转发方向，不用于学习。

### 各选项解析

#### A. Preamble

错误。

Preamble 用于 receiver clock synchronization，不用于 MAC 地址学习。

#### B. Length

错误。

Length 字段表示被封装数据长度，不用于 MAC 地址学习。

#### C. Source MAC Address

正确。

交换机通过 Source MAC Address 学习：

```text
source MAC → receiving interface
```

这就是动态 MAC 地址表的来源。

#### D. Destination MAC Address

错误。

Destination MAC Address 虽然也是 MAC 地址，但它用于查表决定 frame 应该发往哪个端口。交换机不能通过 destination MAC 判断“这个 MAC 从哪里来”。

举例：

```text
PC1 → PC2
Destination MAC = PC2
Source MAC      = PC1
Received on     = Fa0/1
```

SW1 能确定 PC1 在 Fa0/1 方向，因为 frame 是 PC1 发来的。
但 SW1 不能仅凭 destination MAC 判断 PC2 在哪里，否则 unknown unicast 就不会存在了。

### 考点与陷阱

考点：

* MAC learning。
* Source MAC 与 Destination MAC 的不同用途。
* MAC 地址表如何动态生成。

常见陷阱：

* 误以为交换机“想发给谁就学习谁”，于是选 Destination MAC。
* 忘记交换机学习的是“从哪里来”，不是“要到哪里去”。

快速判断方法：

```text
学习 MAC 表 → Source MAC
决定发往哪里 → Destination MAC
```

---

## 第 5 题：交换机会把哪种 frame 从除入接口外的所有接口泛洪？

### 题目还原

What kind of frame does a switch flood out of all interfaces except the one it was received on?

A. Unknown unicast
B. Known unicast
C. Allcast

### 正确答案

A. Unknown unicast

### 推理过程

交换机收到单播 frame 后，会查 MAC 地址表中的 Destination MAC。

如果目标 MAC 不在表中，这个 frame 是 unknown unicast。

交换机不知道目标在哪个端口，但目标可能在某个端口后面，所以交换机会 flooding：

```text
从所有接口发出，除了收到该 frame 的接口
```

因此正确答案是：

```text
A. Unknown unicast
```

### 各选项解析

#### A. Unknown unicast

正确。

Unknown unicast 是目标 MAC 不在交换机 MAC 地址表中的单播 frame。

处理方式：

```text
Flood out all interfaces except the receiving interface.
```

#### B. Known unicast

错误。

Known unicast 是目标 MAC 已经存在于 MAC 地址表中的单播 frame。

交换机知道目标方向，所以只会 forwarding 到对应接口，不需要 flooding。

#### C. Allcast

错误。

Allcast 不是本视频中讲的 Ethernet frame 类型，也不是标准 Ethernet 基本帧类型考点。

字幕没有更多上下文；这里按视频原选项理解，`allcast` 是干扰项。

### 考点与陷阱

考点：

* Unknown unicast。
* Known unicast。
* Flooding 规则。
* 入接口不转发原则。

常见陷阱：

* 以为 unknown unicast 会被丢弃。
* 以为 flooding 等于 broadcast。
* 忘记 flooding 不包括入接口。

快速判断方法：

```text
Destination MAC in table? yes → known unicast → forward
Destination MAC in table? no  → unknown unicast → flood
```

---

### Quiz 错题复盘卡

#### 第 1 题复盘卡

考点：Ethernet frame 字段作用
正确规则：Preamble 用于 receiver clock synchronization。
易错原因：把 SFD 当成同步字段。
变式自测题：哪个 Ethernet 字段表示 Preamble 结束并标记 frame 正文开始？

#### 第 2 题复盘卡

考点：MAC 地址长度
正确规则：MAC address = 48 bits = 6 bytes。
易错原因：把 IPv4 的 32 bits 和 MAC 的 48 bits 混淆，或把 bits/bytes 混淆。
变式自测题：一个 6-byte MAC 地址等于多少 bits？

#### 第 3 题复盘卡

考点：OUI 判断
正确规则：OUI 是 MAC 地址前 24 bits / 前 3 bytes。
易错原因：按点号错误取字段，取成前 2 bytes 或前 4 bytes。
变式自测题：MAC 地址 `001A.2B3C.4D5E` 的 OUI 是什么？

#### 第 4 题复盘卡

考点：MAC address table 学习机制
正确规则：交换机从 Source MAC Address 学习 MAC 表。
易错原因：误以为交换机从 Destination MAC 学习。
变式自测题：SW1 从 Fa0/5 收到一个 source MAC 为 `AAAA.BBBB.CCCC` 的 frame，SW1 会在 MAC 表中添加什么对应关系？

#### 第 5 题复盘卡

考点：Unknown unicast flooding
正确规则：Unknown unicast 会从除入接口以外的所有接口 flood。
易错原因：把 unknown unicast 和 broadcast 混淆，或误以为 unknown unicast 会被丢弃。
变式自测题：交换机从 Fa0/1 收到一个目的 MAC 不在表中的 unicast frame，如果还有 Fa0/2、Fa0/3、Fa0/4，它会从哪些端口发出？

---

## 必须记住的规则

1. Ethernet 涉及 OSI Layer 1 和 Layer 2；本节重点是 Layer 2。
2. 交换机工作在 Layer 2，主要根据 MAC 地址表转发 Ethernet frame。
3. IP 地址是 Layer 3 地址；MAC 地址是 Layer 2 地址。
4. LAN 通常由路由器接口分隔，交换机通常扩展 LAN。
5. Layer 4 PDU 是 segment。
6. Layer 3 PDU 是 packet。
7. Layer 2 PDU 是 frame。
8. Preamble 长度 7 bytes，用于接收端时钟同步。
9. SFD 长度 1 byte，bit pattern 是 `10101011`，表示 Preamble 结束和 frame 开始。
10. Destination MAC 长度 6 bytes。
11. Source MAC 长度 6 bytes。
12. Type/Length 长度 2 bytes。
13. FCS 长度 4 bytes，用 CRC 检测错误。
14. MAC address 长度是 48 bits / 6 bytes。
15. MAC address 通常由 12 个十六进制字符表示。
16. 1 个十六进制字符 = 4 bits。
17. OUI 是 MAC 地址前 24 bits / 前 3 bytes。
18. BIA 指 burned-in address，也就是制造时烧录的 MAC 地址。
19. 交换机从 Source MAC 学习 MAC 地址表。
20. 交换机使用 Destination MAC 查表决定转发。
21. Unknown unicast：目的 MAC 不在 MAC 地址表中。
22. Unknown unicast 会 flooding。
23. Flooding 是从除入接口以外的所有接口发出。
24. Known unicast：目的 MAC 已在 MAC 地址表中。
25. Known unicast 会 forwarding，只发往对应接口。
26. Cisco 动态 MAC 地址默认 5 分钟无活动后老化删除。
27. MAC 地址表中的接口表示“到达该 MAC 的方向”，不一定表示终端直连在该接口上。
28. 本视频无单独 Packet Tracer Lab，Lab 会留到 Part 2 后。

---

## 常见误区

### 误区 1：交换机根据 IP 地址转发

错误。普通二层交换机根据 MAC 地址表转发 Ethernet frame。

正确理解：

```text
Layer 2 switch → MAC address
Router / Layer 3 device → IP address
```

---

### 误区 2：交换机从 Destination MAC 学习

错误。交换机从 Source MAC 学习。

正确规则：

```text
Source MAC + receiving interface → 写入 MAC address table
Destination MAC → 查 MAC address table 决定转发
```

---

### 误区 3：Unknown unicast 是 broadcast

错误。

Unknown unicast 的 destination MAC 仍然是某一个具体 MAC。只是交换机不知道这个 MAC 在哪里，所以临时 flooding。

Broadcast frame 的 destination MAC 是广播地址，这部分视频没有展开。

---

### 误区 4：Flooding 会从所有端口发，包括入接口

错误。

Flooding 是：

```text
all interfaces except the one it was received on
```

入接口不会再发回去。

---

### 误区 5：MAC 地址表中的接口一定直连目标设备

错误。

如果中间有多台交换机，MAC 表中的接口可能只是通往目标 MAC 的方向。

例如：

```text
SW2 MAC table:
AAAA.AA00.0001 → F0/3
```

这可能只是说明 PC1 在 SW2 的 F0/3 方向，并不表示 PC1 直接插在 SW2 F0/3。

---

### 误区 6：MAC 地址是 32 bits

错误。

```text
MAC address = 48 bits
IPv4 address = 32 bits
```

---

### 误区 7：OUI 是 MAC 地址第一个点号前面的内容

错误。

OUI 是前 24 bits / 前 3 bytes，不是按点号机械判断。

例如：

```text
E8BA.7011.2874
```

OUI 是：

```text
E8BA.70
```

不是：

```text
E8BA
```

也不是：

```text
E8BA.7011
```

---

### 误区 8：FCS 可以修复错误

本视频重点是 FCS 用于 detect errors。不要在 CCNA 初学阶段把它说成一定能纠错。

---

### 误区 9：Preamble 和 SFD 功能一样

不一样。

```text
Preamble → receiver clock synchronization
SFD      → marks end of preamble and beginning of frame
```

---

## 主动回忆问题

1. Ethernet 为什么既涉及 Layer 1 又涉及 Layer 2？
2. 交换机主要工作在 OSI 哪一层？
3. IP 地址和 MAC 地址分别属于哪一层？
4. 什么设备通常用于分隔不同 LAN？
5. 交换机是扩展 LAN 还是分隔 LAN？
6. Layer 2 的 PDU 叫什么？
7. Ethernet frame 中 trailer 的字段是什么？
8. Preamble 长度是多少？作用是什么？
9. SFD 的 bit pattern 是什么？
10. Destination MAC 和 Source MAC 分别有多长？
11. Type/Length 字段什么时候表示 Length？
12. Type/Length 字段什么时候表示 Type？
13. `0x0800` 表示什么？
14. `0x86DD` 表示什么？
15. FCS 长度是多少？使用什么算法？
16. MAC 地址有多少 bits？
17. 为什么 12 个十六进制字符可以表示一个 MAC 地址？
18. OUI 是 MAC 地址的哪一部分？
19. `E8BA.7011.2874` 的 OUI 是什么？
20. 交换机用哪个字段学习 MAC 地址表？
21. 交换机用哪个字段决定转发方向？
22. 什么是 unknown unicast？
23. 什么是 known unicast？
24. flooding 和 forwarding 的区别是什么？
25. flooding 是否会从入接口发出？
26. Cisco 动态 MAC 地址默认多久无活动后老化？
27. 两台交换机是否共享同一张 MAC 地址表？
28. MAC 表中的接口是否一定表示目标设备直连？
29. PC2 收到 PC1 的 frame 但没有回复，交换机能不能学习 PC2 的 MAC？
30. 为什么 PC3 收到发给 PC2 的 unicast frame 后会丢弃？

---

## 本日复习清单

### Ethernet frame 字段

* [ ] 我能按顺序写出 Ethernet frame 的主要字段。
* [ ] 我知道 Preamble 是 7 bytes。
* [ ] 我知道 SFD 是 1 byte。
* [ ] 我知道 Destination MAC 是 6 bytes。
* [ ] 我知道 Source MAC 是 6 bytes。
* [ ] 我知道 Type/Length 是 2 bytes。
* [ ] 我知道 FCS 是 4 bytes。
* [ ] 我知道 FCS 使用 CRC 做错误检测。

### MAC 地址

* [ ] 我知道 MAC address = 48 bits = 6 bytes。
* [ ] 我知道 MAC 地址通常写成 12 个十六进制字符。
* [ ] 我知道 1 个 hex digit = 4 bits。
* [ ] 我知道 OUI = 前 24 bits = 前 3 bytes。
* [ ] 我能从 `E8BA.7011.2874` 中取出 OUI：`E8BA.70`。
* [ ] 我知道 BIA 是 burned-in address。

### LAN 与 OSI

* [ ] 我知道交换机主要工作在 Layer 2。
* [ ] 我知道 IP 地址是 Layer 3。
* [ ] 我知道 MAC 地址是 Layer 2。
* [ ] 我知道交换机扩展 LAN，路由器分隔 LAN。
* [ ] 我能区分 segment、packet、frame。

### Switching 行为

* [ ] 我知道交换机从 Source MAC 学习。
* [ ] 我知道交换机根据 Destination MAC 查表转发。
* [ ] 我能解释 dynamic MAC address。
* [ ] 我知道 unknown unicast 会 flooding。
* [ ] 我知道 known unicast 会 forwarding。
* [ ] 我知道 flooding 不会从入接口发出。
* [ ] 我知道 Cisco 动态 MAC 默认 5 分钟无活动后老化。
* [ ] 我知道 MAC 表中的 interface 表示到达方向，不一定是直连端口。

### Quiz 掌握

* [ ] Quiz 1：receiver clock synchronization → Preamble。
* [ ] Quiz 2：physical address / MAC address → 48 bits。
* [ ] Quiz 3：OUI → 前 3 bytes。
* [ ] Quiz 4：populate MAC address table → Source MAC Address。
* [ ] Quiz 5：flood out all except receiving interface → Unknown unicast。
