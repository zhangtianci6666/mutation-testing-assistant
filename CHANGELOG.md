# Changelog

All notable changes to the Mutation Testing Assistant will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [v2.5.0] - 2026-06-10

### Added
- **FastJson 项目** (551 mutants, 68% killed) — Alibaba fastjson 1.2.70 包装器项目实战案例
- **MethodHandle 项目** (490 mutants, 88% killed) — Java MethodHandle 适配器框架 (invokebinder) 实战案例
- **Anagram 项目** (96 mutants, 80% killed) — 字符串变位词求解器实战案例
- **Pattern 20: Wrapper-Project VOID Equivalence** — 包装器项目中最常见的等价变异体模式
- **包装器项目覆盖率天花板** — 新概念：不同类型项目有不同的覆盖率上限
- **Iron Rule 8: Zero Source Modification** — 严禁修改源码/配置/pom.xml
- **Iron Rule 9: Equivalent Mutant Accountability** — 等价变异体精确评估标准表格
- **BEFORE YOU START 强制类清单** + **PER-CLASS GATE** + **HARD GATE 重构** (ASCII 盒子)
- **🚀 LAUNCH SEQUENCE** — 4 条核心规则提前到第 2 屏
- **⛔ EXECUTION PROTOCOL** — 含违规示例 + 自检机制
- **README 提示词编写指南** — 完整章节（模板/约束/坏提示词/ASCII盒子/执行流程图）
- **Self-Optimization Hook v2** — 从 4 步扩展为 7 步，含语义化版本规则 + README 自动同步
- **语义化版本规则 (vMAJOR.MINOR.PATCH)** — 同一天只更新一次版本号
- `README.md` + `CONTRIBUTING.md` + `CHANGELOG.md` — 项目文档体系

### Changed
- 项目数: 18→21, 变异体总数: 5,642→6,779, 等价变异体数: 258→391
- 算法类平均覆盖率: 88.9%→86.8%
- Iron Rule 6: 从散文描述改为 HARD GATE 强制逐类 PIT 循环
- Step-by-Step Workflow 重命名为 Per-Class Loop
- project-data.json 新增 `framework_terminal_method_no_coverage` 指标
- README.md 全局数字与 skill.md 同步

### Fixed
- Iron Rule 6 被跳过问题（新增 EXECUTION PROTOCOL + BEFORE YOU START）
- JSON 数据一致性 (metadata/summary/project list 三处统一)
- Self-Optimization 缺少 README 同步机制
- 版本号无规则 → 新增语义化版本规则
- JUnit 4→5 全量迁移
- INCREMENTS 解释修正、中文混排修正、构造函数 MATH 示例补全

---

## [v2.4.0] - 2026-06-02

### Added
- **BPlusTree 项目** (248 mutants, 85% killed) 实战案例
- 5 个新等价变异体模式：
  - Pattern 15: ArrayList Initial Capacity Equivalence (集合初始容量等价)
  - Pattern 16: Compound Condition Dead Code (复合条件死代码)
  - Pattern 17: Binary Search Boundary Equivalence (二分搜索边界等价)
  - Pattern 18: Self-Consistent Internal Method (自洽内部方法)
  - Pattern 19: Probabilistic Constructor Parameter (概率性构造参数)
- 4 条 B+Tree 测试规则 (t-value 选择、顺序插入、增量构建、断言升级)
- 7 个快速参考表新条目 (GENERIC_TYPE_MISMATCH, CAPACITY_EQUIVALENT, DEAD_COMPOUND_CONDITION, BINARY_SEARCH_BOUNDARY, SELF_CONSISTENT_METHOD, TREE_SPLIT_COVERAGE, PROBABILISTIC_CONSTRUCTOR)

---

## [v2.3.0] - 2026-05-25

### Added
- CMD CLI 解析器项目案例 (72 mutants, 100% killed)
- 多态基类默认路径覆盖模式 (Pattern 12)
- `while(true)` TIMED_OUT 有效杀死信号说明 (Pattern 13)
- 反射 Map 状态注入杀活技巧
- 新增 Test Patterns 16-21：匿名子类、Map注入、泛型兼容、双路径测试等

---

## [v2.2.0] - 2026-05-18

### Added
- Nextday 项目案例 (98 mutants, 99% killed)
- 防御性默认值等价模式 (Pattern 11)
- 三元最值对称性等价模式 (Pattern 10)
- 平台无关输出捕获模式
- 数组索引全遍历杀活模式
- 反射边界值注入模式

---

## [v2.1.0] - 2026-05-10

### Added
- GUI/Animation 专项 (P_Queue 项目, 1032 mutants)
- 动画状态恢复等价模式 (Pattern 9)
- Headless 环境陷阱识别
- Counting Subclass Pattern
- AWT Graphics Mock 链式验证
- 子类部分模拟模式

### Changed
- 覆盖率统计区分算法类和 GUI 类

---

## [v2.0.0] - 2026-05-03

### Added
- UnrolledLinkedList2023 项目案例 (256 mutants, 91.8% killed)
- 遍历对称性等价模式 (Pattern 4)
- 死存储等价模式 (Pattern 5)
- Fail-Fast 计数器单调性等价模式 (Pattern 7)
- 复合条件副作用模式 (Pattern 8)
- 内部状态探查测试模式
- 后向循环多迭代触发模式
- PIT Metrics 诊断指南

---

## [v1.0.0] - 2026-04-20

### Added
- 初始版本
- 8 大变异算子杀活策略
- 6 个等价变异体模式 (Pattern 1-6)
- 10 个测试模式
- 9 个项目实战案例 (CMD → ElevatorManager)
- 7 条 Iron Rules
- 18 步工作流
