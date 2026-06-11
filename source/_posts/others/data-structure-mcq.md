---
title: 数据结构选择题
date: 2023-10-18 10:00:00
description: 本文收集了一系列数据结构相关的选择题，用于巩固对基础数据结构概念的理解和应用。
keywords: 数据结构选择题
categories: 其他
tags:
  - 选择题
  - 算法
  - 学习资料
# sticky: 5
---

## 数据结构选择题集锦

本文收集了一系列数据结构相关的选择题，用于巩固对基础数据结构概念的理解和应用。

### 内容概览

- **线性数据结构**: 数组、链表、栈、队列等相关选择题
- **树结构**: 二叉树、二叉搜索树、平衡树等相关习题
- **图论**: 图的表示、遍历、最短路径等经典问题
- **高级数据结构**: 堆、哈希表、并查集等专题练习

## 数据结构概论选择题

### 1. 单项选择题

<details>
<summary>（1）线性结构中数据元素之间是（ ）关系。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：D. 一对一
</div>
</details>

A. 一对多　　　B. 多对多　　　C. 多对一　　　D. 一对一

<details>
<summary>（2）数据结构中与计算机无关的是数据的（ ）结构。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：C. 逻辑
</div>
</details>

A. 存储　　　B. 物理　　　C. 逻辑　　　D. 物理和存储

<details>
<summary>（3）在计算机中存储数据时，通常不仅要存储各数据元素的值，而且要存储（ ）。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：C. 数据元素之间的关系
</div>
</details>

A. 数据的处理方法　　　　　B. 数据元素的类型
C. 数据元素之间的关系　　　D. 数据的存储方法

<details>
<summary>（4）数据采用链式存储结构时，要求（ ）。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：A. 每个结点占用一片连续的存储区域
</div>
</details>

A. 每个结点占用一片连续的存储区域
B. 所有结点占用一片连续的存储区域
C. 结点的最后一个域必须是指针域
D. 每个结点有多少后继结点，就必须设多少个指针域

<details>
<summary>（5）计算机算法是指（ ）。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：C. 求解问题的有限运算序列
</div>
</details>

A. 计算方法　　　B. 排序方法
C. 求解问题的有限运算序列　　　D. 调度方法

<details>
<summary>（6）计算机算法必须具备输入、输出和（ ）等 5 个特性。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：B. 可行性、确定性和有穷性
</div>
</details>

A. 可行性、可移植性和可扩充性
B. 可行性、确定性和有穷性
C. 确定性、有穷性和稳定性
D. 易读性、稳定性和安全性

<details>
<summary>（7）算法分析的目的是（ ）。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：C. 分析算法的效率以求改进
</div>
</details>

A. 找出数据结构的合理性　　　　　B. 研究算法中的输入和输出的关系
C. 分析算法的效率以求改进　　　　D. 分析算法的易懂性和文档性

<details>
<summary>（8）算法分析的两个主要方面是（ ）。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：A. 空间复杂性和时间复杂性
</div>
</details>

A. 空间复杂性和时间复杂性　　　B. 正确性和简明性
C. 可读性和文档性　　　　　　　D. 数据复杂性和程序复杂性

<details>
<summary>（9）某算法的时间复杂度为 O(n²)，表明该算法的（ ）。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：C. 执行时间与 n² 成正比
</div>
</details>

A. 问题规模是 n²　　　　　　　　B. 执行时间等于 n²
C. 执行时间与 n² 成正比　　　　　D. 问题规模与 n² 成正比

<details>
<summary>（10）某算法的空间复杂度为 O(1)，表明执行该算法时（ ）。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：B. 需要的临时存储空间为常量
</div>
</details>

A. 不需要存储空间　　　　　　　　B. 需要的临时存储空间为常量
C. 需要的存储空间恰好为 1　　　　D. 需要的临时存储空间为 1

## 线性表选择题

### 1. 单项选择题

<details>
<summary>（1）线性表是（ ）。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：A. 一个有限序列，可以为空
</div>
</details>

A. 一个有限序列，可以为空
B. 一个有限序列，不可以为空
C. 一个无限序列，可以为空
D. 一个无限序列，不可以为空

