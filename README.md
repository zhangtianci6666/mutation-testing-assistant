# Mutation Testing Assistant

> 基于 18 个 Java 项目、5,642 个变异体实战经验提炼的 PIT 变异测试知识库——系统化分析存活变异体、识别等价变异体、编写杀活测试。

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Java](https://img.shields.io/badge/Java-8%2B-orange)](https://adoptium.net/)
[![JUnit](https://img.shields.io/badge/JUnit-5-green)](https://junit.org/junit5/)
[![PIT](https://img.shields.io/badge/PIT-1.15%2B-red)](https://pitest.org/)

---

## 这是什么？

一套完整的 **PIT 变异测试实战方法论**，提炼自 18 个真实 Java 项目的变异测试经验——涵盖算法类（B+Tree、链表、加密、排序）、CLI 解析器、GUI/Animation 等多种项目类型。帮助 Java 开发者：

- 🎯 **快速定位**——将存活变异体匹配到 19 个已知存活模式
- ⚡ **精准杀活**——使用 21 个测试模式 + 反射/内部状态探查等高级技巧
- 🛡️ **避免浪费**——识别 11 种真等价变异体，不投入无效测试
- 📊 **读懂指标**——理解 Line Coverage / Mutation Coverage / Test Strength 的关系

## 快速上手

1. **运行 PIT** 生成变异测试报告（先于任何源码分析）
2. **打开报告** 查看 SURVIVED 变异体列表
3. **匹配模式** 对照 [Quick Reference](#quick-reference-survival-patterns) 19 个存活模式
4. **应用策略** 按对应 killing rule 编写测试
5. **重跑 PIT** 验证杀活效果

```bash
# Maven PIT 插件运行
mvn org.pitest:pitest-maven:mutationCoverage

# 务必先验证编译
mvn test-compile
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

完整文档见 [skill.md](./skill.md)（1475 行），关键章节：

| 章节 | 内容 |
|------|------|
| [Quick Reference](./skill.md#quick-reference-survival-patterns) | 19 个存活模式速查表 |
| [Mutation Operators](./skill.md#mutation-operators--killing-rules) | 9 大变异算子 + 杀活策略 + 代码示例 |
| [Survival Patterns](./skill.md#survival-patterns--killing-strategies) | 19 个模式分三类：🟰 真等价 / 🔧 可杀死 / 🛠️ 杀活技巧 |
| [Test Patterns Catalog](./skill.md#test-patterns-catalog-从18个项目提取) | 21 个测试模式 + 代码模板 |
| [B+Tree Testing](./skill.md#btree--recursive-data-structure-testing-rules) | B+Tree 专项：t值选择、增量构建、断言升级阶梯 |
| [GUI Testing](./skill.md#awtgui-class-testing-rules) | AWT/Animation：Headless兼容、Counting Subclass、动画等价识别 |
| [Case Studies](./skill.md#project-case-studies-18个项目实战经验) | 18 个项目实战复盘 |
| [Workflow](./skill.md#workflow) | 7 条 Iron Rules + 22 步完整工作流 |
| [Common Mistakes](./skill.md#common-mistakes) | 30+ 个高频踩坑点 |
| [PIT Metrics](./skill.md#interpreting-pit-metrics) | Line Coverage / Mutation Coverage / Test Strength 诊断指南 |

## 项目数据

来自 18 个 Java 项目的真实变异测试数据：

| 指标 | 数值 |
|------|------|
| 分析项目数 | 18 |
| 总变异体数 | 5,642 |
| 算法类平均覆盖率 | 88.9% |
| 等价变异体数 | 220 |
| GUI/Animation 可测上限 | 25-60% |

详见 [project-data.json](./data/project-data.json)

## 贡献

欢迎提交 Issue 和 PR！详见 [CONTRIBUTING.md](./CONTRIBUTING.md)

## 贡献者

- [zhangtianci6666](https://github.com/zhangtianci6666) — 项目发起人、主要作者

## 开源协议

[Apache License 2.0](./LICENSE) — 与 PIT 项目保持一致
