# Changelog

All notable changes to the Mutation Testing Assistant will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [v2.5.4] - 2026-06-11

### Added
- **Brainfuck 解释器项目** (145 mutants, 83% killed, 98% line) — 3个Brainfuck衍生语言解释器引擎

### Changed
- **P5 Dead Store 细化**: 新增 initate() 重置模式 — 当方法末尾调用重置方法清空所有中间状态时，所有中间运算的 MATH/CONDITIONALS_BOUNDARY 均等价
- **P6 Defensive Redundancy 细化**: 新增自修正括号匹配变体 — BK_RIGHT 后向扫描补偿 BK_LEFT 移除，双层守卫使单个条件移除不可观察
- **P10 Ternary Symmetry 细化**: 新增 substring 边界场景 — `cp+dTL==len` 时 if/else 两分支产生相同子串

### Verified
- initate() 重置模式: 3个类中8个MATH + 4个BOUNDARY 均因 reset 而等价
- BK_RIGHT 后向扫描自修正: 13个 REMOVE_CONDITIONALS 因双层守卫等价
- 单文件聚合策略: 110测试集中在1个 *Test.java 文件，验证 Iron Rule 6 在单文件约束下可行
- 25个幸存变异体全部通过P1-P20模式匹配验证为等价

---

## [v2.5.3] - 2026-06-11

### Added
- **LunarCalendar 项目** (527 mutants, 90% killed, 99% line) — 农历日历库，8个类
- **Test Pattern 23: Public API Over Reflection** — PIT 反射覆盖不稳定问题的解决方案
- **Self-Optimization Hook v3: 项目完成全量审计** — 项目完成后必须审查所有 reference 文件，不仅增添还要修正

### Changed
- **P6 防御式冗余细化**: 新增懒加载变体（setter被downstream getter的lazy-load覆盖）
- **common-mistakes.md**: 新增2条红牌警告——反射PIT覆盖不稳定 + 公共API优先于反射
- **killing-strategies.md**: 新增多t值精确断言技术（天文/三角MATH）
- **test-patterns-catalog.md**: Pattern 23 公共API优先模式
- **SKILL.md Quick Reference P6**: 描述扩展包含懒加载变体
- **全量统计更新**: 23项目、7568变异体、23测试模式、87.7%覆盖率

### Verified
- PIT反射覆盖不稳定: `Method.invoke()` 杀死的VOID_METHOD_CALL在后续运行复活 → 已确认并收录
- 多t值技术: t=-1,0,1,2 四组输入确保任一天文MATH至少在一组产生差异
- P6懒加载变体: DPCManager.setFestivals与getFestivals懒加载完全冗余
- 所有20个存活模式跨23个项目验证有效

---

## [v2.5.1] - 2026-06-11

### Added
- **Hotel 酒店管理系统项目** (262 mutants, 94% killed) — 状态机+排序+价格计算综合业务类实战案例
  - 13个业务类、单文件聚合~228测试
  - 8个类达100%、7个变异算子达100% (含MATH 44/44)
  - 发现 `setPrice()` 去耦技术：用setter覆写构造器自动关联的价格来击杀 getValue() 中与类型/状态相关的 MATH 变异体 (Pattern 18细化)

### Verified
- **P1 支配条件**: `contains("00")` 支配 `≤100`、外循环被内循环支配 (Hotel sortByValue)
- **P16 复合死代码**: 字符范围 `(a-z)||(A-Z)` 中的OR逻辑支配
- **P20 包装器VOID等价**: `setItems()` 冗余调用 (已由构造器设置)、空 `println()` 无功能影响
- **P2 算术恒等**: 比较器中 `return 1` 与 `return 0` 在else分支功能等同
- 14个确定性等价变异体被识别并记录

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
