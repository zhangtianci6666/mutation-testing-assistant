# Coverage Statistics & PIT Metrics

## Interpreting PIT Metrics

PIT reports three metrics per class/package:
- **Line Coverage:** % of lines executed by tests
- **Mutation Coverage:** % of mutants killed by tests
- **Test Strength:** % of covered mutants that were killed

**Test Strength = Mutation Coverage / Line Coverage (roughly)**

### Diagnostic Guide

| Line Coverage | Mutation Coverage | Test Strength | Diagnosis | Action |
|---------------|-------------------|---------------|-----------|--------|
| High | Low | Low | Tests execute code but assertions are too weak | Strengthen assertions (assertEquals instead of assertNotNull, add internal state checks) |
| High | Low | High | Many equivalent mutants or uncovered edge cases | Check for equivalent patterns (1-20), then add edge case tests |
| Low | Low | N/A | Missing test coverage entirely | Add basic tests to execute uncovered lines |
| High | High | High | Healthy test suite | Maintain |

### Example from P_Queue:

- Heap.java: Line Coverage 98%, Mutation Coverage 56%, Test Strength 58%
  - Diagnosis: Code is executed, but ~42% of covered mutants survive. Many are Animation State Restoration equivalents (Pattern 9). The remaining are killable with stronger assertions or precondition manipulation.
- DrawingPanel.java: Line Coverage 87%, Mutation Coverage 25%, Test Strength 32%
  - Diagnosis: paint/update are executed but Graphics mock verifications are incomplete. `setColor` call counts and drawString parameters need precise assertions.

---

## Coverage Statistics Summary

| 项目 | 变异体数 | 覆盖率 | 关键成功因素 |
|------|----------|--------|--------------|
| CMD | 72 | 100% | 多态基类默认路径覆盖 + 反射Map状态注入 + 泛型兼容性 |
| Credit-Card-Validator | 255 | 100% | 边界值精确测试 |
| MementoX | 180 | 100% | 状态精确验证 |
| Research-Project-Mgmt | 333 | 99% | 分支全覆盖 |
| Student-Grade-System | 201 | 99% | 反射测试私有方法 |
| Nextday | 98 | 99% | 反射边界注入+数组索引全遍历+链式void副作用验证 |
| **Brainfuck** | **145** | **98%** | **initate()重置等价识别+自修正括号匹配+单文件聚合3继承类** |
| SimpleAlgorithms | 440 | 96% | 算法结果精确断言 |
| **Hotel** | **262** | **94%** | **setPrice()去耦构造器MATH+支配条件+复合死码+8类100%** |
| UnrolledLinkedList2023 | 256 | 91.8% | 内部状态探查+后向循环多迭代触发+等价变异识别 |
| **LunarCalendar** | **527** | **90%** | **多t值精确断言+公共API优于反射+天文MATH杀活** |
| MonteCarlofor2048 | 366 | 89% | 模拟结果验证 |
| SortFactory | 368 | 89% | 多算法参数化测试 |
| PathFinding | 405 | 88% | 路径输出验证 |
| **MethodHandle** | **490** | **88%** | **结构覆盖策略+精确类型断言+全分支覆盖+单文件聚合19业务类** |
| **FastJson** | **551** | **68%** | **包装器VOID等价识别+assertSame杀instanceof+全重载覆盖** |
| **BPlusTree** | **248** | **85%** | **断言升级阶梯+自洽方法反射验证+概率构造器循环扫描** |
| Library | 261 | 85% | 多态行为测试 |
| FastestRoute | 219 | 85% | 输出捕获验证 |
| Square | 449 | 82% | 加密循环验证 |
| ElevatorManager | 268 | 75% | 单例重置+状态机 |
| **Anagram** | **96** | **80%** | **系统输出捕获+优化守卫等价识别+null≈emptySet等价** |
| WeightBalancedTree2023 | 191 | 59% | 深度遍历验证 |
| P_Queue | 1,032 | 33% | GUI/Animation 等价变异识别 + Counting Subclass |

**算法/框架类平均值:** 8,297 mutants, 87.3% coverage (24 projects)
**框架适配器项目覆盖率天花板:** ~88% — 受 MethodHandles API 类型匹配屏障限制
**包装器/库封装项目覆盖率天花板:** 65-75% — 受 Wrapper VOID Equivalence 等价变异限制
**GUI/Animation 类实际可测上限:** 25-60% per class — 受 Animation State Restoration 等价变异限制

---

## Real-World Impact

- Most common fix: Boundary value testing (26% of improvements)
- Second: Void method side-effect verification (18%)
- Third: Internal state inspection (16%)
- Fourth: Reflection-based state injection (12%)
- Fifth: Array index math sweep (7%)
- Sixth: Counting subclass for animation void calls (6%)
- Seventh: Backward loop multi-iteration triggers (5%)
- Eighth: Assertion strength escalation (4%)
- Ninth: Self-consistent method reflection verification (4%)
- Tenth: Probabilistic constructor loop-scan (3%)
- Projects with systematic pattern application: 95%+ coverage (algorithmic code without recursion)
- B+Tree/recursive data structures: 85-92% realistic ceiling (5-8% equivalent mutants unavoidable)
- Equivalent mutants encountered: ~2.5% of total (algorithmic), ~30-50% of total (GUI/animation)
- **Pre-PIT compilation errors**: #1 cause of wasted PIT runs
- **ArrayList capacity MATH**: #1 equivalent mutant pattern in collection-heavy Java projects
- **Weak assertions on tree splits**: #1 cause of survived MATH in B+Tree projects
- **Wrapper/library project VOID equivalence**: #1 cause of survived VOID_METHOD_CALL in wrapper projects
