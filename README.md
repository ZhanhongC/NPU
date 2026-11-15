# NPU 驱动知识库

面向**自研 + 外购** NPU、**Linux + RTOS** 双栈驱动的个人知识库。
入口是「你会问的问题」，出口是「可复现的结论」；不是笔记堆。

## 怎么找

| 我要… | 去这里 |
|---|---|
| 回忆某个报错的根因 | `50-cases/`，先看 `INDEX.md` 的案例表 |
| 查一个接口的契约 / 错误码来源 | `20-linux/README.md`、`30-rtos/README.md` |
| 定位一个没见过的新现象 | `10-common/debug-playbook.md` |
| 同一个动作在 Linux 与 RTOS 下分别怎么做 | `10-common/os-parity.md` |
| 查缩写 | `GLOSSARY.md` |
| 查自研芯片寄存器 / 固件 / 硅版本差异 | `40-platforms/self/` |
| 查外购平台版本矩阵 / errata / 厂商工单结论 | `40-platforms/vendor/` |
| 我还不知道什么 | `70-gaps.md` |

## 骨架

- `10-common/` 平台与 OS 无关的方法论：定位法、双栈对照、性能口径
- `20-linux/` Linux 内核态驱动：probe、UAPI、内存、电源复位、调试手段
- `30-rtos/` RTOS 侧驱动：无 MMU 地址、cache 手工维护、ISR 约束、静态池
- `40-platforms/` 平台私有事实：`self/` 自研，`vendor/` 外购
- `50-cases/` 案例库（核心资产），一条一个文件
- `60-ref/` 外部资料索引　`80-lab/` 最小复现与脚本

## 怎么加（10 分钟规矩）

1. debug 结束 10 分钟内：只写「现象 + 根因」两段就存，照抄 `00-meta/templates/case.md`，文件名 `YYYY-MM-DD-<module>-<关键词>.md`。
2. 次日补「定位过程」，**失败的假设照写**。
3. 每周 20 分钟：把案例里可复用的结论提升到 `10-common` / `20-linux` / `30-rtos`，在案例里加反向链接。
4. 每月：更新 `70-gaps.md`，它就是下次主动学习的作业单。

## 维护

- 重新生成索引：`python3 00-meta/scripts/index.py`
- 规则见 `00-meta/conventions.md`；违反五条硬约定的条目不算完成。