<details>
<summary>（2）顺序表具有随机存取特性，是指（ ）。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：C. 查找序号为 i 的元素的时间与顺序表中元素个数 n 无关
</div>
</details>

A. 查找值为 x 的元素的时间与顺序表中元素个数 n 无关
B. 查找值为 x 的元素的时间与顺序表中元素个数 n 有关
C. 查找序号为 i 的元素的时间与顺序表中元素个数 n 无关
D. 查找序号为 i 的元素的时间与顺序表中元素个数 n 有关

<details>
<summary>（3）在 n 个元素的顺序表中，算法的时间复杂度是 O(1)的操作是（ ）。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：A. 访问第 i 个元素(2≤i≤n) 及其前驱元素
</div>
</details>

A. 访问第 i 个元素(2≤i≤n) 及其前驱元素
B. 在第 i (1≤i≤n)个元素后插入一个新元素
C. 删除第 i 个元素(1≤i≤n)
D. 将 n 个元素从小到大排序

<details>
<summary>（4）在含有 127 个元素的顺序表中插入一个新元素，平均移动元素的次数是（ ）。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：B. 63.5
</div>
</details>

A. 8　　　B. 63.5　　　C. 63　　　D. 7

<details>
<summary>（5）将两个分别含有 m、n 个元素的有序顺序表归并成一个有序顺序表，对应算法的时间复杂度是（ ），这里 MIN 表示取最小值。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：C. O(m+n)
</div>
</details>

A. O(n)　　　B. O(m)　　　C. O(m+n)　　　D. O(MIN(m,n))

<details>
<summary>（6）线性表采用链表存储结构时，其存放各个元素的单元地址（ ）。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：D. 连续与否均可以
</div>
</details>

A. 必须是连续的　　　B. 一定是不连续的
C. 部分地址必须是连续的　　　D. 连续与否均可以

<details>
<summary>（7）线性表的链式存储结构和顺序存储结构相比，其优点是（ ）。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：C. 便于插入和删除元素
</div>
</details>

A. 所有的操作算法实现简单　　　B. 便于随机存取
C. 便于插入和删除元素　　　　　D. 节省存储空间

<details>
<summary>（8）关于线性表的顺序存储结构和链式存储结构的描述中，正确的是（ ）。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：B. II，IV
</div>
</details>

I. 线性表的顺序存储结构优于链式存储结构
II. 顺序存储结构比链式存储结构的存储密度高
III. 如需要频繁插入和删除元素，最好采用顺序存储结构
IV. 如需要频繁插入和删除元素，最好采用链式存储结构

A. I，II，III　　　B. II，IV　　　C. II，III　　　D. III，IV

<details>
<summary>（9）设线性表中有 n 个元素，以下运算中，（ ）在单链表上实现要比在顺序表上实现效率更高。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：A. 删除指定位置元素的后一个元素
</div>
</details>

A. 删除指定位置元素的后一个元素
B. 在尾元素的后面插入一个新元素
C. 顺序输出前 k (k＜n)个元素
D. 交换第 i 个元素和第 n-i+1 个元素的值

<details>
<summary>（10）以下关于单链表的叙述中，不正确的是（ ）。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：C. 可以通过头结点直接计算第 i 个结点的存储地址
</div>
</details>

A. 结点除自身信息外还包括指针域，因此存储密度小于顺序存储结构
B. 逻辑上相邻的元素物理上不必相邻
C. 可以通过头结点直接计算第 i 个结点的存储地址
D. 插入、删除运算操作方便，不必移动结点

<details>
<summary>（11）通过含有 n(n≥1)个元素的数组 a，采用头插法建立一个单链表 L，则 L 中结点值的次序（ ）。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：B. 与数组 a 的元素次序相反
</div>
</details>

A. 与数组 a 的元素次序相同　　　B. 与数组 a 的元素次序相反
C. 与数组 a 的元素次序无关　　　D. 以上都不对

<details>
<summary>（12）在含有 n(n≥1)个结点的单链表中，实现（ ）运算的时间复杂度为 O(n)。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：A. 遍历单链表求第 i 个结点值
</div>
</details>

A. 遍历单链表求第 i 个结点值
B. 在地址为 p 的结点之后插入一个新结点
C. 删除链表的首结点
D. 删除地址为 p 的结点的后继结点

