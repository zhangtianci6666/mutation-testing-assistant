# Changelog

All notable changes to the Mutation Testing Assistant will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [v2.7.0] - 2026-10-19

> **版本纪律：一日一版。** 同一自然日的多次改动累计合并为本条，编号只在上一已提交版本（v2.6.1）上递增一档（MINOR），不跳号。本条目 = 上午的 P23/P24/TP26-28 + 下午的 P25/TP29/TP30 与案例库修正。

### Added
- **P23 Fixed-Point Clamp 三类逃生口** — ① ±0.0 符号位 ② 隐藏状态破坏不变量（构造器允许越界 → `releaseHours(0)` 从"无操作"变成"归一为上限"）③ 后续算术吸收（吸收掉才是真等价）
- **P24 Floor-Masked Lower Clamp** — 下限钳制被后续 `max()/floor` 吞掉，REMOVE_CONDITIONALS 不可观测
- **P25 Duplicate Scan Mutual Masking** — 同方法两段循环同区间同谓词、后段带 `if(!found)` 守卫时，任一侧被削弱都会被另一侧补回，块内变异体互相不可观测；判定法是先 diff 两段循环再决定是否写测试，并把重复扫描作为源码缺陷上报（Credit-Card-Validator 的 `650002-650027` 整段因此被静默禁用）
- **TP26 黄金序列 + 位布局反射** — 固定种子 PRNG 用黄金序列逐值精杀移位变异；时间相关 ID 用 `before==after` 毫秒窗口 + 反射读计数器反算
- **TP27 异常消息区分** — 统一异常出口（catch 后重包装）会让 `assertThrows(类型)` 失效，必须升级到 `getMessage()`
- **TP28 边界等价体三类逃生口** — 含三段可直接复用的测试代码
- **TP29 静态工具类实例化** — 只含静态方法的类，隐式构造器被 JaCoCo 记在类声明行；从未 `new` 过则行覆盖永远差这一行，`assertNotNull(new XxxUtil())` 一行补一个类
- **TP30 对照实验取证（Counterfactual Probe）** — 项目外临时副本只改疑似源码缺陷、同一套测试重跑 PIT：存活体成批死亡即证明等价性源于源码而非测试不足（实测 96% → 99%）
- **pit-metrics「Locating the Last 1%」** — 解析 `jacoco.xml` 的 `mi/mb` 逐行定位缺口，附 4 种缺口形态的判读与处置表
- 12 条 common-mistakes（10 + 2）：异常类型断言、ID/PRNG 弱断言、依赖链累加假设、`floorEntry` 语义、构造器 clamp 未核对、见钳制就判等价、用 delta 比较 ±0.0、只按合法区间设计输入、EMPTY_RETURNS 一律判等价、99% 缺口全落在类声明行、3 个分支差 1%~2% 就硬凑
- **Research-Project-Management-System** — 14 业务类、305 变异体、281 击杀（92%）、JaCoCo 全 100%
- **Credit-Card-Validator 重跑** — 32 业务类、272 变异体、261 killed + 1 timed_out、10 个真等价（上限 96%）；单文件 67 个 `@Test`

### Fixed
- **P23 判定过于绝对（重要修正）** — 初版写"钳制边界一律等价、不要再写测试"，被复检证伪：30 个存活体里有 6 个（20%）可杀。P23 现改为"先试 3 类逃生口，全不成立才判等价"，并附判定流程图
- **`assertEquals(a,b,delta)` 看不见 ±0.0** — 补入逃生口①：`x < 0` 与 `x <= 0` 在 `x = -0.0` 处结论相反，必须用 `Double.doubleToRawLongBits`
- **`project-case-studies.md` 中 `Credit-Card-Validator (255 mutants, 100% killed)` 属错误结论** — 在给定 pom（`DEFAULTS` + `targetClasses=net.mooctest.*`）下实测 272 个变异体、10 个真等价、**上限 96.3%**。已改写为如实的 96% ceiling 并录入逐条证明与对照实验；该旧记录是"该项目可达 100%"误判的来源

- **自优化机制的三处结构缺陷** — ① `Step 5` 全文审计排在写入之前，审计表却在检查尚未写出的 CHANGELOG/README/JSON，导致"审计通过即收工"而漏写 CHANGELOG（本次事故的直接成因）→ 重排为"先落盘 Step 3-8、再审计 Step 9"；② `Step 4a` 的回读校验引用未定义变量 `v_new`，复制即 `NameError`，"同日条目数==1"只有注释没有代码 → 改为可独立运行的校验代码；③ 检查清单漏 `changelog[0]` 与 `CHANGELOG.md` 的联动
- **统计恒等式差 1** — `killed(7975) + survived(2459) = 10434 ≠ total(10435)`，survived 修正为 2460（Credit-Card-Validator 重跑含 1 个 TIMED_OUT）
- **`test-patterns-catalog.md` 文首计数过时** — 写 "22 reusable test patterns"（实有 30）、"从24个项目提取"（实为 26）；同时暴露出该文件存在两套标题格式（`### 12.` 与 `### Pattern 24:`），校验脚本已兼容

