# Changelog

All notable changes to the Mutation Testing Assistant will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.4.1] - 2026-06-10

### Fixed
- **JSON 数据一致性**：统一 metadata/summary/project list 三处为 18 项目、5,642 变异体、88.9% 覆盖率
- **BPlusTree 项目**：补入 JSON 项目列表（248 mutants, 85%）
- **重复内容**：删除 Common Mistakes 表格中 5 行完全重复的条目
- **测试模式编号**：Pattern 19/20/21 重新排序为 1-21 连续编号
- **等价模式分类**：章节重命名为 Survival Patterns & Killing Strategies，分三类标注（🟰 真等价 / 🔧 可杀死 / 🛠️ 杀活技巧）
- **Pattern 交叉引用**：Workflow 节全部改为描述性引用，消除"Pattern 14 指代两个概念"等歧义
- **JUnit 4→5 全量迁移**：`@Before`→`@BeforeEach`、`@After`→`@AfterEach`、`@Test(expected=)`→`assertThrows()`、移除自定义 assertThrows 工具方法
- **INCREMENTS 解释**：修正误导性注释为正确的无限循环 TIMED_OUT 机制说明
- **中文混排**：`test增量` → `minimal incremental test`
- **构造函数 MATH 示例**：补全来源变量推导过程

### Added
- `README.md` — 项目主页（简介、快速上手、导航、技术栈）
- `CONTRIBUTING.md` — 贡献指南（PR 规范、代码示例规范、术语规范）
- `CHANGELOG.md` — 本文件

---

## [2.4.0] - 2026-06-02

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

## [2.3.0] - 2026-05-25

### Added
- CMD CLI 解析器项目案例 (72 mutants, 100% killed)
- 多态基类默认路径覆盖模式 (Pattern 12)
- `while(true)` TIMED_OUT 有效杀死信号说明 (Pattern 13)
- 反射 Map 状态注入杀活技巧
- 新增 Test Patterns 16-21：匿名子类、Map注入、泛型兼容、双路径测试等

---

## [2.2.0] - 2026-05-18

### Added
- Nextday 项目案例 (98 mutants, 99% killed)
- 防御性默认值等价模式 (Pattern 11)
- 三元最值对称性等价模式 (Pattern 10)
- 平台无关输出捕获模式
- 数组索引全遍历杀活模式
- 反射边界值注入模式

---

## [2.1.0] - 2026-05-10

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

## [2.0.0] - 2026-05-03

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

## [1.0.0] - 2026-04-20

### Added
- 初始版本
- 8 大变异算子杀活策略
- 6 个等价变异体模式 (Pattern 1-6)
- 10 个测试模式
- 9 个项目实战案例 (CMD → ElevatorManager)
- 7 条 Iron Rules
- 18 步工作流
