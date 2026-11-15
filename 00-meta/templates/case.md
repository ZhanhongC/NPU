---
id: YYYY-MM-DD-<module>-<keyword>
scope: linux            # linux | rtos | both
platform: self          # self | vendor:<型号>
stack: { kernel: "", fw: "", sdk: "" }
module: cmd-submission  # cmd-submission | mm | irq | pm-reset | runtime | compile | perf | bringup | other
symptom: 一句话写现象，含关键字便于 grep
severity: P1            # P0 阻塞量产 | P1 阻塞版本 | P2 有绕行 | P3 观察
status: 已解决           # 已解决 | 已知未解 | 误判
date: YYYY-MM-DD
tags: [timeout, iommu]
related: []
---

## 现象

直接粘贴日志/命令输出，不要转述。给出可复现的命令行。

## 复现条件

最小充分条件：哪个模型/哪组用例、什么并发、什么负载、多久一次。做不到稳定复现就写概率与场景。

## 定位过程

每步三行：**假设 → 验证手段（命令/探针）→ 结果**。走错的假设保留，末尾标「已排除」。

## 根因

一句话结论 + 机制解释（为什么会这样，而不是「改了就对了」）。附证据指针。

## 修复

patch 摘要 / 配置项 / 上游 commit。不贴完整 diff，贴关键几行与提交号。

## 验证与回归

怎么证明修好了：跑了什么、指标多少、观察多久。

## 复发条件

什么情况下会再犯（换版本、换负载、换硅 rev），以及下次怎么快速确认。
