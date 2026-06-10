# Changelog

All notable changes to the Mutation Testing Assistant will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.6.5] - 2026-06-10

### Added
- **Anagram 项目** (96 mutants, 80% killed) — 字符串变位词求解器实战案例
  - 3 个业务类 (Helper/Dictionary/Anagram) / 80 个测试全部聚合在单一文件中
  - 递归算法中系统性的优化守卫等价确认：5处REMOVE_CONDITIONALS是纯性能优化，核心算法提供独立正确的backstop
  - null ≈ emptySet 等价确认：递归算法中EMPTY_RETURNS的null和空Set在所有调用方行为一致
  - 防御性null检查等价：3处方法的参数null检查，调用方已保证非null
  - for循环CONDITIONALS_BOUNDARY等价：额外迭代被递归守卫条件截获返回null
  - 死代码NO_COVERAGE：usage()私有方法无人调用

### Changed
- 项目数: 20→21, 变异体总数: 6,683→6,779, 等价变异体数: 372→391
- 算法类平均覆盖率: 87.2%→86.8%

### Verified
- Pattern 1 (Dominated Condition): Helper L42/L99/L104/L109 的优化守卫被再次确认
- Pattern 6 (Defensive Redundancy): Anagram L116/L133/L138 的防御性null检查被再次确认
- Pattern 20 (Wrapper VOID): Dictionary L85 reader.close() 局部变量VOID等价被再次确认
- EMPTY_RETURNS null≈emptySet 模式：递归算法中调用方的 `!= null && !isEmpty()` 双检查使两者语义等价

---

## [2.6.4] - 2026-06-10

### Added
- **MethodHandle 项目** (490 mutants, 88% killed) — Java MethodHandle 适配器框架 (invokebinder) 实战案例
  - 19 个业务类 / 304 个测试全部聚合在单一文件中
  - 框架终端方法 NO_COVERAGE 模式确认：invoke*/getField/setField 方法需要应用上下文，单测不可达
  - Transform.up() 类型匹配屏障确认：MethodHandles API 的严格类型要求使 Catch/Fold/TryFinally.up() 在单测中极难覆盖
  - 构造器歧义模式确认：varargs 构造器重载在 Java 中永久歧义，不可达

### Changed
- 项目数: 19→20, 变异体总数: 6,193→6,683, 等价变异体数: 315→372
- 算法类平均覆盖率: 87.3%→87.2%
- project-data.json 新增 `framework_terminal_method_no_coverage: ~5%` 指标

### Verified
- Pattern 1 (Dominated Condition): Cast/Convert 中 `returnType == void.class` 条件被再次确认
- Pattern 7 (Counter Monotonicity): 循环迭代器 i++↔i-- 在 Collect/Permute 中被再次确认
- Pattern 20 (Wrapper VOID): 内部 List.add/Binder::add 的 VOID 移除被确认为等价
- Pattern 3 (Unconditional Return): Insert.types() 私有方法返回值在所有路径下相同

---

## [2.6.3] - 2026-06-10

### Added
- **README 提示词编写指南** — 新增完整章节：最小提示词模板、带约束提示词示例、坏提示词对照表、提示词原则（ASCII盒子）、Skill 内部执行流程图

---

## [2.6.2] - 2026-06-10

### Changed
- **行为规则前移** — 新增 🚀 LAUNCH SEQUENCE（第67行），将逐类执行/PIT优先/源码零修改/编译验证 4 条核心规则从第1181行 Workflow 提前到第2屏。AI 不需要读完 1100 行知识就能被约束
- 修复 `## Quick Reference` 标题被错误替换为重复的 `## When to Use`

---

## [2.6.1] - 2026-06-10

### Fixed
- **HARD GATE 仍被跳过** — AI 仍输出 "covering all N business classes"。修复：在 Overview 后新增 ⛔ EXECUTION PROTOCOL 章节（最显眼位置），含违规示例 + 自检机制 + 单文件特殊说明。BEFORE YOU START 新增 @Test 注解计数自检和 "SAY OUT LOUD" 确认步骤

---

## [2.6.0] - 2026-06-10

### Added
- **Iron Rule 8: Zero Source Modification** — 严禁修改源码/配置/pom.xml，只能新增测试代码。不可杀死时须文档化等价变异体
- **Iron Rule 9: Equivalent Mutant Accountability** — 等价变异体精确评估标准表格（变异算子+行号+逻辑证明+模式匹配），禁止笼统描述
- **BEFORE YOU START 强制类清单** — 写测试前必须先列出所有业务类、按复杂度排序、标记当前处理类🔄
- **PER-CLASS GATE** — 每个类完成后的强制检查点（复选框格式），禁止在PIT确认前推进到下一个类
- **Self-Optimization Hook v2** — 从4步扩展为7步：新增 Step 4 语义化版本规则、Step 6 README.md 自动同步、Step 7 project-data.json 版本更新
- **语义化版本规则** — PATCH (修正) / MINOR (新模式/项目) / MAJOR (重构)，版本严格递增：2.4.1→2.4.2→...→2.4.9→2.5.0
- **README 自动同步清单** — 10 个必更新字段的 checklist

### Changed
- **Iron Rule 6: HARD GATE 重构** — 从散文描述改为 ASCII 盒子强制逐类 PIT 循环，明确违规后果（删除多余测试、重新开始）
- **Step-by-Step Workflow** — 重命名为 Per-Class Loop，强调不可批处理多个类
- **Self-Optimization Hook** — 重写 Step 2 为决策矩阵、新增版本号决策表、Delta Detection 增加 Version 列
- **README.md** — 全局数字与 skill.md 同步（18→19 项目、19→20 模式、21→23 测试模式、11→14 等价模式、7→9 Iron Rules、1475→1863 行）

### Fixed
- Iron Rule 6 被跳过：AI 写完所有类测试才跑 PIT → 改为 HARD GATE 强制执行
- Self-Optimization 缺少 README 同步机制 → 新增 Step 6
- 版本号无规则 → 新增语义化版本规则
- README 数字与 skill.md 不一致（Iron Rules 7 vs 9、模式数 19 vs 20 等）

---

## [2.5.0] - 2026-06-10

## [2.5.0] - 2026-06-10

### Added
- **FastJson 项目** (551 mutants, 68% killed) — Alibaba fastjson 1.2.70 包装器项目实战案例
- **Pattern 20: Wrapper-Project VOID Equivalence** — 包装器项目中最常见的等价变异体模式
  - 24/82 VOID_METHOD_CALL 在库内部对象上等价 (parser.close, handleResovleTask)
  - 识别方法：库对象是局部变量 + 不存储在字段中 + 方法返回后丢弃 = void 调用等价
- **包装器项目覆盖率天花板** — 新概念：不同类型项目有不同的覆盖率上限
  - 包装器项目: ~65-75% / 算法项目: ~85-95% / GUI项目: ~25-60%
- **3 个新测试技术:** assertSame 杀 instanceof 条件, NonStandardBean invoke 分支, 有序Map构造器验证
- **4 条新 Common Mistakes 条目** — 包装器VOID等价、assertSame技术、包装器vs叶子null检查、项目类型天花板
- **FastJson Post-Mortem** — 177 幸存变异体分类 (95 真等价 + 44 不可达 + 38 环境限制)

### Changed
- 项目数: 18→19, 变异体总数: 5,642→6,193, 算法平均覆盖率: 88.9%→87.3%

### Verified
- Pattern 1-19 全部被 FastJson 项目再次验证
- 包装器项目等价率: ~32% (177/551) — 远高于算法项目 ~2.5%

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
