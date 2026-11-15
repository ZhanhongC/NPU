# Linux 内核驱动层

放 OS 机制相关、与具体平台无关的内容。平台私有事实去 `40-platforms/`。

## 建议的条目顺序（按踩坑频率排）

1. `cmd-submission.md` — ioctl 入队 → doorbell → 中断 → fence 完成，全链路时序与失败点
2. `uapi-contracts.md` — 对外 ioctl / sysfs / debugfs 契约，错误码到底谁返回的
3. `mm.md` — IOVA、IOMMU 域、SG 表、cache 维护方向、bounce buffer 何时必须
4. `probe-init.md` — DT/ACPI 资源、probe 与 remove 的资源顺序（含 DMA 在飞时怎么停）
5. `pm-reset.md` — runtime PM / genpd / 时钟引用计数、复位恢复序列
6. `debug/` — 手法库：`dmesg` 解析、ftrace 关注点、`devmem` 用法、IOMMU fault 判读

## 写法

用 `00-meta/templates/concept.md`；接口条目用 `contract.md`。每条必须写「适用内核版本」。