### Changed
- **自优化机制加固** — 两档触发（单类完成只记录 post-mortem、项目结束统一落盘）；Step 4 新增"统计 5 副本对齐"；审计后置为 Step 9；Step 10 回读校验；新增"新模式准入门槛"（实证 + 反证尝试 + 可判定 + 不复述）；**移除全部 git 快照/自动提交**，版本控制完全由人工负责
- 新增 `scripts/check_stats.py`（只读）：校验 metadata / summary / projects 明细 / README / SKILL.md 五处统计与模式计数
- **本次加固自身违反了两条新规则，已修** — ① 新增 P25 后 `SKILL.md` 仍有 4 处 `P1-P24`、1 处 `all 24 patterns`、1 处 `16 operators, 24 patterns` 未同步（正是"改模式必须连带改引用"要防的）；② `SKILL.md` Overview 仍写 `10,418+ mutants` 与 `11 mutation operators`（实为 10,435 / 16），而 Step 4 的 5 副本表当时没覆盖 Overview，`check_stats.py` 也没校验 → 两处均逃过检查
- **`scripts/check_stats.py` 扩展** — 新增：SKILL.md Overview 的项目/变异体/运算符数、全文 `P1-P{N}` 与 `all N patterns` 硬编码上限、运算符数与 JSON `supported` 对齐；已用"故意写坏 P1-P25→P1-P24"做过回归自测（FAIL 后还原）
- 本条为当日追加，版本号保持 v2.7.0（一日一版，不新开版本）
- 项目 25→26；变异体 10,113→10,435；存活模式 22→25；测试模式 25→30
- 累计击杀 7,688→7,975；等价体 498→532（等价率 3.7%）
- 版本号纠正：本条目曾误记为 v2.8.0/v2.9.0，现按"一日一版、不跳号"收敛为 v2.7.0（同日改动已全部并入）

---

## [v2.6.1] - 2026-07-23

### Added
- **Online-Edu 在线教育平台项目** (1,388 mutants, 43% mutation, 85% line, 9 业务类) — Spring Boot 3.5 服务架构（6 个大型 Service：考试评分/学习进度/报名资格审查/退款策略/高级定价/排课调度 + 3 个小型 Service）
- 单文件聚合 ~5,400 行、450+ 测试；PIT 4%→34%→43%，JaCoCo 9%→72%→85% 行 / 73% 分支 / 96% 方法
- **包级私有 Spring `@Bean` 反射覆盖技术**；Record 紧凑构造器 `List.copyOf` 拒绝 null 造成验证死分支；验证主导死分支（P1：`maximumPoints.signum()==0` 被前置验证屏蔽）
- 3 条 common-mistakes：`Mockito.when` 非 mock 对象、类型推断 `Set.of()/List.of()`、sed 批处理破坏 Java 源码

---

## [v2.6.0] - 2026-07-23

### Added
- **OASYS 企业OA系统项目** (1012 mutants, 55% killed, 93% line, 19类) — 大型企业应用含考勤/费用/权限/工作流/休假5个子系统
- **P21 Grade Multiplier Switch Gap** — switch-enum中间值(SENIOR/MANAGER)未覆盖导致REMOVE_CONDITIONALS存活
- **P22 Record Compact Constructor NPE** — Java Record紧凑构造器中调用实例方法访问未赋值字段导致NPE
- **TP24 Single-File @Nested Aggregation** — 使用@Nested类在单文件中聚合500+测试
- **TP25 JaCoCo + PIT Dual Analysis** — 互补使用JaCoCo(行/分支/方法)和PIT(变异)的双覆盖分析策略

### Changed
- 项目总数: 23→24, 变异体总数: 7,713→8,725
- SKILL.md Quick Reference: 20→22 存活模式, 23→25 测试模式
- common-mistakes.md: 新增6条(含Maven source level/Record NPE/工厂参数过多)
- survival-patterns.md: 新增P21+P22
- test-patterns-catalog.md: 新增TP24+TP25
- project-data.json: 版本 v2.5.4→v2.6.0, 新增OASYS项目条目

### Verified
- 方法覆盖100% (164/164), 类覆盖100% (60/60)
- JaCoCo分支覆盖80% (329/1674 missed), 行覆盖95%
- PIT变异覆盖55% (561/1012 killed)
- 单文件聚合策略在大项目中可行(5500+行, 500+测试)

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
