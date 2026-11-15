# 约定（违反即条目不算完成）

## 1. 五条硬约定

1. **一条案例一个文件**，文件名 `YYYY-MM-DD-<module>-<现象关键词>.md`；聚类靠 front-matter 的 `module`，不靠目录。
2. **结论必须可证伪**：写「根因是 X」必须附支持它的证据（寄存器值 / 日志行 / 代码位置 / 波形），否则写「推测」。
3. **失败假设照写**：定位过程中走错的岔路是给后来人省时间的部分，删掉它等于删掉价值。
4. **硬件事实必须标版本**：寄存器与位域随硅 rev、spec 版本变，未标版本的速查表有害。
5. **元数据不写全不算完成**：`INDEX.md` 由脚本扫 front-matter 生成，字段缺了检索就断。

## 2. 平台与 OS 两轴怎么落

不按「平台 x OS」建矩阵（会 4 倍膨胀且大半是空目录），改用**scope 字段 + 差异只在差异点描述**：

- 与平台、OS 都无关（提交模型、定位法、指标口径）→ `10-common/`
- OS 机制相关（中断上下文、cache 维护、PM 框架）→ `20-linux/` 或 `30-rtos/`
- 平台私有事实（寄存器、固件版本、errata、厂商行为）→ `40-platforms/self|vendor/`
- 每条条目 front-matter 必写 `scope: common | linux | rtos | both | self | vendor`；平台私有条目再加 `platform:`。
- **同一根因跨 OS 或跨平台出现时只写一条案例**，正文用「Linux 侧表现 / RTOS 侧表现」两小节说明差异，别复制成两条。

## 3. 链接与命名

- 用相对路径 Markdown 链接（`[fence](../../10-common/os-parity.md)`），不用 wiki 双链 —— 保证 grep、diff 与 AI 检索都能读。
- `module` 取固定枚举（见 `templates/case.md` 注释），新枚举先加注释再用。
- 标题用中文，术语保留英文原词。

## 4. 外购 / NDA 内容

- 不粘贴厂商 NDA 文档原文；只写**结论 + 内部存放位置 + 版本与日期**，指回内部 Confluence 或共享盘路径。
- 厂商工单结论单独一条，写明工单号与回复日期 —— 这类知识最容易丢。

## 5. 索引

- 改完条目跑 `python3 00-meta/scripts/index.py`，它会重写 `INDEX.md`（不要手改 INDEX.md）。
