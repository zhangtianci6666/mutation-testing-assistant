# Self-Optimization Hook (自动优化机制) — Full Steps

定义"跑完 PIT 之后如何把经验写回知识库"。核心顺序：**先落盘 → 再审计 → 最后回读校验**。
版本号一律**从文件推导**，不凭记忆。

---

## 触发档位（先判断档位，不要一律跑全流程）

| 时机 | 做什么 | 改文件？ |
|---|---|---|
| 单个业务类跑完 | 只在会话里记 Step 1 的 post-mortem 要点 | ❌ 不落笔 |
| 项目全部类完成 / 会话收尾 / 用户明确要求"更新技能" | 执行 Step 2 → Step 10 一次 | ✅ |
| 同一天第二次及以后 | 不新开版本，改动**追加**进当日条目 | ✅ |

> **不使用 git 快照或自动提交。** 版本控制由用户人工负责；本机制内不得执行 `git add / commit / push`。
> 唯一的保护链是：改前读全文 → 单文件单次改 → 改后回读校验（Step 10）。

---

## Step 1: Post-Mortem Analysis（单类完成时，只记录不落笔）

```
## Post-Mortem: {PROJECT_NAME}

### Basic Stats
- Project: {name}
- Type: {algorithmic|GUI|CLI|data-structure|etc}
- Total mutants: {N}
- Killed: {N} ({X}%)
- Equivalent mutants identified: {N}
- Final mutation coverage: {X}%
- Time spent: {N} minutes

### Survivor Breakdown
| Mutator | Survived | Equivalent? | Pattern Match | Action |
|---------|----------|-------------|---------------|--------|

### New Discoveries (if any)
- [ ] New equivalent mutant pattern found?
- [ ] New killing technique discovered?
- [ ] Existing pattern needs correction?
- [ ] New test pattern invented?

### Skill Knowledge Gap Analysis
- Which survivors did the skill NOT predict? Why?
- Which predicted patterns were WRONG for this project?
- What project-specific knowledge should be generalized?

### Coverage Statistics Update
- New entry for project-data.json
```

---

## Step 2: Determine Update Type

| Condition | Action | Tool |
|-----------|--------|------|
| New equivalent pattern discovered | Add to references/survival-patterns.md, assign next Pattern ID | Edit |
| New killing technique found | Add to references/killing-strategies.md | Edit |
| Existing pattern confirmed correct | No change needed | - |
| Pattern description inaccurate | Update pattern section **+ 连带更新所有引用点**（见表） | Edit |
| New test pattern invented | Add to references/test-patterns-catalog.md | Edit |
| New project completed | Add to references/project-case-studies.md, update stats | Edit |
| New project completed | Add entry to project-data.json | Edit |
| Common Mistakes table has gap | Add new row to references/common-mistakes.md | Edit |
| Quick Reference table has gap | Add new row to SKILL.md Quick Reference | Edit |
| 机制本身被证伪 / 步骤跑不通 | 改本文件，并在 CHANGELOG 的 `Fixed` 留痕 | Edit |

**改一条模式，必须连带检查的引用点：**

| 引用点 | 检查什么 |
|---|---|
| `SKILL.md` Quick Reference | 该模式那一行的结论/动作是否仍成立 |
| `references/test-patterns-catalog.md` | 是否有 TP 依赖该模式的结论 |
| `README.md` | 模式总数、等价变异体数是否需要改 |
| `project-data.json` → `survival_patterns_index` | 条目是否需增补/改名 |
| 其他 P/T 条目正文 | `grep -n "P{N}\|Pattern {N}"` 逐条看有无交叉引用 |

---

## Step 3: Execute Knowledge Edits

按 Step 2 识别的动作立即落笔（项目内不要把改动堆到最后）。三条约束：

1. **一次只改一个主题**，改完立刻回读该段落确认写入。
2. **不要在同一个文件里做大面积重排**；确需重写，先读全文再整体 Write。
3. **删除/改写既有结论时必须留痕**：CHANGELOG 的 `Fixed` 段写清"原结论 → 新结论 → 证据"。

---

## Step 4: 统计数字统一（5 处副本，必须全部对齐）

同一组数字散落在 5 个位置，改一处必须同步其余四处：

| 位置 | 字段 | 由什么推导 |
|---|---|---|
| `project-data.json` → `skill_metadata` | total/killed/survived/equivalent | 各项目累加 |
| `project-data.json` → `project_statistics.summary` | 同名字段 | 必须与上一行**完全相同** |
| `project-data.json` → `project_statistics.projects[]` | 每项目 mutants | 明细，累加后应等于 total |
| `README.md` | 头部"X 个项目、Y 个变异体" + 项目数据表 3 行 | 同 JSON |
| `SKILL.md` | Overview：项目数 / 变异体数 / 运算符数 / 模式数 | 同 JSON 与 Quick Reference 实际行数 |
| 全文任意位置 | `P1-P{N}`、`all N patterns` 这类**硬编码上限** | 必须等于当前模式总数；新增模式后最易漏 |