<details>
<summary>（13）已知两个长度分别为 m 和 n 的升序单链表，若将它们合并为一个长度为 m+n 的升序单链表，则最坏情况下的时间复杂度是（ ）。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：C. O(MIN(m,n))
</div>
</details>

A. O(n)　　　B. O(m×n)　　　C. O(MIN(m,n))　　　D. O(MAX(m,n))

<details>
<summary>（14）与非循环单链表相比，循环单链表的主要优点是（ ）。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：D. 从表中任意结点出发都能扫描到整个链表
</div>
</details>

A. 不再需要头指针
B. 已知某个结点的位置后，能够容易找到它的前驱结点
C. 在进行插入、删除操作时，能更好地保证链表不断开
D. 从表中任意结点出发都能扫描到整个链表

<details>
<summary>（15）与单链表相比，双链表的优点之一是（ ）。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：D. 访问前后相邻结点更方便
</div>
</details>

A. 插入、删除操作更简单　　　　　B. 可以进行随机访问
C. 可以省略表头指针或表尾指针　　D. 访问前后相邻结点更方便

<details>
<summary>（16）在长度为 n(n≥1)的双链表中插入一个结点(非尾结点)要修改（ ）个指针域。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：D. 4
</div>
</details>

A. 1　　　B. 2　　　C. 3　　　D. 4

<details>
<summary>（17）在长度为 n(n≥1)的双链表 L 中，在 p 所指结点之前插入一个新结点的时间复杂度为（ ）。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：A. O(1)
</div>
</details>

A. O(1)　　　B. O(n)　　　C. O(n²)　　　D. O(nlog₂n)

<details>
<summary>（18）非空的循环单链表 L 的尾结点（由 p 所指向）满足（ ）。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：C. p -> next == L
</div>
</details>

A. p -> next == NULL　　　B. p == NULL
C. p -> next == L　　　　　D. p == L

<details>
<summary>（19）在长度为 n(n≥1)的循环双链表 L 中，删除尾结点的时间复杂度为（ ）。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：A. O(1)
</div>
</details>

A. O(1)　　　B. O(n)　　　C. O(n²)　　　D. O(nlog₂n)

<details>
<summary>（20）某线性表最常用的操作是在尾元素之后插入一个元素和删除尾元素，则采用以下（ ）存储方式最节省运算时间。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：D. 循环双链表
</div>
</details>

A. 单链表　　　B. 循环单链表　　　C. 双链表　　　D. 循环双链表

## 栈和队列选择题

### 1. 单项选择题

<details>
<summary>（1）栈的"先进后出"特性是指（ ）。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：A. 最后进栈的元素总是最先出栈
</div>
</details>

A. 最后进栈的元素总是最先出栈
B. 当同时进行进栈和出栈操作时，总是进栈优先
C. 每当有出栈操作时，总要先进行一次进栈操作
D. 每次出栈的元素总是最先进栈的元素

<details>
<summary>（2）设一个栈的进栈序列是 a、b、c、d（即元素 a～d 依次进过该栈），则借助该栈所得到的输出序列不可能是（ ）。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：D. dabc
</div>
</details>

A. abcd　　　B. dcba　　　C. acdb　　　D. dabc

<details>
<summary>（3）一个栈的进栈序列是 a、b、c、d、e，则栈的不可能的输出序列是（ ）。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：C. deab
</div>
</details>

A. edcba　　　B. decba　　　C. deab　　　D. abcde

<details>
<summary>（4）已知一个栈的进栈序列是 1、2、3、…、n，其输出序列的第一个元素是 i（1≤i≤n），则第 j（1≤j≤n）个出栈元素是（ ）。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：D. 不确定
</div>
</details>

A. i　　　B. n－i　　　C. j－i+1　　　D. 不确定

<details>
<summary>（5）设顺序栈 st 的栈顶指针 top 的初始值为 -1，栈空间大小为 MaxSize，则判断 st 栈为栈空的条件为（ ）。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：A. st. top == -1
</div>
</details>

A. st. top == -1　　　B. st. top! == -1
C. st. top! = MaxSize　　　D. st. top == MaxSize

