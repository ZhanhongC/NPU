# Linux 与 RTOS 双栈对照表

同一个硬件动作，两个栈的做法与陷阱。**新发现差异就在这里加一行**，这是本库最高频查询的一页。

| 动作 | Linux 内核驱动 | RTOS 驱动 | 常见陷阱 |
|---|---|---|---|
| 命令提交 | ioctl 入队 → doorbell → dma-fence 等待 | 直接写寄存器或投递到自建队列 | RTOS 常在 ISR 上下文提交，禁止阻塞；Linux 侧 fifo 满时不可忙等 |
| 完成通知 | 中断 → threaded IRQ → signal fence / complete | ISR 置标志 + 任务轮询或信号量 | RTOS 无 workqueue，长活不能放 ISR；Linux 侧注意关中断时间 |
| 地址 | IOVA + IOMMU 域，设备地址不等于 CPU 地址 | 常为物理地址直通或固定映射 | 无 MMU 时 buffer 必须物理连续，不能靠 scatter |
| cache 一致性 | dma_map / dma_sync_sg_for_cpu 与 _device | 手工 clean / invalidate by range | 方向搞反读到旧数据；invalidate 前若有脏行会丢写 |
| 内存分配 | kzalloc / vmalloc / dma_alloc_coherent | 静态池或预分配内存池 | RTOS 不许运行中碎片化，池大小要在设计期定死 |
| 并发保护 | mutex / spinlock / RCU，语义分明 | 关中断 + 临界区为主 | 同一套锁策略不可直接移植；RTOS 关中断时间直接影响实时性 |
| 电源与时钟 | runtime PM + genpd + clk framework | 直接操作时钟/电源寄存器 | RTOS 没有框架兜底，漏开时钟表现为总线挂死而非报错 |
| 复位与恢复 | 复位序列 + 重新 probe 资源 | 自写恢复流程，常配 watchdog | 恢复后 DMA 描述符环与固件状态需一并重init，只复位硬件不够 |
| 日志与取证 | dmesg / ftrace / devmem / debugfs | 环形缓冲 + 串口导出 | RTOS 现场取证能力弱，**trace 点要在开发期预留**，出事再补来不及 |
| 性能观测 | perf / 硬件计数器 / sysfs 统计 | 硬件计数器 + 周期打点 | 两边口径要统一（见 `perf-metrics.md`），否则数字不可比 |

## 使用方式

1. 跨栈问题先在这里找对应动作，确认哪一列是「我们的实现」。
2. 发现新差异：加一行，并在 `50-cases/` 留一条案例说明怎么被坑到的。
