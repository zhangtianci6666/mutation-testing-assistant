# Contributing to Mutation Testing Assistant

感谢你的贡献兴趣！本项目是一个社区驱动的变异测试知识库，欢迎任何形式的贡献。

## 贡献方式

### 报告问题

通过 [GitHub Issues](https://github.com/zhangtianci6666/mutation-testing-assistant/issues) 提交：

- **Bug 报告**：数据错误、代码示例 bug、技术表述不准确
- **内容建议**：缺失的变异算子、测试模式、FAQ 问题
- **文档改进**：表述不清、排版问题、翻译建议

### 提交 PR

1. Fork 本仓库
2. 从 `develop` 分支创建你的 feature 分支：`git checkout -b feature/my-contribution`
3. 做出修改并提交：`git commit -m "feat: add SWITCH_MUTATOR killing guide"`
4. 推送到你的 fork：`git push origin feature/my-contribution`
5. 创建 Pull Request 到 `develop` 分支

### PR 规范

- 一个 PR 做一件事（避免混合多个不相关的修改）
- 描述清楚你做了什么、为什么这样做
- 涉及数据修改时提供依据（源码截图、PIT 报告片段等）

## 文档规范

### Markdown 风格

- 代码块必须标注语言：` ```java `
- 表格使用对齐格式
- 标题层级不超过 3 级（`###`）

### 代码示例规范

- **JUnit 5 语法**：使用 `@Test`、`@BeforeEach`、`assertThrows()`，禁止 JUnit 4 风格
- 代码示例必须是自解释的（关键变量有注释）
- 变异测试代码需标注目标变异算子和预期杀活效果

```java
// ✅ 好的示例
@Test
void testBoundaryValue() {
    // Kills CONDITIONALS_BOUNDARY: > → >= on threshold check
    Calculator calc = new Calculator(10); // threshold = 10
    assertEquals("AT_LIMIT", calc.process(10)); // exact boundary
}

// ❌ 不好的示例
@Test
void test() {
    Calculator c = new Calculator(10);
    assertNotNull(c.process(10)); // 弱断言，无法杀死边界变异
}
```

### 术语规范

| 中文 | English | 备注 |
|------|---------|------|
| 变异体 | Mutant | 不使用"突变体" |
| 存活 | Survived | |
| 杀死/杀活 | Kill | |
| 等价变异体 | Equivalent Mutant | |
| 变异算子 | Mutation Operator / Mutator | |

### 数据维护

如需更新 `project-data.json`（如添加新项目数据），必须同步更新：
1. `skill_metadata` — 项目数、变异体总数、平均覆盖率
2. `project_statistics.summary` — 同上
3. `project_statistics.projects` — 项目列表
4. `skill.md` 中的 Overview 行和 Coverage Statistics 表

三个位置的数据必须一致。

## 分支管理

```
main          ← 稳定发布版
develop       ← 开发集成分支
feature/*     ← 新功能 / 新内容
fix/*         ← Bug 修复
docs/*        ← 纯文档修改
```

## 行为准则

- 尊重所有贡献者
- 建设性讨论技术问题
- 保持文档质量优先

## 许可证

贡献的代码/文档默认采用本项目的 [Apache 2.0 License](./LICENSE)