<details>
<summary>（6）设顺序栈 st 的栈顶指针 top 的初始值为 -1，栈空间大小为 MaxSize，则判断 st 栈为栈满的条件是（ ）。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：D. st. top == MaxSize-1
</div>
</details>

A. st. top! = -1　　　B. st. top == -1
C. st. top! = MaxSize-1　　　D. st. top == MaxSize-1

<details>
<summary>（7）当用一个数组 data[0..n-1]存放栈中元素时，栈底最好（ ）。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：C. 设置在 data[0]或 data[n-1]处
</div>
</details>

A. 设置在 data[0]处　　　　　　B. 设置在 data[n-1]处
C. 设置在 data[0]或 data[n-1]处　　　D. 设置在 data 数组的任何位置

<details>
<summary>（8）若一个栈用数组 data[1..n]存储，初始栈顶指针 top 为 0，则以下元素 x 进栈的正确操作是（ ）。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：A. top++; data[top]=x;
</div>
</details>

A. top++; data[top]=x;　　　B. data[top]=x; top++;
C. top--; data[top]=x;　　　D. data[top]=x; top--;

<details>
<summary>（9）若一个栈用数组 data[1..n]存储，初始栈顶指针 top 为 n，则以下元素 x 进栈的正确操作是（ ）。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：D. data[top]=x; top--;
</div>
</details>

A. top++; data[top]=x;　　　B. data[top]=x; top++;
C. top--; data[top]=x;　　　D. data[top]=x; top--;

<details>
<summary>（10）队列中元素的进出原则是（ ）。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：A. 先进先出
</div>
</details>

A. 先进先出　　　B. 后进先出　　　C. 栈空则进　　　D. 栈满则出

<details>
<summary>（11）栈和队列的不同点是（ ）。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：C. 栈只能在一端进行插入删除操作，而队列在不同端进行插入删除操作
</div>
</details>

A. 都是线性表
B. 都不是线性表
C. 栈只能在一端进行插入删除操作，而队列在不同端进行插入删除操作
D. 没有不同点

<details>
<summary>（12）元素 a、b、c、d 依次连续进入队列 qu 后，队头元素是（ ① ），队尾元素是（ ② ）。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：① A. a ② D. d
</div>
</details>

A. a　　　B. b　　　C. c　　　D. d

<details>
<summary>（13）一个队列的进队序列为 1234，则队列可能的输出序列是（ ）。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：B. 1234
</div>
</details>

A. 4321　　　B. 1234　　　C. 1432　　　D. 3241

<details>
<summary>（14）在循环队列中，元素的排列顺序（ ）。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：A. 由元素进队的先后顺序确定
</div>
</details>

A. 由元素进队的先后顺序确定　　　B. 与元素值的大小有关
C. 与队头和队尾指针的取值有关　　D. 与队中数组大小有关

<details>
<summary>（15）循环队列 qu（队头指针 front 指向队首元素的前一位置，队尾指针 rear 指向队尾元素的位置）的队满条件是（ ）。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：C. (qu. rear+1)%MaxSize == qu. front
</div>
</details>

A. (qu. rear+1)%MaxSize == (qu. front+1)%MaxSize
B. (qu. rear+1)%MaxSize == qu. front+1
C. (qu. rear+1)%MaxSize == qu. front
D. qu. rear == qu. front

<details>
<summary>（16）循环队列 qu（队头指针 front 指向队首元素的前一位置，队尾指针 rear 指向队尾元素的位置）的队空条件是（ ）。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：D. qu. rear == qu. front
</div>
</details>

A. (qu. rear+1)%MaxSize == (qu. front+1)%MaxSize
B. (qu. rear+1)%MaxSize == qu. front+1
C. (qu. rear+1)%MaxSize == qu. front
D. qu. rear == qu. front

<details>
<summary>（17）设循环队列中数组的下标是 0～N-1，其头尾指针分别为 f 和 r（队头指针 f 指向队首元素的前一位置，队尾指针 r 指向队尾元素的位置），则其元素个数为（ ）。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：D. (r-f+N)%N
</div>
</details>

A. r-f　　　B. r-f-1　　　C. (r-f)%N+1　　　D. (r-f+N)%N

<details>
<summary>（18）一个循环队列中用 data[0..n-1]数组保存队中元素，另设置一个队尾指针 rear 和一个记录队中实际元素个数的变量 count，则该队中最多可以存放的元素个数是（ ）。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：B. n
</div>
</details>

