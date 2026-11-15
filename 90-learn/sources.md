# 前沿来源登记

规则：只登记公开来源；写日期与可靠度；消化后标「已入题库」。复核栏写我实际核对过的内容。

| 主题 | 来源 | 日期 | 可靠度 | 状态 |
|---|---|---|---|---|
| accel 框架总览 | https://docs.kernel.org/accel/introduction.html | 2026-11 | 官方文档 | 已入题库 |
| 加速器进 DRM 的政策史 | https://lwn.net/Articles/867168/ | 2021-08-26 | LWN | 已入题库 |
| accel 并入 DRM 的 v4 讨论 | https://lwn.net/Articles/915509/ | 2022-11-19 | LWN | 已入题库 |
| NPU 子系统路线（LPC 2025） | https://lpc.events/event/19/contributions/2088/ | 2025-12 | 会议 slides | 待消化 |
| QDA/FastRPC 进 accel 的 RFC | https://lwn.net/Articles/1059949/ | 2026-02-24 | LWN | 待消化 |
| uring_cmd 设备提交 | https://www.usenix.org/system/files/fast24-joshi.pdf | 2024-02 | USENIX 论文 | 已入题库 |
| io_uring for DRM（未合并） | https://lists.freedesktop.org/archives/dri-devel/2025-June/509457.html | 2025-06-06 | 邮件列表 | 已入题库 |
| drm_accel 源码 | https://github.com/torvalds/linux/blob/master/drivers/accel/drm_accel.c | 持续 | 上游源码 | 已复核（ACCEL_MAJOR/register_chrdev/minor_acquire） |
| drm.h UAPI | https://github.com/torvalds/linux/blob/master/include/uapi/drm/drm.h | 持续 | 上游源码 | 已复核（:789 CAP 0x14、:961 WAIT_DEADLINE） |
| dma_fence 语义 | https://github.com/torvalds/linux/blob/master/include/linux/dma-fence.h | 持续 | 上游源码 | 已入题库 |
| syncobj 时间线实现 | https://github.com/torvalds/linux/blob/master/drivers/gpu/drm/drm_syncobj.c | 持续 | 上游源码 | 已复核（:350 chain_init） |
| 门铃发布语义 | https://github.com/torvalds/linux/blob/master/drivers/gpu/drm/amd/amdgpu/amdgpu_ring.c | 持续 | 上游源码 | 已复核（:169 mb、:170 set_wptr） |
| 固件命令环 | https://github.com/torvalds/linux/blob/master/drivers/gpu/drm/xe/xe_guc_ct.c | 持续 | 上游源码 | 已复核（:992/:1031 xe_device_wmb） |
| IPC 超时→心跳→recovery | https://github.com/torvalds/linux/blob/master/drivers/accel/ivpu/ivpu_ipc.c | 持续 | 上游源码 | 已复核（:267 ETIMEDOUT、:352 HB、:356 recovery） |
| 影子队列 / staged CS | https://github.com/torvalds/linux/blob/master/drivers/accel/habanalabs/common/command_submission.c | 持续 | 上游源码 | 已入题库 |
| 显式同步与隐式同步之差 | https://www.collabora.com/news-and-blog/blog/2022/06/09/bridging-the-synchronization-gap-on-linux/ | 2022-06-09 | 厂商博客 | 已入题库 |
| 抢占与 preempt fence | https://github.com/torvalds/linux/blob/master/drivers/gpu/drm/xe/xe_exec_queue.c | 持续 | 上游源码 | 已入题库 |
| 可观测性数据源 | https://perfetto.dev/docs/data-sources/gpu | 访问 2026-11-15 | 官方文档（无发布日，待核实） | 已入题库 |
| 片上 trace（ETB/ETR） | https://github.com/torvalds/linux/blob/master/drivers/hwtracing/coresight/coresight-tmc-core.c | 持续 | 上游源码 | 已入题库 |
| rocket 设计文档 | https://docs.kernel.org/accel/rocket/index.html | 2026-11 | 官方文档 | 待入题库 |
| amdxdna 设计文档 | https://docs.kernel.org/accel/amdxdna/index.html | 2026-11 | 官方文档 | 待入题库 |
| qaic 设计文档 | https://docs.kernel.org/accel/qaic/index.html | 2026-11 | 官方文档 | 待入题库 |
| 加速器驱动准入门槛（需开源用户态） | https://lwn.net/Articles/870418/ | 2021-09-27 | LWN | 待入题库 |
| ivpu UAPI（两代提交并存） | https://github.com/torvalds/linux/blob/master/include/uapi/drm/ivpu_accel.h | 持续 | 上游源码 | 已复核（:19 SUBMIT、:25/:27 CMDQ） |
| rocket 提交路径 | https://github.com/torvalds/linux/blob/master/drivers/accel/rocket/rocket_job.c | 持续 | 上游源码 | 已复核（:193 deps、:248 push_job） |