# 题库：开源 NPU/加速器驱动案例

来源批次：研究批次 1（2026-11-15）。设计取舍类题目，答对要点不够，要能说出代价。

### OC-01 上游对加速器驱动的准入门槛是什么
- 层级: L1
- 评分点: ① 必须有一份开源用户态实现 ② 不接受私有 ABI 的 out-of-tree 中间层 ③ 走 DRM/accel 框架 ④ 这条规则直接塑造了 rocket 的形态
- 标准答案: 至少一份开源用户态。这是 rocket 把算子编译与调度放进用户态（Gallium/Mesa）的根本原因——内核只上电、映射、提交。
- 追问: 这条规则对厂商的商业边界意味着什么？哪部分可以闭源？
- 来源: https://lwn.net/Articles/870418/（2021-09-27）

### OC-02 rocket 与 amdxdna 的调度粒度差异，以及各自代价
- 层级: L2
- 评分点: ① rocket 每核一个 in_flight_job，单发 ② amdxdna 每个 hwctx 一个 drm_sched ③ 单发实现简单但核间无法并行排队 ④ 多 ctx 要自己处理跨 sched 的优先级与抢占
- 标准答案: rocket 用 rocket_core.h 里每核一个 in_flight_job，实现极简但一个核同时只能有一个作业在飞；amdxdna 以 hwctx 为调度单位（aie2_ctx.c 的 drm_sched_stop(sched, bad_job)），才可能多租户并发，代价是跨 ctx 调度与资源竞争要自己兜。
- 追问: 如果你的 NPU 有 8 个核，你会选哪种粒度？说出判据而不是结论。
- 来源: docs.kernel.org/accel/rocket、docs.kernel.org/accel/amdxdna（2026-11）

### OC-03 RK3588 上 job 超时后的恢复路径
- 层级: L3
- 评分点: ① drm_sched_stop(sched, bad_job) ② 硬件复位 ③ 清 in_flight_job ④ drm_sched_start(sched, 0) 再放行
- 标准答案: 顺序是停调度器 → 复位硬件 → 清在飞状态 → 重启调度器。顺序错了会出现「复位后调度器还在往旧环里推」的二次故障。
- 追问: 复位过程中已完成但还没 signal 的 fence 怎么处理？不处理会怎样？
- 来源: rocket_job.c（rocket_reset 与 drm_sched_stop/start 路径）

### OC-04 HL_WAIT_CS 与 dma_fence 同步的本质区别
- 层级: L1
- 评分点: ① 前者是阻塞 ioctl + 内核 completion ② 后者可跨驱动共享时间线 ③ habanalabs 因此无法参与 dma-buf 隐式同步 ④ 用户态必须显式 wait
- 标准答案: HL_WAIT_CS 走 completion（wait_for_completion_interruptible_timeout(&pend->fence.completion)），是驱动内部同步；dma_fence 是跨子系统契约。选了前者就自动放弃与 DRM/媒体栈的隐式互操作。
- 追问: 这对多设备流水线（NPU + 相机 + 显示）意味着什么额外工作？
- 来源: drivers/accel/habanalabs/common/command_submission.c

### OC-05 ivpu 为什么同时保留 SUBMIT 与 CMDQ 两套 ioctl
- 层级: L2
- 评分点: ① 旧模型每个 job 一次消息提交，开销大 ② 新模型门铃 + 环形队列，可批量 ③ 归零用户态已发布（XRT/Level-Zero）④ UAPI 只增不删
- 标准答案: 兼容已发布的用户态。DRM_IVPU_SUBMIT(0x05) 与 DRM_IVPU_CMDQ_SUBMIT(0x0d) 并存，新路径靠 ivpu_cmdq_ring_db() 走门铃，旧路径每次走 JSM 消息。
- 追问: 两套路径并存时，测试矩阵要怎么设计才不会漏掉其中一条？
- 来源: include/uapi/drm/ivpu_accel.h:19,25,27