A. n-1　　　B. n　　　C. (rear+n) % n　　　D. (n-rear) % n

<details>
<summary>（19）设栈 S 和队列 Q 的初始状态为空，元素 e₁～e₆ 依次通过栈 S，一个元素出栈后即进队列 Q，若 6 个元素出队的序列是 e₂、e₁、e₃、e₆、e₅、e₄，则栈 S 的容量至少应该是（ ）。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：C. 3
</div>
</details>

A. 5　　　B. 4　　　C. 3　　　D. 2

<details>
<summary>（20）与顺序队相比，链队的（ ）。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：D. 缺点是不能根据队首和队尾指针计算队的长度
</div>
</details>

A. 优点是可以实现无限长队列
B. 优点是进队和出队时间性能更好
C. 缺点是不能进行顺序访问
D. 缺点是不能根据队首和队尾指针计算队的长度

## 树与二叉树选择题

### 1. 单项选择题

<details>
<summary>（1）以下关于树的描述中，不正确的是（ ）。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：D. 树中任意两个结点有且只有一条路径相通
</div>
</details>

A. 树是一种非线性数据结构
B. 树的根结点没有前驱
C. 树中除根结点外的所有结点有且只有一个前驱
D. 树中任意两个结点有且只有一条路径相通

<details>
<summary>（2）设一个非空的m叉树中有n个结点，则该树中的分支结点（非终端结点）的个数是（ ）。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：C. ⌈(n-1)/m⌉
</div>
</details>

A. n-1　　　B. n/m　　　C. ⌈(n-1)/m⌉　　　D. n-⌊n/m⌋

<details>
<summary>（3）在一棵度为3的树中，若有10个度为3的结点，5个度为2的结点，8个度为1的结点，则该树的叶子结点个数为（ ）。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：A. 24
</div>
</details>

A. 24　　　B. 25　　　C. 26　　　D. 23

<details>
<summary>（4）若一颗完全二叉树有768个结点，则该二叉树的高度为（ ）。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：D. 10
</div>
</details>

A. 8　　　B. 9　　　C. 11　　　D. 10

<details>
<summary>（5）设二叉树的前序遍历序列为ABCDEFGH，中序遍历序列为BDCEAFGH，则后序遍历序列为（ ）。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：B. DCEBFGHA
</div>
</details>

A. DCEBHGFA　　　B. DCEBFGHA　　　C. BDCEHGFA　　　D. DCBEHGFA

<details>
<summary>（6）具有n个结点的完全二叉树的高度为（ ）。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：C. ⌊log₂n⌋+1
</div>
</details>

A. ⌈log₂n⌉　　　B. ⌊log₂n⌋　　　C. ⌊log₂n⌋+1　　　D. ⌈log₂n⌉+1

<details>
<summary>（7）一棵非空二叉树的先序遍历序列与后序遍历序列正好相反，则该二叉树一定是（ ）。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：B. 只有一个结点的二叉树
</div>
</details>

A. 只有左子树的二叉树　　　B. 只有一个结点的二叉树
C. 只有右子树的二叉树　　　D. 完全二叉树

<details>
<summary>（8）若一棵满二叉树的结点个数为n，则叶子结点的个数是（ ）。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：A. (n+1)/2
</div>
</details>

A. (n+1)/2　　　B. n/2　　　C. (n-1)/2　　　D. (n+1)/3

<details>
<summary>（9）在一棵非空二叉树中，若终端结点数为n₀，度为2的结点数为n₂，则n₀=（ ）。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：D. n₂+1
</div>
</details>

A. n₂　　　B. n₂-1　　　C. 2n₂　　　D. n₂+1

<details>
<summary>（10）设计一个算法，求二叉树中以值为x的结点为根的子树中的结点数目。如二叉树采用二叉链表存储结构，空间复杂度为（ ）。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：B. O(h)，h为二叉树的高度
</div>
</details>

A. O(n)，n为二叉树的结点总数　　　B. O(h)，h为二叉树的高度
C. O(1)　　　　　　　　　　　　　　D. O(log₂n)，n为二叉树的结点总数