**恒等式（必须成立）：** `total = killed + survived`。

跑校验：`python scripts/check_stats.py`（不一致即 FAIL，退出码 1）。

---

## Step 5: Version Bump（读文件 / 一日一版 / 只进一档）

先跑只读校验器，它会双读版本、检查当日条目数，直接给出唯一合法候选：

```bash
python scripts/next_version.py
```

**版本号必须从文件读出来，不能凭记忆写。** 历史上出现过 `v2.6.1 → v2.8.0 → v2.9.0` 的跳号，根因就是"没读文件、按印象写了个大版本"。

三条判定，顺序执行、不允许跳步：

| 情况 | 动作 |
|---|---|
| ① CHANGELOG 最新条目日期 == 今天 | **不新增版本**；改动追加进该条目，`version` 保持不变 |
| ② 跨日，且本次只改统计/纠错 | 前进 **PATCH** 一档：`vX.Y.Z → vX.Y.(Z+1)` |
| ③ 跨日，且本次有新模式/新测试模式/新项目 | 前进 **MINOR** 一档：`vX.Y → vX.(Y+1).0`（`Z` 归零） |

**禁止跳号：** 每次只能 `+1` 一档。`v2.6.1 → v2.7.0` 合法；`v2.6.1 → v2.8.0`、`v2.8.0 → v2.9.0` 均非法。跨大版本仅限整章重构。

**一日一版：** 同一自然日的多次改动（含多次会话、自动化）必须落在**同一条目**里，不允许出现两个同日期条目；最多在条目顶部注明"本条目合并了当日第 N 次改动"。

**写入必须三处联动**（漏一处就是"changelog 没变动 / 摘要对不上"的事故）：

| 位置 | 写什么 |
|---|---|
| `CHANGELOG.md` | 人读条目（Added / Changed / Fixed） |
| `project-data.json` → `skill_metadata.version` | 同一版本号 |
| `project-data.json` → `skill_metadata.changelog[0]` | 以 `vX.Y.Z: ` 开头的摘要 |

写完立刻回读（可直接用脚本，也可粘下面这段；变量均已定义，可独立运行）：

```python
import json, io, re, datetime
data = json.load(open('project-data.json', encoding='utf-8'))
v    = data['skill_metadata']['version']
log  = io.open('CHANGELOG.md', encoding='utf-8').read()
heads = re.findall(r'^## \[(v\d+\.\d+\.\d+)\] - (\d{4}-\d{2}-\d{2})', log, re.M)
assert v == heads[0][0],               f'版本不一致: json={v}, changelog={heads[0][0]}'
assert data['skill_metadata']['changelog'][0].startswith(v + ':'), 'changelog[0] 未同步'
assert sum(1 for _, d in heads if d == datetime.date.today().isoformat()) == 1, '今日出现多个版本条目'
print('版本三处一致:', v)
```

---

## Step 6: Write CHANGELOG.md

```
## [v{NEW_VERSION}] - {DATE}

### Added
- {Project} project case study ({N} mutants, {X}% killed)
- Pattern {N}: {name} ({category})

### Fixed
- {原结论} → {新结论}，证据：{项目/行号/PIT 实测}

### Changed
- {What was modified and why}

### Verified
- {Which existing patterns were confirmed by this project — 没有就写 "none"}
```

`### Verified` 不可省略：它是"哪些结论本轮被复验过"的唯一痕迹；长期缺失会让知识库无法评估老化。

---

## Step 7: Update project-data.json

- `skill_metadata.version` + `last_updated`
- `skill_metadata.changelog[0]`（摘要，与 CHANGELOG 同义）
- `project_statistics.summary` 与 `skill_metadata` 的四个计数
- `project_statistics.projects[]`：新增/更新项目条目
- `survival_patterns_index` / `test_patterns_index`：新条目

改完 `python -c "import json;json.load(open('project-data.json'))"` 确认可解析。

---

## Step 8: Update README.md

| README Field | When to Update |
|-------------|---------------|
| Header: "X 个项目、Y 个变异体" | 项目/变异体数变化 |
| "提炼自 X 个真实 Java 项目" | 新项目 |
| "N 个已知存活模式" | 新模式（MINOR） |
| "N 个测试模式" | 新测试模式 |
| "N 种真等价变异体" | 新等价模式 |
| "N 条 Iron Rules" | 新 Iron Rule |
| 项目数据表（分析项目数/总变异体数/等价变异体数） | 统计变化 |
| `SKILL.md (NNN 行)` | 行数变化（**注意大小写：正文用 `SKILL.md`**） |
| "N 步完整工作流" | 流程步骤变化 |
| "N+ 个高频踩坑点" | common-mistakes 增长 |