### OC-06 Gaudi 队列满或阻塞时如何避免死等
- 层级: L3
- 评分点: ① 先判空闲槽位再提交 ② 轮询 + 超时而不是纯阻塞 ③ completion 带 timeout ④ 超时走复位与 CS 超时上报
- 标准答案: 提交前用 queue_free_slots() 判断，等待用 hl_poll_timeout_memory 带超时，最终以 completion 的 timeout 收口并上报，绝不允许无限阻塞在提交路径里。
- 追问: 为什么在提交路径里睡眠是危险的？中断上下文与非中断上下文各写多少行？
- 来源: habanalabs/common/hw_queue.c

### OC-07 rocket 为什么把算子编译与调度放到用户态
- 层级: L1
- 评分点: ① 内核只做上电/映射/提交 ② 把 ABI 面积压到最小 ③ 编译器与算子演进不必跟着内核走 ④ 与上游「必须有开源用户态」互相成就
- 标准答案: 官方文档原话就是内核只上电、分配映射、提交作业给前端单元，其余在用户态由 Gallium 驱动完成。内核越小，UAPI 越稳定，升级越不需要碰内核。
- 追问: 代价是什么？用户态出错时内核还能提供哪些兜底？
- 来源: https://docs.kernel.org/accel/rocket/index.html（2026-11）

### OC-08 共享单一 IOMMU domain（不用 GPUVM）换来什么、失去什么
- 层级: L2
- 评分点: ① 省掉 GPUVM 抽象与页表管理 ② iommu_map_sgtable 直接映射 ③ 失去 per-VM/per-进程隔离 ④ 难以支持稀疏地址与按需缺页
- 标准答案: rocket 在 rocket_gem.c 里直接 iommu_map_sgtable 到共享 domain，实现简单；代价是没有 per-进程地址空间隔离，多租户或需要稀疏虚拟地址时就得自己造一套。
- 追问: 若要求进程间隔离，最小改动是在哪一层加东西？
- 来源: drivers/accel/rocket/rocket_gem.c

### OC-09 中断/MSI 为什么是产品级问题而不是边角料
- 层级: L3
- 评分点: ① 中断风暴会拖垮整机而不是单个进程 ② 单 MSI 模式下要自己做源聚合 ③ 用户态隔离影响谁能 mask 中断 ④ 需有速率限制与降级策略
- 标准答案: qaic 文档专门写 IRQ Storm Mitigation、Single MSI Mode、Userspace Client Isolation 三节，说明这属于交付设计而非调试细节：没有速率限制的中断路径在异常时会把整机打挂。
- 追问: 你的驱动有没有中断频率上限？超过上限时该丢谁？
- 来源: https://docs.kernel.org/accel/qaic/index.html（2026-11）

## 可迁移教训（背诵级）

| 教训 | 出处 |
|---|---|
| 内核只做上电/映射/提交，编译调度放用户态，ABI 面积最小 | rocket 文档 |
| 环队列范式：写描述符+影子环 → 更新 pi → 敲门铃 | habanalabs/common/hw_queue.c |
| 用 drm_sched 就别手写依赖，隐式 fence 交给框架 | rocket_job.c:193、ethosu_job.c |
| 不用 drm_sched 就要自建超时与复位，并失去 dma_fence 互操作 | hl_cs 路径 |
| 单 IOMMU domain 省掉 GPUVM，但牺牲 per-VM 隔离 | rocket_gem.c |
| 调度粒度选 ctx 而不是核，才可能多租户 | aie2_ctx.c |
| UAPI 换代要新旧并存，不能删 ioctl | ivpu_accel.h |
| suspend 前必须确认硬件 idle，否则 D0i3 挂死 | ivpu_pm.c |
| 中断/MSI 是产品问题，要有速率限制与降级 | qaic 文档 |
| 平台限制显式写进 Kconfig，别等运行时才发现 | habanalabs/Kconfig（depends on X86_64） |