<details>
<summary>（11）以下关于二叉树与度为2的树的区别，描述错误的是（ ）。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：B. 在二叉树中，结点子树的左右次序是严格约定的
</div>
</details>

A. 度为2的树至少有3个结点，而二叉树可以为空
B. 在二叉树中，结点子树的左右次序是严格约定的
C. 度为2的树中，所有结点的度都是2
D. 二叉树中，结点的度可以为0、1或2

<details>
<summary>（12）下列二叉树中，后序遍历序列与中序遍历序列相同的是（ ）。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：C. 只有右子树的单支树
</div>
</details>

A. 只有根结点的二叉树　　　B. 只有左子树的单支树
C. 只有右子树的单支树　　　D. 完全二叉树

<details>
<summary>（13）对于具有n个结点的二叉树，若按完全二叉树的顺序对二叉树中的结点进行编号，且编号为i的结点，其左孩子（若存在）的编号一定是（ ）。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：A. 2i
</div>
</details>

A. 2i　　　B. 2i+1　　　C. 2i-1　　　D. i/2

<details>
<summary>（14）若一个具有n个结点的二叉树，其中叶结点个数为n₀，则度为1的结点个数为（ ）。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：C. 2n₀-n
</div>
</details>

A. n₀-1　　　B. n-n₀　　　C. 2n₀-n　　　D. n-2n₀

<details>
<summary>（15）一棵二叉树的前序序列为ABCDE，中序序列为BADEC，则该二叉树的后序序列为（ ）。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：A. BDECA
</div>
</details>

A. BDECA　　　B. BEDCA　　　C. DEBCA　　　D. DECBA

<details>
<summary>（16）设一个二叉树的遍历序列如下：前序遍历为ABDCEF，中序遍历为DBAECF，则该二叉树的后序遍历序列为（ ）。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：D. DBECFA
</div>
</details>

A. DBEFCA　　　B. DBCFEA　　　C. DBECAF　　　D. DBECFA

<details>
<summary>（17）已知二叉树中序序列为BDAC，后序序列为DBCA，则先序序列为（ ）。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：B. ABDC
</div>
</details>

A. ADBC　　　B. ABDC　　　C. ACBD　　　D. ABCD

<details>
<summary>（18）一棵二叉树的先序遍历序列和后序遍历序列正好相反，则该二叉树中的结点个数最多是（ ）。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：A. 1
</div>
</details>

A. 1　　　B. 2　　　C. 3　　　D. 不确定

<details>
<summary>（19）若某二叉树有5个结点，则不同的二叉树形态共有（ ）种。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：D. 14
</div>
</details>

A. 5　　　B. 8　　　C. 12　　　D. 14

<details>
<summary>（20）完全二叉树的存储结构最佳选择是（ ）。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：C. 顺序存储
</div>
</details>

A. 链式存储　　　B. 哈希存储　　　C. 顺序存储　　　D. 索引存储

## 图论选择题

### 1. 单项选择题

<details>
<summary>（1）在一个图中，所有顶点的度数之和等于图的边数的（ ）倍。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：C. 2
</div>
</details>

A. 1/2　　　B. 1　　　C. 2　　　D. 4

<details>
<summary>（2）有 8 个顶点的无向图最多有（ ）条边。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：B. 28
</div>
</details>

A. 14　　　B. 28　　　C. 56　　　D. 112

<details>
<summary>（3）有 8 个顶点的无向连通图最少有（ ）条边。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：C. 7
</div>
</details>

A. 5　　　B. 6　　　C. 7　　　D. 8

<details>
<summary>（4）有 8 个顶点的有向完全图有（ ）条边。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：C. 56
</div>
</details>

A. 14　　　B. 28　　　C. 56　　　D. 112

<details>
<summary>（5）n 个顶点的强连通图中至少有（ ）条边。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：A. n
</div>
</details>

A. n　　　B. n－1　　　C. 2n　　　D. n(n－1)

<details>
<summary>（6）若一个图的邻接矩阵是对称矩阵，则该图一定是（ ）。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：D. 无向图或有向图
</div>
</details>

A. 有向图　　　　　B. 无向图
C. 连通图　　　　　D. 无向图或有向图

