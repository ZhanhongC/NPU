# 题库：提交队列、屏障、抢占与可观测

来源批次：研究批次 1（2026-11-15）。行号已由我对上游源码复核（amdgpu_ring.c:169 mb() / :170 set_wptr；xe_guc_ct.c:992 与 :1031 xe_device_wmb）。

### SQ-01 为什么写 wptr / 门铃之前需要 mb()
- 层级: L1
- 评分点: ① wptr 是「发布」语义，不是普通寄存器写 ② 必须保证命令内容先全局可见 ③ 弱序架构与 IO 重排都会让你偶发丢命令 ④ 与中断无关，别把两者混为一谈
- 标准答案: mb() 保证前序存储对设备可见后才敲门铃。证据：amdgpu_ring.c:169 mb(); :170 amdgpu_ring_set_wptr(ring)。writel 本身不提供这个顺序。
- 追问: virtio 的等价写法是什么，为什么它用 virtio_store_mb 而不是 mb()？
- 来源: https://github.com/torvalds/linux/blob/master/drivers/gpu/drm/amd/amdgpu/amdgpu_ring.c#L169

### SQ-02 GuC CTB（主机→固件环）的提交顺序与溢出检测
- 层级: L2
- 评分点: ① 先写 buffer（头+payload）② 再 xe_device_wmb ③ 最后 desc_write 更新 tail ④ 溢出由固件回写 GUC_CTB_STATUS_OVERFLOW/UNDERFLOW
- 标准答案: 顺序是 memcpy 到 H2G buffer → xe_device_wmb(xe)（xe_guc_ct.c:1031）→ desc_write(tail)。长度在 GUC_CTB_MSG_0_NUM_DWORDS，错误通过 descriptor 的 status 字段枚举，不是靠中断。
- 追问: 如果固件没来得及消费，驱动侧应该看到什么现象，怎么区分「固件慢」和「环写满」？
- 来源: https://github.com/torvalds/linux/blob/master/drivers/gpu/drm/xe/xe_guc_ct.c#L1031

### SQ-03 固件 5 秒不响应提交，怎么证明是固件挂死而不是队列写错
- 层级: L3
- 评分点: ① 先看 wptr 是否推进、descriptor 是否被消费 ② 再发独立心跳消息（不经过数据路径）③ 只有心跳也超时才进 recovery ④ 进 recovery 前先把现场 dump 出来
- 标准答案: 照 ivpu 的三段式：先 wait_event_timeout 拿 -ETIMEDOUT（ivpu_ipc.c:267），再发 VPU_JSM_MSG_QUERY_ENGINE_HB_DONE（:352），仍然超时才 ivpu_pm_trigger_recovery(vdev, "IPC timeout")（:356）。关键点是不要一跳超时就复位——那会毁掉唯一现场。
- 追问: 心跳消息为什么必须走独立通道？走数据通道会误判成什么？
- 来源: https://github.com/torvalds/linux/blob/master/drivers/accel/ivpu/ivpu_ipc.c#L349

### SQ-04 影子队列 + staged CS 的隐式契约
- 层级: L2
- 评分点: ① 影子队列保存内核侧待提交项 ② 索引取模要求队列深度是 2 的幂 ③ staged 提交让「最后一个 CS 才发中断」成为隐式契约 ④ 断链就会漏完成或重复完成
- 标准答案: habanalabs 用 shadow_cs_queue[sequence & (max_pending_cs - 1)]，要求 max_pending_cs 为 2 的幂（command_submission.c:777）；staged 语义下中断只由链尾触发，中间项靠扫影子队列推进。
- 追问: 如果队列深度不是 2 的幂，代码会崩还是静默算错？你怎么测出来？
- 来源: https://github.com/torvalds/linux/blob/master/drivers/accel/habanalabs/common/command_submission.c#L777

### SQ-05 timeline fence 与 binary fence 的本质差别
- 层级: L1
- 评分点: ① 一条时间线一个单调 counter ② 能表达 N:M 依赖 ③ 可批量等待 ④ 不必每帧造新对象
- 标准答案: binary fence 一个对象一次完成，只能表达一对一；timeline 用 point 表达「同一条线上的进度」，再靠 dma_fence_chain 把多个 point 串起来（drm_syncobj.c:350）。
- 追问: 为什么 chain 的 prev 必须与 fence 属于同一 context？
- 来源: https://github.com/torvalds/linux/blob/master/drivers/gpu/drm/drm_syncobj.c#L350

### SQ-06 跨引擎依赖偶发花屏 / 偶发错结果，怀疑隐式同步失效，怎么查
- 层级: L3
- 评分点: ① 确认依赖只落在 BO 粒度，表达不了跨设备顺序 ② 检查 signalling 段是否睡眠或持锁（dma_fence_begin_signalling 断言）③ 补显式 syncobj/timeline ④ 用 tracepoint 对齐提交与完成时刻
- 标准答案: 隐式 fence 天然无法表达跨设备顺序，先把它显式化再谈别的；同时查 fence signal 段有没有违规睡眠/持锁，那会触发 lockdep 或 UAF。
- 追问: 显式化之后仍然偶发，你下一个怀疑对象是什么？
- 来源: https://www.collabora.com/news-and-blog/blog/2022/06/09/bridging-the-synchronization-gap-on-linux/（2022-06-09）

### SQ-07 硬件调度器 vs 软件队列，各自付什么代价
- 层级: L1
- 评分点: ① 抢占与上下文切换粒度 ② 固件 ABI 的维护成本 ③ 调试可见性变差 ④ 队列数/并发上限
- 标准答案: 硬件调度器换来抢占与 QoS，代价是错误只以固件 ABI 状态码暴露、调试靠 IPC dump；软件队列透明可查，但抢占基本没有。
- 追问: 为什么上游驱动在这点上分歧巨大（habanalabs 与 rocket 是两个极端）？
- 来源: https://github.com/torvalds/linux/blob/master/drivers/gpu/drm/xe/xe_exec_queue.c（sched_props.preempt_timeout_us）

### SQ-08 mid-command 抢占要实现什么
- 层级: L2
- 评分点: ① 指令边界保存 PC/寄存器/内存态 ② drain 在飞访存 ③ 抢占完成必须能以 fence 观测 ④ 超时后走 reset 而不是无限等
- 标准答案: 三件事：可恢复的上下文保存、在飞访存的 drain、以及把抢占本身表达成可观测对象（Xe 用 xe_vm_in_preempt_fence_mode + preempt_timeout_us 兜底）。
- 追问: NPU 常见的「整网格不可抢占」设计，在什么业务下会变成硬伤？
- 来源: https://github.com/torvalds/linux/blob/master/drivers/gpu/drm/xe/xe_exec_queue.c

### SQ-09 Perfetto 里只有计数器、没有提交时间线，怎么补
- 层级: L3
- 评分点: ① 开 gpu.renderstages / 厂商 HAL 数据源 ② 开内核 tracepoint（提交与调度）③ 必要时 CoreSight ETR 抓到 DRAM ④ 统一时钟域再对齐
- 标准答案: 两条腿：计数器说明「忙不忙」，提交事件说明「谁在等谁」，缺一条就无法归因。内核侧对应 amdgpu_cs_ioctl / amdgpu_sched_run_job 这类 tracepoint；固件挂死时唯一现场是片上 trace（TMC 的 ETB/ETR，coresight-tmc-core.c:515 对 ETR 有专门路径）。
- 追问: 时钟域不统一时，你会看到什么假象？
- 来源: https://perfetto.dev/docs/data-sources/gpu（访问 2026-11-15）、coresight-tmc-core.c