---

## Step 9: FULL REFERENCE AUDIT（**最后执行**，在所有写入之后）

⚠️ 顺序很关键：审计必须在 Step 3-8 全部落盘之后，否则审计表里的 CHANGELOG/README/JSON 三项永远在"检查还没写的东西"。

Review EVERY reference file — not just the one with new knowledge:

| File | Check |
|------|-------|
| `survival-patterns.md` | 描述不准确？缺变体？Action 写错？ |
| `killing-strategies.md` | 策略不足？示例代码杀不掉？缺子技巧？ |
| `test-patterns-catalog.md` | 示例有 bug？缺关键规则？交叉引用是否仍成立？ |
| `common-mistakes.md` | 本轮踩的坑没列？已列的修法是错的？ |
| `bplustree-testing.md` | （树项目）规则需细化？缺断言层级？ |
| `awt-gui-testing.md` | （GUI 项目）模式有误？缺 headless 变通？ |
| `pit-metrics.md` | 诊断矩阵是否仍准确？项目对比表是否更新？ |
| `SKILL.md` | Quick Reference 全对？Overview 计数对？Iron Rules 完整？Pattern 上限是否写死过时数字？ |
| `project-data.json` | 版本、统计、changelog、索引四者一致？ |
| `README.md` | 计数、项目表、过时结论？ |
| `CHANGELOG.md` | 条目完整？`Fixed` 列了纠正而非只有新增？`Verified` 有内容？ |
| `self-optimization.md`（本文件） | 本轮是否有步骤跑不通？有则改，并在 CHANGELOG `Fixed` 记一笔 |

**"Nothing to fix" 只有在你真的逐个读过并核对后才成立。**

---

## Step 10: 回读校验 & Checklist

```bash
python scripts/next_version.py     # 版本三处一致 + 今日条目唯一
python scripts/check_stats.py      # 5 处统计副本对齐
```

- [ ] Post-mortem 已填（单类阶段完成）
- [ ] 所有存活体匹配到已知模式，或按"准入门槛"新增模式
- [ ] 等价变异体逐条有证明（Iron Rule 9 格式）
- [ ] 版本号来自文件，且只进一档 / 当日合并
- [ ] `CHANGELOG.md` 条目含 Added / Fixed / Changed / Verified
- [ ] `project-data.json`：version + changelog[0] + 四个计数 + 项目条目 + 索引
- [ ] `README.md`：所有命中字段已同步
- [ ] 若新增模式：survival-patterns + SKILL.md Quick Reference + 索引三处齐
- [ ] 若新增测试模式：test-patterns-catalog + SKILL.md 计数
- [ ] Step 9 的 12 个文件逐个过过
- [ ] 两个校验脚本均 PASS

---

## 新模式准入门槛（P 系列 / TP 系列）

新增一条模式，必须同时满足，缺一不可入 P/TP 系列：

1. **实证**：写明项目名 + 变异体所在类/行号 + 本轮 PIT 的实测状态（KILLED / SURVIVED / TIMED_OUT）。
2. **反证尝试**：列出为杀掉它试过的技术（边界值、反射、计数子类、对照实验…）及失败原因。
3. **可判定**：给出"看到什么症状 → 判定为什么"的可操作判据，而不是一句"这种情况通常等价"。
4. **不复述**：现有模式已覆盖的，只允许加"变体"，不允许新开条号。

不满足 1/2 的，只能写进 `common-mistakes.md` 当作**疑点**，不得进入 P 系列正文。
（教训：P23 初版"钳制一律等价"当天即被证伪；`255 mutants / 100% killed` 的断言在案例库滞留数月无人复核。）

---

## Delta Detection: When to Actually Edit the Skill

You ONLY need to edit when there's a DELTA — something the skill doesn't already know:

| Situation | Delta? | Action | Version |
|-----------|--------|--------|---------|
| Survivor matches an existing pattern exactly | NO | Document in post-mortem only | PATCH |
| Survivor matches a pattern but with a new sub-type | YES | Add sub-type to existing pattern | PATCH |
| Survivor requires a completely new pattern | YES | Create Pattern N+1（过准入门槛）, update README | MINOR |
| All survivors already covered by skill | NO | Just update project-data.json stats | PATCH |
| Skill's prediction was wrong for a mutant | YES | Correct the pattern **+ 所有引用点** | PATCH |
| Found a more efficient killing method | YES | Update the pattern's killing strategy | MINOR |

**Iron Rule for self-optimization: Add knowledge, don't duplicate it.** If the skill already explains how to handle a situation, don't add another explanation.