<details>
<summary>（7）若用邻接矩阵 A 表示一个含有 n 个顶点不带权的有向图，则其中第 i(0≤i≤n－1)列中包含的 1 的个数为（ ）。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：A. 图中顶点 i 的入度
</div>
</details>

A. 图中顶点 i 的入度　　　　　　　B. 图中顶点 i 的出度
C. 图中边的数目　　　　　　　　　D. 图中连通分量的数目

<details>
<summary>（8）一个带权有向图 G 用邻接矩阵 A 存储，则顶点 i 的出度等于 A 中（ ）。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：C. 第 i 行非∞且非 0 的元素个数
</div>
</details>

A. 第 i 行非∞的元素之和　　　　　B. 第 i 列非∞的元素之和
C. 第 i 行非∞且非 0 的元素个数　　D. 第 i 列非∞且非 0 的元素个数

<details>
<summary>（9）用邻接表存储图所用的空间大小（ ）。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：A. 与图的顶点和边数有关
</div>
</details>

A. 与图的顶点和边数有关　　　　　B. 只与图的边数有关
C. 只与图的顶点数有关　　　　　　D. 与边数的二次方有关

<details>
<summary>（10）一个图的邻接表表示中有奇数个边结点，则该图是（ ）。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：A. 有向图
</div>
</details>

A. 有向图　　　B. 无向图　　　C. 无向图或有向图　　　D. 以上都不对

<details>
<summary>（11）设无向图 G=(V,E)和 G'=(V',E')，如果 G'是 G 的生成树，则下面的说法中错误的是（ ）。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：B. G'为 G 的连通分量
</div>
</details>

A. G'为 G 的子图　　　　　　　　　B. G'为 G 的连通分量
C. G'为 G 的极小连通子图且 V=V'　　D. G'是 G 的一个无环子图

<details>
<summary>（12）用邻接表表示图进行广度优先遍历时，通常是采用（ ）来实现算法的。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：B. 队列
</div>
</details>

A. 栈　　　B. 队列　　　C. 树　　　D. 图

<details>
<summary>（13）图的广度优先遍历方法中用到辅助队列，每个顶点最多进队（ ）次。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：A. 1
</div>
</details>

A. 1　　　B. 2　　　C. 3　　　D. 不确定

<details>
<summary>（14）已知一个图的邻接表如图 7.1 所示，则从顶点 0 出发得到的深度优先遍历序列是（ ）。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：D. 0 1 2 3
</div>
</details>

A. 0 1 3 2　　　B. 0 2 3 1　　　C. 0 3 2 1　　　D. 0 1 2 3

<details>
<summary>（15）已知一个图的邻接表如图 7.1 所示，则从顶点 0 出发得到的广度优先遍历序列是（ ）。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：D. 0 1 2 3
</div>
</details>

A. 0 1 3 2　　　B. 0 2 3 1　　　C. 0 3 2 1　　　D. 0 1 2 3

<details>
<summary>（16）深度优先遍历类似于二叉树的（ ）。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：A. 先序遍历
</div>
</details>

A. 先序遍历　　　B. 中序遍历　　　C. 后序遍历　　　D. 层次遍历

<details>
<summary>（17）广度优先遍历类似于二叉树的（ ）。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：D. 层次遍历
</div>
</details>

A. 先序遍历　　　B. 中序遍历　　　C. 后序遍历　　　D. 层次遍历

<details>
<summary>（18）最小生成树指的是（ ）。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：C. 连通图中所有生成树中权值之和为最小的生成树
</div>
</details>

A. 由连通图所得到的边数最少的生成树
B. 由连通图所得到的顶点数相对较少的生成树
C. 连通图中所有生成树中权值之和为最小的生成树
D. 连通图的极小连通子图

<details>
<summary>（19）任何一个带权连通图的最小生成树（ ）。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：B. 一棵或多棵
</div>
</details>

A. 只有一棵　　　B. 一棵或多棵　　　C. 一定有多棵　　　D. 可能不存在

<details>
<summary>（20）用 Prim 和 Kruskal 两种算法构造图的最小生成树，所得到的最小生成树（ ）。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：C. 可能相同，也可能不同
</div>
</details>

A. 是相同的　　　B. 是不同的　　　C. 可能相同，也可能不同　　　D. 以上都不对

