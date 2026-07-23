# Mutation Testing Assistant

> 基于 24 个 Java 项目、8,725 个变异体实战经验提炼的 PIT 变异测试知识库——系统化分析存活变异体、识别等价变异体、编写杀活测试。

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Java](https://img.shields.io/badge/Java-8%2B-orange)](https://adoptium.net/)
[![JUnit](https://img.shields.io/badge/JUnit-5-green)](https://junit.org/junit5/)
[![PIT](https://img.shields.io/badge/PIT-1.15%2B-red)](https://pitest.org/)

---

## 这是什么？

一套完整的 **PIT 变异测试实战方法论**，提炼自 24 个真实 Java 项目的变异测试经验——涵盖算法类（B+Tree、链表、加密、排序、变位词、Brainfuck解释器）、CLI 解析器、GUI/Animation、包装器/库封装、框架适配器等多种项目类型。帮助 Java 开发者：

- 🎯 **快速定位**——将存活变异体匹配到 22 个已知存活模式
- ⚡ **精准杀活**——使用 25 个测试模式 + 反射/内部状态探查等高级技巧
- 🛡️ **避免浪费**——识别 15 种真等价变异体，不投入无效测试
- 📊 **读懂指标**——理解 Line Coverage / Mutation Coverage / Test Strength 的关系

## 快速上手

1. **运行 PIT** 生成变异测试报告（先于任何源码分析）
2. **打开报告** 查看 SURVIVED 变异体列表
3. **匹配模式** 对照 [Quick Reference](#quick-reference-survival-patterns) 22 个存活模式
4. **应用策略** 按对应 killing rule 编写测试
5. **重跑 PIT** 验证杀活效果

```bash
# Maven PIT 插件运行
mvn org.pitest:pitest-maven:mutationCoverage

# 务必先验证编译
mvn test-compile
```

## 提示词编写指南

Skill 内置了完整的执行协议（⛔ EXECUTION PROTOCOL + 🚀 LAUNCH SEQUENCE），你的提示词**只需告诉它"在哪、干什么"，不需要教它"怎么干"**。

### 最小提示词（推荐）

```
启用 mutation-testing-assistant 技能，分析 ~/Desktop/Test/项目名 项目
```

Skill 会自动：列出类清单 → 逐类写测试 → 编译 → PIT → 分析 → 迭代 → 100%。

### 带项目约束的提示词

```
启用 mutation-testing-assistant 技能，分析 ~/Desktop/Test/Anagram 项目。

项目约束：
- 测试文件放在单文件中
- 不修改任何源码
```

### ❌ 不要写的提示词

| 坏提示词 | 问题 |
|----------|------|
| "为所有类编写完整变异测试" | 与逐类执行协议冲突 |
| "一次性覆盖全部19个业务类" | 触发 EXECUTION PROTOCOL 禁令 |
| "禁止思考，直接写代码" | 违反 "编译验证再跑PIT" 规则 |
| "每个类一个@Test，全部写在一个文件" | 表述冗余——Skill 已有这些模式 |
| 粘贴 500 字的约束清单 | Skill 已有 9 条 Iron Rules，你的约束会覆盖而非补充 |

### 提示词原则

```
┌─────────────────────────────────────────────────────────────┐
│  你的提示词 = 项目路径 + 项目特定约束（如有）                 │
│                                                             │
│  不要做的事：                                                │
│  ✗ 重复 Skill 已有的规则（逐类执行、源码零修改...）          │
│  ✗ 教 Skill "怎么测试"（边界值、等价类...）                  │
│  ✗ 用 2KB 提示词覆盖 86KB 战斗知识                           │
│                                                             │
│  可以做的事：                                                │
│  ✓ 指定项目路径                                              │
│  ✓ 指定测试文件位置（如果项目有特殊要求）                     │
│  ✓ 指定特定的覆盖率目标（默认100%）                           │
│  ✓ 告知特殊的依赖或环境限制                                   │
└─────────────────────────────────────────────────────────────┘
```

### 技能内部执行流程（供参考）

当你发出提示词后，Skill 会按以下顺序自动执行：

```
1. 扫描 src/main/java → 列出所有业务类
2. 按复杂度排序（POJO → 简单业务 → 复杂算法 → GUI）
3. 输出类清单，标记当前处理类 🔄
4. 【逐类循环开始】
   a. 为当前类写 @Test 方法
   b. mvn test-compile → 修复编译错误
   c. mvn pitest:mutationCoverage → 生成变异报告
   d. 读取报告，匹配存活变异体到 22 个模式
   e. 等价变异体 → 文档化；可杀死 → 补测试 → 回到 b
   f. 100% 或等价已记录 → 推进到下一个类
   g. 检查是否应更新 Skill 自身（新模式？→ 自动优化）
5. 输出 Post-Mortem 分析报告
```

## 适用场景

| ✅ 适用 | ❌ 不适用 |
|---------|-----------|
| PIT 变异测试覆盖率低于目标（<80%） | 通用单元测试指导（非变异测试） |
| 特定变异算子大量存活（BOUNDARY, VOID_CALL, MATH 等） | 其他变异测试工具（非 PIT） |
| 需要区分可杀变异体和等价变异体 | |
| GUI/AWT/Animation 类的变异测试 | |
| B+Tree / 递归数据结构的覆盖率提升 | |
| 泛型 / 多态继承项目的编译验证 | |

## 技术栈

| 组件 | 版本 |
|------|------|
| Java | 8+ |
| JUnit | 5 |
| PIT (Pitest) | 1.15+ |
| Mockito | 配合 AWT/Graphics mock |
| Maven | pitest-maven 插件 |

## 内容导航

采用三层加载模型控制Token消耗：

```
Tier 1 (Always):    description 字段 → 永远在上下文中
Tier 2 (Trigger):   SKILL.md (281行) → 核心协议 + 路由表，触发时加载
Tier 3 (On-Demand): references/*.md  → 详细内容，用到才读
```

### 路由表（SKILL.md，281 行）

SKILL.md 不包含详细内容，而是告诉模型**什么时候去读哪个文件**：

| 遇到什么情况 | 读哪个文件 |
|-------------|-----------|
| 变异体匹配到某个模式，需要详情 | [survival-patterns.md](references/survival-patterns.md) — 22个模式：症状、根因、代码、行动 |
| 需要某种操作符的杀活代码 | [killing-strategies.md](references/killing-strategies.md) — 11种操作符 + 快速杀活决策树 |
| 需要特定测试技巧（反射、计数子类等） | [test-patterns-catalog.md](references/test-patterns-catalog.md) — 25个测试模式 + 代码 |
| 处理 B+Tree / 递归数据结构 | [bplustree-testing.md](references/bplustree-testing.md) — t值选择、断言升级阶梯 |
| 处理 AWT/Swing/GUI 类 | [awt-gui-testing.md](references/awt-gui-testing.md) — Headless兼容、Graphics mock |
| 想对测试做 sanity check | [common-mistakes.md](references/common-mistakes.md) — 46+常见错误 + 36+红旗检查 |
| 需要解读 PIT 报告指标 | [pit-metrics.md](references/pit-metrics.md) — 覆盖率统计、诊断矩阵 |
| 想参考类似项目经验 | [project-case-studies.md](references/project-case-studies.md) — 24个项目深度复盘 |
| PIT 跑完后（自动优化） | [self-optimization.md](references/self-optimization.md) — 7步Post-Mortem工作流

## 项目数据

来自 24 个 Java 项目的真实变异测试数据：

| 指标 | 数值 |
|------|------|
| 分析项目数 | 24 |
| 总变异体数 | 8,725 |
| 算法类平均覆盖率 | 87.3% |
| 等价变异体数 | 430 |
| GUI/Animation 可测上限 | 25-60% |
| 包装器/库封装类可测上限 | 65-75% |

详见 [project-data.json](./project-data.json)

## 贡献

欢迎提交 Issue 和 PR！详见 [CONTRIBUTING.md](./CONTRIBUTING.md)

## 贡献者

- [zhangtianci6666](https://github.com/zhangtianci6666) — 项目发起人、主要作者

## 开源协议

[Apache License 2.0](./LICENSE) — 与 PIT 项目保持一致
