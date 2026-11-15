# 题库：加速器框架与 UAPI

来源批次：研究批次 1（2026-11-15）。行号已由我对上游源码复核。

### AF-01 accel 设备的主设备号与 fops 从哪来
- 层级: L1
- 评分点: ① ACCEL_MAJOR = 261 ② 节点 /dev/accel/accelN ③ DEFINE_DRM_ACCEL_FOPS ④ unlocked_ioctl = drm_ioctl 直接复用 DRM 分派
- 标准答案: 261；fops 由 DEFINE_DRM_ACCEL_FOPS 生成，ioctl 直接落到 drm_ioctl，所以 accel 只是 DRM 的一个新 major 加一层极薄字符设备壳。证据：drivers/accel/drm_accel.c:101 MKDEV(ACCEL_MAJOR, index)、:198 register_chrdev(ACCEL_MAJOR, "accel", &accel_stub_fops)。
- 追问: 那 accel 的 ioctl 号段和 DRM render node 冲突吗？为什么？
- 来源: https://docs.kernel.org/accel/introduction.html（2026-11）、上游 drm_accel.c

### AF-02 为什么另立 accel，而不是复用 render node
- 层级: L2
- 评分点: ① 隔离的是 UAPI 面不是内核实现 ② DRIVER_COMPUTE_ACCEL 与 DRIVER_RENDER / DRIVER_MODESET 互斥 ③ 防止 GPU 用户态栈误用 accel 设备 ④ 内核侧仍共用 drm_minor / drm_gem / drm_sched
- 标准答案: 目的是让加速器有一组不会被 GPU 生态假设污染的 UAPI 语义；内核实现完全复用 DRM core（drivers/accel/Kconfig 整段包在 if DRM 内，accel_core_init() 由 drm_core_init() 调用，见 drivers/gpu/drm/drm_drv.c:1286）。
- 追问: 如果某加速器既要 render 又要 compute，上游怎么处理？
- 来源: https://lwn.net/Articles/867168/（2021-08-26）、https://lwn.net/Articles/915509/（2022-11-19）

### AF-03 同事说 drivers/accel 是独立于 DRM 的第二个子系统，用证据反驳
- 层级: L3
- 评分点: ① Kconfig 在 if DRM 内 ② accel_core_init 由 drm_core_init 调 ③ 共用 drm_minor_acquire 与 drm_ioctl ④ 2021 LWN 那场争论的结论是并入 DRM
- 标准答案: 三条硬证据：drivers/accel/Kconfig 首行 if DRM；drm_drv.c:1286 调 accel_core_init；drm_accel.c:123 用 drm_minor_acquire(&accel_minors_xa, iminor(inode))。结论：目录独立，框架不独立。
- 追问: 那为什么它还需要自己的 xarray 和 major，而不直接用 DRM 的 minor 空间？
- 来源: 上游源码（2026-11 复核）

### AF-04 drm_accel 自带命令调度吗
- 层级: L1
- 评分点: ① 不带 ② 调度由各驱动自选 ③ rocket / amdxdna / ethosu 的 Kconfig 写 select DRM_SCHED ④ ivpu / qaic / habanalabs 自建队列
- 标准答案: 不带。核心只做字符设备、minor 生命周期、sysfs/debugfs 挂载。要 drm_sched 就自己 select 并自建 entity/sched。
- 追问: 自建队列相对于 drm_sched 会失去哪些东西（至少三条）？
- 来源: https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/log/drivers/accel（2025-07）

### AF-05 drm_uring_cmd 如何省掉上下文切换
- 层级: L2
- 评分点: ① IORING_OP_URING_CMD 一次 enter 批量提交 ② 16 字节命令字段：ioctl 号 + 参数指针 ③ 内核侧仍走 drm_ioctl 分发 ④ Cloud AI 100 批量 128 条最佳提速约 50%（厂商自报）
- 标准答案: 把 N 次 syscall 压成 1 次 enter，命令本身走 16B 固定字段描述，内核复用既有 drm_ioctl 实现，所以不改驱动分派逻辑。截至 2026-11 主线仍未合并（drm_ioctl.c 无 DRM_URING_CMD）。
- 追问: 你的场景里 syscall 占比多高时才值得上 uring_cmd？先测什么？
- 来源: https://lists.freedesktop.org/archives/dri-devel/2025-June/509457.html（2025-06-06）、https://indico.freedesktop.org/event/6/contributions/309/（2024-10）

### AF-06 给新 NPU 选 ioctl / uring_cmd / 自研队列，怎么论证
- 层级: L3
- 评分点: ① 先量化 syscall 与提交开销占比 ② 安全面（io_uring 历史 CVE、部分平台禁用）③ UAPI 稳定与上游接受度 ④ 是否需要 iopoll / 批量
- 标准答案: 顺序是先测再选：perf 量出提交路径占端到端比例，占比小于几个百分点就别引入新 ABI；再评估 io_uring 在该发行版/Android 是否可用；最后看上游态度——未合并的 ABI 不能作为产品依赖。
- 追问: 如果产品必须支持老内核又没有 uring_cmd，你会怎么折中？
- 来源: 同上 + https://www.usenix.org/system/files/fast24-joshi.pdf（2024-02）

### AF-07 timeline syncobj 的 point 到底是什么
- 层级: L1
- 评分点: ① 64 位单调序号 ② wait 针对某个 point ③ QUERY 返回 last signaled / last submitted ④ WAIT_ALL 与 WAIT_FOR_SUBMIT 语义不同
- 标准答案: 它是这条时间线（一个 dma_fence context）上的进度序号，不是队列深度也不是帧号。内核用 dma_fence_chain 把每个 point 串成链（drm_syncobj.c:350 dma_fence_chain_init(chain, prev, fence, point)）。
- 追问: 同一个 syncobj 上 point 能否跳号？内核怎么处理？
- 来源: https://github.com/torvalds/linux/blob/master/include/uapi/drm/drm.h（DRM_CAP_SYNCOBJ_TIMELINE 0x14，:789）

### AF-08 dma_fence_is_later() 为什么不能跨 context 用
- 层级: L2
- 评分点: ① seqno 只在同一 context 内单调 ② 跨驱动/跨引擎没有全序 ③ 误判会导致排序错误甚至释放后使用 ④ 合流必须用 dma_fence_array
- 标准答案: 它比较的是 seqno，而 seqno 只在单个 context 内有意义；两个 context 的 seqno 不可比。要表达多个 fence 都完成，用 dma_fence_array 而不是比大小。
- 追问: 那如何正确表达「A 引擎第 5 号任务早于 B 引擎第 3 号任务」这种跨引擎顺序？
- 来源: https://github.com/torvalds/linux/blob/master/include/linux/dma-fence.h

### AF-09 用户态拿 syncobj 当「数据已对 CPU 可见」的凭据，错在哪
- 层级: L3
- 评分点: ① fence 只保证执行完成，不保证缓存可见性 ② 可见性要靠驱动侧 barrier / cache 维护 ③ 跨 context 无全序 ④ WAIT_DEADLINE 只是调度提示（drm.h:961，1<<3）
- 标准答案: 完成不等于可见。fence signal 时硬件写完，但 CPU 侧 cache 是否需要 invalidate、写是否已过内存屏障，取决于驱动实现；把 fence 当可见性凭据会在 non-coherent 平台上读到旧数据。
- 追问: 你会要求在 UAPI 文档里补哪一句话，才不至于让用户态误解？
- 来源: 上游 drm.h + dma-fence.h