<details>
<summary>（21）用 Prim 算法求一个连通的带权图的最小生成树，在算法执行的某时刻，已选取的顶点集合 U={1,2,3}，已选取的边的集合 TE={(1,2),(2,3)}，要选取下一条权值最小的边，应当从（ ）组边中选取。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：A. {(1,4),(3,4),(3,5),(2,5)}
</div>
</details>

A. {(1,4),(3,4),(3,5),(2,5)}
B. {(4,5),(1,3),(3,5)}
C. {(1,2),(2,3),(3,5)}
D. {(3,4),(3,5),(4,5),(1,4)}

<details>
<summary>（22）用 Kruskal 算法求一个连通的带权图的最小代价生成树，在算法执行的某时刻，已选取的边集合 TE={(1,2),(2,3),(3,5)}，要选取下一条权值最小的边，不可能选取的边是（ ）。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：A. (1,3)
</div>
</details>

A. (1,3)　　　B. (2,4)　　　C. (3,6)　　　D. (1,4)

<details>
<summary>（23）对含 n 个顶点 e 条边的有向图，Dijkstra 算法的时间复杂度为（ ）。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：C. O(n²)
</div>
</details>

A. O(n)　　　B. O(n+e)　　　C. O(n²)　　　D. O(ne)

<details>
<summary>（24）用 Dijkstra 算法求一个带权有向图 G 中从顶点 0 出发的最短路径，在算法执行的某时刻，S={0,2,3,4}，下一步选取的目标顶点可能是（ ）。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：D. 顶点 7
</div>
</details>

A. 顶点 2　　　B. 顶点 3　　　C. 顶点 4　　　D. 顶点 7

<details>
<summary>（25）对含 n 个顶点 e 条边的有向图，Floyd 算法的时间复杂度为（ ）。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：D. O(n³)
</div>
</details>

A. O(n)　　　B. O(ne)　　　C. O(n²)　　　D. O(n³)

<details>
<summary>（26）有一个顶点编号为 0～4 的带权有向图 G，现用 Floyd 算法求任意两个顶点之间的最短路径，在算法执行的某时刻，已考虑了 0～2 的顶点，现考虑顶点 3，则以下叙述中正确的是（ ）。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：D. 所有两个顶点之间的路径都可能被修改
</div>
</details>

A. 只可能修改从顶点 0～2 到顶点 3 的最短路径
B. 只可能修改从顶点 3 到顶点 0～2 的最短路径
C. 只可能修改从顶点 0～2 到顶点 4 的最短路径
D. 所有两个顶点之间的路径都可能被修改

<details>
<summary>（27）已知有向图 G=(V,E)，其中，V={1,2,3,4}，E=<1,2>,<1,3>,<2,3>,<2,4>,<3,4>，图 G 的拓扑序列是（ ）。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：A. 1,2,3,4
</div>
</details>

A. 1,2,3,4　　　B. 1,3,2,4　　　C. 1,3,4,2　　　D. 1,2,4,3

<details>
<summary>（28）若一个有向图中的顶点不能排成一个拓扑序列，则可断定该有向图（ ）。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：D. 含有顶点个数大于 1 的强连通分量
</div>
</details>

A. 是个有根有向图　　　　　　　　B. 是个强连通图
C. 含有多个入度为 0 的顶点　　　　D. 含有顶点个数大于 1 的强连通分量

<details>
<summary>（29）关键路径是事件结点网络中（ ）。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：A. 从源点到汇点的最长路径
</div>
</details>

A. 从源点到汇点的最长路径　　　B. 从源点到汇点的最短路径
C. 最长的回路　　　　　　　　　D. 最短的回路

<details>
<summary>（30）以下对于 AOE 网的叙述中，错误的是（ ）。</summary>
<div style="background-color: #f0f0f0; padding: 10px; border-left: 4px solid #009688;">
答案：C. 任何一个关键活动提前完成，整个工程也将提前完成
</div>
</details>

A. 在 AOE 网中可能存在多条关键路径
B. 关键活动不按期完成就会影响整个工程的完成时间
C. 任何一个关键活动提前完成，整个工程也将提前完成
D. 所有关键活动都提前完成，整个工程也将提前完成

题目将陆续更新，敬请期待。

<!-- 题目将在此处添加 --> 