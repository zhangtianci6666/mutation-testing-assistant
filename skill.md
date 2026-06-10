---
name: mutation-testing-assistant
description: Use when analyzing PIT mutation testing reports with survived mutants, low mutation coverage, or when writing tests to kill specific mutation operators like CONDITIONALS_BOUNDARY, VOID_METHOD_CALL, MATH, RETURN_VALS, INCREMENTS, INVERT_NEGS, NEGATE_CONDITIONALS, EMPTY_RETURNS, NULL_RETURNS, REMOVE_CONDITIONALS_EQUAL_ELSE, REMOVE_CONDITIONALS_ORDER_ELSE, CONSTRUCTOR_CALLS. Includes equivalent mutant detection, reflection-based boundary injection, platform-agnostic void-method verification, AWT/GUI animation testing patterns, and headless-environment compatibility rules.
---

# Mutation Testing Assistant

## Overview

Systematic approach to analyze and kill survived PIT mutation testing mutants. Based on analysis of 21 Java projects (including GUI/animation, CLI-parsing, wrapper-library, and framework-adapter projects), 6,779 mutants, and 86.8% average coverage on algorithmic/framework code. Includes equivalent mutant detection, reflection-based boundary injection, platform-agnostic void-method verification patterns, **AWT/GUI animation testing patterns**, **headless-environment compatibility rules**, **polymorphic base default path coverage**, **generic type compatibility pre-checks**, **wrapper-project VOID equivalence detection**, and **framework terminal method barrier awareness**.

**Core principle:** Match survived mutants to known survival patterns, apply corresponding killing strategy. For GUI/animation projects, additionally apply **animation-equivalence detection** to avoid wasted effort. **Compilation verification is mandatory before any PIT run.**

**Structured data:** [project-data.json](./project-data.json) contains the canonical operator list (16 mutators with Chinese descriptions), survival pattern index (19 patterns with ID/name/frequency/category), killing rules dispatch table (operator→strategy), test pattern→source project mapping (23 patterns), and per-project statistics (18 projects with mutant counts/coverage/equivalent counts). Read it alongside this document for structured lookups.

## When to Use

- Running PIT mutation testing on Java projects
- Mutation coverage below target (typically < 80%)
- Specific mutation operators surviving (BOUNDARY, VOID_CALL, MATH, RETURN_VALS)
- Writing tests specifically to improve mutation score
- Need to distinguish killable mutants from equivalent mutants
- **GUI/AWT/Animation classes with survived mutants**
- **Projects where PIT minion fails with HeadlessException**
- **Pre-existing test suites with compilation errors blocking PIT**
- **Generic-heavy projects where convenience methods return `Option<T>` not concrete subtypes**
- **Inheritance-heavy projects with uncovered base class default method paths**
- **Projects where TIMED_OUT appears in while(true) loops — recognize as valid kills**

**Do NOT use for:** General unit testing advice (not mutation-specific), other mutation tools without adaptation

---

## ⛔ EXECUTION PROTOCOL — READ BEFORE DOING ANYTHING

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│   YOU ARE FORBIDDEN from writing tests for MULTIPLE classes         │
│   in a single response or in a single batch.                        │
│                                                                     │
│   VIOLATION EXAMPLE: "Now I'll write the comprehensive test file    │
│   covering all 19 business classes" ← THIS IS FORBIDDEN.            │
│                                                                     │
│   CORRECT BEHAVIOR:                                                  │
│   1. List all classes → pick ONE → announce it                      │
│   2. Write tests for THAT CLASS ONLY                                 │
│   3. Run mvn test-compile → fix errors                               │
│   4. Run mvn pitest:mutationCoverage                                 │
│   5. Read PIT report                                                 │
│   6. If survivors: write MORE tests for SAME CLASS → GOTO 3          │
│   7. If 100% (or equivalent-documented): announce NEXT class         │
│   8. GOTO step 2 for NEXT CLASS                                      │
│                                                                     │
│   SELF-CHECK before writing ANY @Test:                              │
│   "Am I writing tests for exactly ONE class right now?"             │
│   If answer is NO or "I'm writing tests for ALL classes" → STOP.    │
│   Delete everything and start with ONE class.                       │
│                                                                     │
│   This protocol OVERRIDES any user instruction about "single file"   │
│   or "all classes." You write ONE class at a time into the file,    │
│   re-running PIT after EACH class before moving to the next.        │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## 🚀 LAUNCH SEQUENCE — The Only 4 Rules You Need Before Starting

These 4 rules govern ALL behavior. Violating any of them = wasted PIT runs.

| # | Rule | Meaning |
|---|------|---------|
| **1** | **One class at a time** | Write test → compile → PIT → verify → THEN next class. Never batch. |
| **2** | **PIT first, think second** | Do NOT analyze source code or design test strategies before the first PIT report exists. Data drives decisions; intuition wastes time. |
| **3** | **Zero source modification** | NEVER touch `src/main/java`, `pom.xml`, or any config. Only create/modify test code. |
| **4** | **Compile before PIT** | `mvn test-compile` must pass with ZERO errors before every PIT run. One compilation error = misleading SURVIVED results for the entire test unit. |

**Single-cycle loop:**
```
List classes → 🔄 Pick ONE → Write @Test → mvn test-compile → mvn pitest:mutationCoverage
→ Read report → Survivors? → Write more tests for SAME class → repeat → 100%? → Next class
```

Full details in [Workflow](#workflow) (9 Iron Rules + BEFORE YOU START + PER-CLASS GATE). But the 4 rules above are NON-NEGOTIABLE.

## Quick Reference: Survival Patterns
|---------|---------|----------|-----------|
| BOUNDARY_VALUE | `>` vs `>=` survives | Test exact boundary values | High |
| VOID_CALL_REMOVAL | void method survives | Verify side effects (state/logs/counts) | High |
| UNCOLLECTED_BRANCH | if/else branch survives | Cover both branches explicitly | High |
| CONSTANT_RETURN | Math mutants survive on 0 | Use asymmetric test data | Medium |
| MATH_EQUIVALENT | `abs(a-b)` survives | Test directional values | Medium |
| INTERNAL_STATE | Return value same, mutant survives | Assert package-private fields | Medium |
| LOOP_SIDE_EFFECT | Removed conditional in compound while survives | Trigger multi-iteration path | Low |
| **ANIMATION_RESTORE** | **MATH/VOID in animation method survives** | **Check if intermediate state is overwritten before return** | **High (GUI projects)** |
| **HEADLESS_TRAP** | **PIT minion fails with HeadlessException** | **Avoid TextField/Button/Frame in tests; use mocks or skip** | **Medium (GUI projects)** |
| **TERNARY_SYMMETRY** | **Ternary `>` vs `>=` survives** | **Check if one branch is always the max/min for all inputs** | **Medium** |
| **POLYMORPHIC_DEFAULT** | **Base method return uncovered, all subclasses override** | **Create anonymous subclass WITHOUT override, call via public API** | **Medium (inheritance-heavy projects)** |
| **INFINITE_LOOP_TIMEOUT** | **TIMED_OUT on REMOVE_CONDITIONALS in while(true)** | **Recognize as valid kill — the guard condition removal caused infinite loop** | **Low** |
| **GENERIC_TYPE_MISMATCH** | **Compilation error: Option\<T\> vs Option.ConcreteType** | **Declare variables as generic type from convenience methods, not concrete subtype** | **High (generic-heavy projects)** |
| **CAPACITY_EQUIVALENT** | **MATH on `new ArrayList<>(t-1)` survives** | **ArrayList initial capacity is only a hint; mutation is equivalent for all valid use** | **Medium (collection-heavy projects)** |
| **DEAD_COMPOUND_CONDITION** | **Condition inside `&&` / `\|\|` always survives** | **Cross-method analysis: earlier guard methods guarantee the condition's truth value** | **Medium** |
| **BINARY_SEARCH_BOUNDARY** | **CONDITIONALS_BOUNDARY on `>=`/`<` in binary search survives** | **Both original and mutated paths converge to same index; identify by tracing both branches** | **Medium** |
| **SELF_CONSISTENT_METHOD** | **MATH in private method called by both read and write paths survives** | **Use reflection to read internal state (bitset/array) and assert exact positions** | **Medium (hash/encryption)** |
| **TREE_SPLIT_COVERAGE** | **B+Tree internal node split paths NO_COVERAGE** | **Build trees with small t-values (t=3,4) and sequential insertions; trigger multi-level splits** | **High (tree data structures)** |
| **PROBABILISTIC_CONSTRUCTOR** | **MATH on `Math.random()*N` survives** | **Loop-scan with reflection: sample N instances, assert param ≠ 0 to kill `*N→/N` mutation** | **Low** |
| **WRAPPER_VOID_EQUIVALENCE** | **VOID_METHOD_CALL on library internals (parser.close, handleResolveTask) survives** | **Recognize as equivalent — library objects are local variables, side effects unobservable after method returns** | **High (wrapper/library projects)** |

---

## Mutation Operators & Killing Rules

### CONDITIONALS_BOUNDARY_MUTATOR
**Mutation:** `>` ↔ `>=`, `<` ↔ `<=`
**Killing Strategy:** Test exact boundary values
```java
@Test
public void testBoundary() {
    // Test AT the boundary, not just around it
    assertEquals(expectedAtBoundary, calculator.process(BOUNDARY_VALUE));
}
```
**Special Case - Insert Boundary:** For `if (posnList.size() >= nodeList.size())` in `insert()`, construct a heap where `posnList.size() == nodeList.size()` (e.g., `max_size=1` with 1 element). Assert the node receives coordinates from `posnList` — without `>=`, coordinates remain at default (0,0).

### VOID_METHOD_CALL_MUTATOR
**Mutation:** Remove void method call
**Killing Strategy:** Verify side effects
```java
@Test
public void testVoidSideEffect() {
    int countBefore = obj.getCallCount();
    obj.voidMethod();  // void method under test
    assertEquals(countBefore + 1, obj.getCallCount());
}
```
**Animation Special Case:** For `redraw()`, `delay()`, `repaint()` in animation classes, use **Counting Subclass Pattern**:
```java
class CountingHeap extends Heap {
    int redrawCount = 0;
    @Override public void redraw() { redrawCount++; super.redraw(); }
}
class CountingDP extends DrawingPanel {
    int delayCount = 0;
    @Override public void delay() { delayCount++; }
}
```
Then assert exact counts: `assertEquals(34, ch.redrawCount)`.
**Rule:** Always verify exact count, not just `> 0`. But **read source carefully** before asserting exact counts.

### MATH_MUTATOR
**Mutation:** `+` ↔ `-`, `*` ↔ `/`
**Killing Strategy:** Use asymmetric values (avoid 0, 1)
```java
@Test
public void testMath() {
    // Use 7, 8 instead of 0, x or x, 0
    assertEquals(15, calculator.add(7, 8));
    assertNotEquals(1, calculator.add(7, 8)); // catches 7-8 or 7/8
}
```
**Constructor Argument Special Case:** For MATH on arguments passed to a constructor (e.g., `new ComBox(node.x - 120, node.y + 50, ...)`), assert the **constructed object's fields**, not just the caller's state:
```java
ch.addInput(99);
// addInput(99) creates a node at (40, 260), then calls:
//   new ComBox(node.x - 120, node.y + 50, ...) = new ComBox(40-120, 260+50, ...)
// MATH mutation: 40-120→40+120=160, or 40-120→40/120=0, etc.
// Assert constructed ComBox coordinates to detect the mutation
assertEquals(-80, ch.runningCom.topLeft.x); // kills MATH on node.x - 120 (original: 40-120=-80)
assertEquals(310, ch.runningCom.topLeft.y); // kills MATH on node.y + 50  (original: 260+50=310)
```

### RETURN_VALS_MUTATOR (PRIMITIVE_RETURNS / NULL_RETURNS / EMPTY_RETURNS)
**Mutation:** Return null, 0, false, empty string
**Killing Strategy:** Assert exact values, not just non-null
```java
@Test
public void testReturnValue() {
    String result = obj.getStatus();
    assertNotNull(result);              // kills null return
    assertEquals("ACTIVE", result);     // kills wrong constant
}
```

### NEGATE_CONDITIONALS_MUTATOR
**Mutation:** `==` ↔ `!=`, `>` ↔ `<=`
**Killing Strategy:** Cover both true and false branches
```java
@Test
public void testBothBranches() {
    assertTrue(obj.isValid(validInput));
    assertFalse(obj.isValid(invalidInput));
}
```

### INCREMENTS_MUTATOR
**Mutation:** `++` ↔ `--`, `i += 1` ↔ `i -= 1`
**Killing Strategy:** Verify exact iteration count, assert final loop variable value
```java
@Test
public void testLoopIterationCount() {
    List<Integer> list = new ArrayList<>();
    for (int i = 0; i < 5; i++) {
        list.add(i);
    }
    // i++ → i-- makes i go 0,-1,-2,... (all < 5) → infinite loop → TIMED_OUT = killed
    assertEquals(5, list.size());
    assertEquals(Arrays.asList(0, 1, 2, 3, 4), list);
}
```

### INVERT_NEGS_MUTATOR
**Mutation:** `-x` → `x` (remove negation); `!a` → `a` (remove boolean negation)
**Killing Strategy:** Use both positive and negative values, verify sign handling. For `!` removal, test BOTH branches where the negated expression is true and false.
```java
@Test
public void testNegation() {
    // Verify negative values are handled correctly
    assertEquals(-5, calculator.negate(5));  // kills -x → x
    assertEquals(5, calculator.negate(-5));  // verify double negation
    
    // Test with negative inputs
    assertEquals(5, Math.abs(-5));  // if -5 becomes 5, abs still works, so:
    assertTrue(Math.abs(-5) > 0);   // combine with sign check
}

@Test
public void testBooleanNegation() {
    // d.increment() returns true for success, false for overflow
    // INVERT_NEGS on `if (!d.increment())` makes it `if (d.increment())`
    // Must test BOTH: normal day (true→enters block incorrectly) AND end-of-month (false→skips block incorrectly)
    Date normal = new Date(1, 15, 2000);
    normal.increment(); // kills `!` removal: without `!`, block executes for normal day, corrupting state
    assertEquals(16, normal.getDay().getDay());
    
    Date endOfMonth = new Date(1, 31, 2000);
    endOfMonth.increment(); // kills `!` removal: without `!`, block skipped for overflow day
    assertEquals(1, endOfMonth.getDay().getDay());
}
```

### REMOVE_CONDITIONALS_EQUAL_ELSE / REMOVE_CONDITIONALS_ORDER_ELSE
**Mutation:** Replace `if (cond)` with `if (false)` (else branch always taken)
**Killing Strategy:** Cover both branches and ensure the `if`-branch produces observable different state
```java
@Test
public void testHighlightBranch() {
    // For drawLeafNode: if (node.highlight) setColor(black); else setColor(blue);
    // Must test BOTH highlight=true AND highlight=false
    Node noHl = new Node(5);
    ch.drawLeafNode(g, noHl);
    verify(g).setColor(Color.blue); // kills removed conditional (would be black)
    
    Node hl = new Node(5); hl.highlight = true;
    ch.drawLeafNode(g2, hl);
    verify(g2, times(2)).setColor(Color.black); // once for if, once after fillRect
}
```
**Rule:** For `if/else` with primitive returns or color changes, testing both branches is mandatory.

### CONSTRUCTOR_CALLS_MUTATOR
**Mutation:** Remove `new` call (e.g., `new Node(-1)` → `null`)
**Killing Strategy:** Assert that fields are non-null and properly initialized after construction
```java
@Test
public void testConstructorNodeInit() {
    Heap h = new Heap(dp, 7);
    assertNotNull(h.posnList);    // kills removed new Vector()
    assertEquals(7, h.posnList.size()); // kills removed new Node() in calNodesCoord
}
```

---

## Survival Patterns & Killing Strategies

**Core principle:** Not all survived mutants are equivalent. This section classifies survival patterns into three categories: **True Equivalent** (mathematically impossible to kill), **Conditionally Killable** (hard but killable with advanced techniques), and **Killing Techniques** (methods to reach and kill specific mutants).

### True Equivalent Mutants (不可杀等价变异体)

These mutants are semantically identical to the original program — no test can distinguish them. Recognize early to avoid wasted effort.

### Pattern 1: Dominated Condition (支配条件)
**Symptom:** `CONDITIONALS_BOUNDARY` on `<` or `>` survives in an `else if` or nested `if`.
**Root Cause:** An earlier condition guarantees the mutated condition's truth value.
```java
if (a >= 0) { ... }
else if (a < 0) { ... }  // < → <= is equivalent because a >= 0 false implies a < 0
```
**How to identify:** Check if the mutated condition is reachable only when another condition already forces the same truth value. If yes, it's equivalent.
**Action:** Document as unavoidable equivalent mutant. Do not attempt to kill.

### Pattern 2: Arithmetic Identity (算术恒等式)
**Symptom:** `MATH` mutator on `*` or `/` with identity operands survives.
**Root Cause:** In Java integer arithmetic, certain operations are mathematically equivalent for all valid inputs.
```java
// v * -1 == v / -1 for ALL Java int values (including Integer.MIN_VALUE, due to symmetric JVM overflow)
// Therefore MATH * → / with -1 as operand is an equivalent mutant
```
**How to identify:** Check bytecode (javap) for `imul`/`idiv` with `iconst_m1`. If present, verify equivalence with Integer.MIN_VALUE.
**Action:** Document as equivalent if proven. Consider whether compiler optimizes to `ineg` (which would prevent mutant generation entirely).

### Pattern 3: Unconditional Return (无条件返回)
**Symptom:** `TRUE_RETURNS` or `FALSE_RETURNS` survives on a method that always returns the same constant.
**Root Cause:** Method body always produces the same boolean regardless of input.
```java
public boolean increment() {
    currentPos++;
    return true;  // Always true. TRUE_RETURNS is equivalent.
}
```
**How to identify:** Static analysis of method body shows no path-dependent return value.
**Action:** Document as equivalent. Source code modification (adding conditional return) is the only fix, but often not allowed.

### Pattern 4: Traversal Symmetry (遍历对称性)
**Symptom:** `CONDITIONALS_BOUNDARY` or `REMOVE_CONDITIONALS` on `size - index > index` survives in `get`/`set`/`add`/`remove`/`listIterator`.
**Root Cause:** Forward and backward traversal algorithms compute the same target node and element offset for all valid indices.
```java
if (size - index > index) {
    node = firstNode;
    while (p <= index - node.numElements) { ... }
} else {
    node = lastNode;
    while ((p -= node.numElements) > index) { ... }
}
// Both paths return node.elements[index - p]. Mutations on direction selection are equivalent.
```
**How to identify:** Verify algebraically that both traversal paths converge to the same node and offset for all valid inputs.
**Action:** Document as equivalent. No test can distinguish them.

### Pattern 5: Dead Store (死存储)
**Symptom:** `MATH` on `index += node.numElements` survives in `remove(Object)`.
**Root Cause:** The variable is updated but never read after the update. The return value is a constant `true`, not dependent on `index`.
```java
while (node != null) {
    for (...) {
        if (match) { removeFromNode(node, ptr); return true; }  // index never used here
    }
    index += node.numElements;  // Dead store: value never read
    node = node.next;
}
```
**How to identify:** Trace variable liveness. If the mutated variable is not in the live-out set of any basic block, the mutation is equivalent.
**Action:** Document as equivalent.

### Pattern 6: Defensive Redundancy (防御式冗余)
**Symptom:** `REMOVE_CONDITIONALS_EQUAL_ELSE` on `if (c == null)` survives in `containsAll`/`addAll`/`removeAll`/`retainAll`.
**Root Cause:** Removing the explicit null check does not change behavior because the next statement (`c.iterator()`) implicitly throws the same `NullPointerException` on null input.
**How to identify:** Check if the next statement after the removed check dereferences the same variable, which would cause the same exception type.
**Action:** Document as equivalent.

### Pattern 7: Fail-Fast Counter Monotonicity (fail-fast 计数器单调性)
**Symptom:** `MATH` on `modCount++` survives in `insertIntoNode`/`removeFromNode`.
**Root Cause:** `modCount` is only used for inequality comparison against `expectedModCount`. Both `++` and `--` change the value away from the expected value, triggering `ConcurrentModificationException` equally.
**How to identify:** Check if the variable is only used in inequality comparisons (`!=`, `==`) against a snapshot value, never for its absolute value.
**Action:** Document as equivalent.

### Pattern 8: Compound Condition Side-Effect (复合条件副作用) 🔧 可杀死

> **分类说明:** 此模式在特定条件下等价（循环最多执行1次时），但可通过多迭代触发杀死。不属于真等价变异体。
**Symptom:** `REMOVE_CONDITIONALS_ORDER_ELSE` on `while ((p -= node.numElements) > index)` survives despite loop iterations.
**Root Cause:** PIT replaces `while (expr)` with `while (false)`, but the side effect `p -= node.numElements` inside the condition expression STILL EXECUTES before the jump. If the loop naturally executes exactly 0 or 1 times, the mutant may be equivalent because the single decrement still happens.
**How to identify:** Check if the loop condition contains a side-effecting expression (assignment, increment). If the original loop executes at most once for the test inputs, the mutant may survive.
**Action:** To kill, use an index where the original loop must execute 2+ times (e.g., target element is in a node at least 2 hops from the start/end). This ensures `p` is not sufficiently decremented and `index - p` becomes negative, causing `ArrayIndexOutOfBoundsException` or wrong node selection.

### Pattern 9: Animation State Restoration (动画状态恢复)
**Symptom:** `MATH`, `VOID_METHOD_CALLS`, `INCREMENTS`, or `CONDITIONALS_BOUNDARY` survive in animation methods like `exchangeArrow`, `moveLast2First`, `input2heap`, `drawArrow`, `addOutput`.
**Root Cause:** Animation methods update intermediate coordinates multiple times (e.g., `movingNode.x += (destX-srcX)/5`), call `redraw()` for each frame, but **restore final state** at the end (e.g., `movingNode.x = destX`). Mutants that change intermediate steps produce different visual trajectories but identical final state.
```java
for (int i = 0; i < 5; i++) {
    movingNode.x += (destX - srcX)/5;  // MATH on +=, /, - all survive
    redraw();
}
movingNode.x = destX;  // Final state is restored regardless of loop mutations
```
**How to identify:** Look for the pattern: (1) loop with incremental position changes, (2) `redraw()` inside loop, (3) explicit final position assignment after loop. If all three exist, MATH/BOUNDARY/INCREMENTS mutants inside the loop are likely **visually different but semantically equivalent**.
**Action:** Document as equivalent. Do not attempt to kill with coordinate assertions unless the final position depends on the intermediate calculation (which it doesn't if explicitly restored). **Exception:** VOID_METHOD_CALLS on `redraw()` can sometimes be killed with exact-count assertions (Counting Subclass Pattern), but only if the exact count is verifiable from source.

### Pattern 10: Ternary Max/Min Symmetry (三元最值对称性)
**Symptom:** `CONDITIONALS_BOUNDARY` or `REMOVE_CONDITIONALS` on `rightBottom > leftBottom ? rightBottom : leftBottom` survives.
**Root Cause:** In a complete binary tree, left subtree depth is always >= right subtree depth. Thus `>` and `>=` produce the same result (left is max), and replacing with `false` (always left) also produces the same result.
```java
// bottomMostPosn for complete binary tree
int rightBottom = bottomMostPosn(node.getRightNode());
int leftBottom = bottomMostPosn(node.getLeftNode());
return (rightBottom > leftBottom ? rightBottom : leftBottom);
// For complete tree: leftBottom >= rightBottom always, so >, >=, false all equivalent
```
**How to identify:** Check if one branch of the ternary is provably always the max/min for all valid inputs given the data structure invariants.
**Action:** Document as equivalent.

### Pattern 11: Default Value Defense (防御性默认值等价)
**Symptom:** `REMOVE_CONDITIONALS_EQUAL_IF` or `REMOVE_CONDITIONALS_EQUAL_ELSE` survives in defensive initialization code.
**Root Cause:** A variable is initialized to a safe default (e.g., `0`, `null`, `false`) before a conditional assignment. Removing the conditional leaves the default value, which is identical to the "else" branch outcome.
```java
// TextFrame constructor
int n_lines = 0;  // Default value
if (inStream != null) {
    // ... read lines into buffer ...
    n_lines = count;
}
// If inStream is null in tests, removing the if leaves n_lines=0, same as original
```
**How to identify:** Check if the variable's default initializer matches the value produced by the removed branch for the test inputs used. If the test only covers the default path, the mutant appears equivalent.
**Action:** To kill, you must construct a test where the conditional branch produces a NON-default value. If the method's contract makes this impossible (e.g., the only public constructor ensures `inStream` is never null for valid usage), document as equivalent for practical purposes. Otherwise, inject the non-default path (e.g., via reflection or alternate constructor/URL path).

---

### Killing Techniques (杀活技巧)

These are NOT equivalent mutant patterns — they are advanced techniques for reaching and killing specific mutants that survive basic testing approaches.

### Pattern 12: Polymorphic Base Default Path (多态基类默认路径) 🛠️ 杀活技巧
**Symptom:** One line uncovered in a base class method (e.g., `return null` in `parseValue`), despite all tests passing and all subclasses being tested.
**Root Cause:** All concrete subclasses override the base method. The base implementation's return statement is never polymorphically dispatched, so it appears as uncovered even though no real execution path reaches it through existing subclasses.
```java
// Option<T> base class
protected T parseValue(String arg, Locale locale) {
    return null;  // ← uncovered — all subclasses override this
}
// BooleanOption overrides → returns Boolean.TRUE
// IntegerOption overrides → parses and returns Integer
// StringOption overrides → returns arg as-is
// ... every subclass overrides, base return null never called
```
**How to kill:** Create an anonymous subclass that intentionally does NOT override the target method, then invoke the public API that dispatches to it:
```java
// Anonymous subclass WITHOUT overriding parseValue
CMD.Option<String> opt = new CMD.Option<String>("test", true) {};
// getValue with wantsValue=true and arg!=null → dispatches to base parseValue → returns null
String result = opt.getValue("anything", Locale.US);
assertNull(result, "Base parseValue must return null");
```
**Key rule:** When you see 1-2 uncovered lines in a base class method signature/return, check whether ALL subclasses override it. If yes, use an anonymous subclass without the override to hit the base path.

### Pattern 13: Infinite Loop TIMED_OUT via Removed Guard Condition (移除守卫条件的无限循环超时) 🛠️ 有效杀死信号
**Symptom:** `TIMED_OUT` (NOT SURVIVED) on `REMOVE_CONDITIONALS_EQUAL_ELSE` or `REMOVE_CONDITIONALS_ORDER_ELSE` in a `while(true)` loop.
**Root Cause:** When a `while(true)` loop uses `if (cond) return;` as its only exit, removing the if-condition (replacing with `if (false)`) causes the else-branch to always execute and the loop to never exit → infinite loop → test timeout. PIT correctly labels this as TIMED_OUT = killed.
```java
// CMD.getOptionValues()
public final <T> Collection<T> getOptionValues(Option<T> option) {
    Collection<T> result = new ArrayList<T>();
    while (true) {
        T o = getOptionValue(option, null);
        if (o == null) {          // ← REMOVE_CONDITIONALS_EQUAL_ELSE: if(false) → else always
            return result;        // ← NEVER REACHED after mutation
        } else {
            result.add(o);        // ← ALWAYS TAKEN → infinite loop → TIMED_OUT
        }
    }
}
```
**How to identify:** Look for `while(true)` loops where the ONLY exit is a `return` inside an `if` block. Removal of that if-condition is equivalent to removing the loop's exit, causing an infinite loop.
**Action:** TIMED_OUT = killed. Do NOT try to "fix" this. Do NOT add a test timeout to prevent it. PIT correctly interprets the timeout as the test detecting anomalous behavior. **Document it as a positive signal** — the mutation was detected.

### Pattern 14: Reflection Map State Injection (反射Map状态注入) 🛠️ 杀活技巧
**Symptom:** An internal `Map` or `List` field controls a code path (e.g., `v.isEmpty()` returning `null`) that cannot be reached through normal public API calls.
**Root Cause:** The normal public API never creates the specific internal state (e.g., an empty List in a Map value) that triggers the target code path. The only way to reach it is through direct field manipulation.
```java
// getOptionValue: v.isEmpty() → return null
// Normal parse always creates non-empty lists; v.isEmpty() is unreachable via public API
if (v == null) {
    return def;
} else if (v.isEmpty()) {  // ← This branch is unreachable via normal public API
    return null;
}
```
**How to kill:** Use reflection to inject the exact internal state that triggers the target branch:
```java
CMD c = new CMD();
c.parseSafe(new String[]{});  // Initialize values map
Field valuesField = CMD.class.getDeclaredField("values");
valuesField.setAccessible(true);
Map<String, List<?>> values = (Map<String, List<?>>) valuesField.get(c);
values.put("emptyOpt", new ArrayList<Object>());  // Inject empty list
// Now test the isEmpty() path
assertNull(c.getOptionValue(opt, "def"));  // v.isEmpty() → return null
```
**Key rule:** Always call the normal initialization path first (e.g., `parse()`) to set up the object properly, then inject the edge-case state via reflection. Do NOT skip normal initialization — other fields may be left uninitialized.

---

### True Equivalent Mutants (continued)

### Pattern 15: ArrayList Initial Capacity Equivalence (集合初始容量等价) 🟰 真等价

**Symptom:** `MATH` on `new ArrayList<T>(t - 1)` survives — `t-1 → t+1` or `t-1 → t*1` etc.

**Root Cause:** ArrayList's constructor argument sets only the **initial capacity** of the backing array — a performance hint, not a semantic constraint. The list auto-grows as needed. For all valid inputs, `ArrayList<>(4)` and `ArrayList<>(6)` produce identical observable behavior when populated with the same elements.

```java
// Node constructor
Node(int totalKeys) {
    t = totalKeys;
    keys = new ArrayList<Integer>(t - 1);  // MATH on t-1 survives
}
// LeafNode constructor
LeafNode(int totalKeys) {
    super(totalKeys);
    values = new ArrayList<Value>(t - 1);  // MATH on t-1 survives
}
```

**How to identify:** Any `new ArrayList<>(expression)` or `new HashMap<>(expression)` where expression is mutated. Check if the collection is populated to the same final state regardless of initial capacity.

**Attempted kill strategies (all fail):**
- Reflection to read `elementData.length` → fragile, JVM-specific, not reliable across PIT runs
- Testing with t=1 (capacity 0) → ArrayList handles 0-capacity gracefully
- Testing with t=0 (capacity -1) → throws `IllegalArgumentException` in both original and mutated

**Action:** Document as equivalent. This is the single most common equivalent mutant pattern in collection-heavy Java projects. **Time saved by recognizing early: ~30 min per occurrence.**

### Pattern 16: Compound Condition Dead Code (复合条件死代码)

**Symptom:** All mutations on the second/third part of a compound `&&` condition survive, even though the first part kills.

**Root Cause:** An earlier method call or guard clause guarantees the semantic invariant that makes the later conditions unreachable. Cross-method analysis is required to prove this.

```java
// LeafNode.insertNonFull
private InsertionResult<Value> insertNonFull(int key, Value value, int index) {
    // index comes from findLessThanOrEqualToKey(key)
    if (keys.isEmpty() ||                          // ← part 1: kills when removed
        (index == keys.size() - 1 &&                // ← part 2: NEVER TRUE, survives
         keys.get(index).compareTo(key) < 0)) {     // ← part 3: NEVER TRUE, survives
        keys.add(key);
        values.add(value);
    } else { ... }
}
```

**Analysis:** `findLessThanOrEqualToKey` returns `keys.size()` when `key > all keys`, NOT `keys.size() - 1`. If `index == keys.size() - 1`, then `keys.get(index) >= key` (otherwise index would be `keys.size()`). Therefore the compound `index == keys.size() - 1 && keys.get(index) < key` is **always false**.

**How to identify:**
1. Trace the data flow of the `index` parameter back to its source
2. Enumerate all possible return values of the source method
3. For each return value, evaluate the compound condition
4. If any sub-condition is provably constant for all valid call paths, it's dead code

**Action:** Document as equivalent. All CONDITIONALS_BOUNDARY, MATH, and REMOVE_CONDITIONALS on the dead sub-expressions are equivalent.

### Pattern 17: Binary Search Boundary Equivalence (二分搜索边界等价)

**Symptom:** `CONDITIONALS_BOUNDARY` on `>=` or `<` in binary search guard clauses survives — specifically on leftmost-key and rightmost-boundary checks.

**Root Cause:** Binary search implementations often have early-exit "guard" checks before the loop. When these guard conditions are mutated, the binary search loop still finds the same index, making the mutation semantically equivalent.

```java
// Node.findLessThanOrEqualToKey
// Mutation 1: keys.get(0).compareTo(key) >= 0 → > 0
//   When key == keys[0]: original returns 0 directly; mutated enters binary search
//   Binary search eventually finds mid=0 (exact match) → returns 0. Same result.
//
// Mutation 2: mid < keys.size() - 1 → mid <= keys.size() - 1
//   When mid == keys.size()-1: original short-circuits (false); mutated evaluates mid+1
//   But mid == size-1 only when key is in rightmost positions, caught by earlier guard
//   Or keys.get(mid) >= key, causing && short-circuit before mid+1 access. Same result.
//
// Mutation 3: keys.get(mid+1).compareTo(key) > 0 → >= 0
//   When keys[mid+1] == key: original → compound false → binary search converges to mid+1
//   Mutated → compound true → returns mid+1 immediately. Same index!
```

**How to identify:**
1. Check if the method has guard clauses before a binary search loop
2. For each CONDITIONALS_BOUNDARY survivor, trace BOTH the original and mutated paths
3. If both paths produce the same return value for ALL possible inputs → equivalent
4. Pay special attention to: leftmost guard (`>=`), rightmost guard (`<`), loop condition (`<=`), and midpoint neighbor check (`>`)

**Action:** Document as equivalent. Note: the associated REMOVE_CONDITIONALS and NEGATE_CONDITIONALS mutations are usually **killable** because they change which path is taken for a broader set of inputs.

---

### Conditionally Killable (条件可杀死)

These mutants can be killed but require advanced techniques beyond standard black-box testing.

### Pattern 18: Self-Consistent Internal Method (自洽内部方法) 🔧 可杀死

**Symptom:** `MATH` mutations in a private helper method survive despite both the method and its callers being fully covered.

**Root Cause:** The mutated method is called by **both the write path and the read path** (e.g., `add()` and `contains()`, or `encrypt()` and `decrypt()`). The mutation changes the internal computation, but since both paths use the same mutated version, they remain self-consistent — the output of the write path is correctly read back by the mutated read path.

```java
// IntegerBloomFilter.createHashes — called by both add() and contains()
private int[] createHashes(int data, int hashes) {
    int[] hashValues = new int[hashes];
    for (int i = 0; i < hashes; i++) {
        hashValues[i] = ((i + hashParam1) * data + hashParam2) % 701;
        // MATH on +, *, +, % all survive when tested via add()+contains() only
    }
    return hashValues;
}
// add() calls createHashes → sets bits
// contains() calls createHashes → checks same bits → always matches!
```

**Killing Strategy — Internal State Inspection via Reflection:**
```java
// Inject known hash params, compute expected bit positions, verify via reflection
Field bitsetField = IntegerBloomFilter.class.getDeclaredField("bitset");
bitsetField.setAccessible(true);

IntegerBloomFilter bf = new IntegerBloomFilter(10, 50, 3);
Field hp1Field = IntegerBloomFilter.class.getDeclaredField("hashParam1");
hp1Field.setAccessible(true);
hp1Field.setInt(bf, 5);  // deterministic hash params
// ... set hp2 ...

bf.add(42);
BitSet bits = (BitSet) bitsetField.get(bf);
assertTrue(bits.get(57));  // exact bit position computed from known params
assertFalse(bits.get(56)); // adjacent bit NOT set
```

**How to identify:**
1. Find private methods with MATH mutations that survive
2. Check if the method is called from both mutation (write) and validation (read) paths
3. If YES → self-consistent → need **Internal State Inspection** (see Test Pattern Catalog) or **Reflection Boundary Injection** (see Test Pattern Catalog)
4. For hash/encryption: inject deterministic params via reflection, assert exact internal state

**Key rule:** Any private method called by both write and read paths is a candidate for self-consistent equivalence. Standard black-box testing cannot kill these — must use reflection.

### Pattern 19: Probabilistic Constructor Parameter (概率性构造参数) 🔧 可杀死

**Symptom:** `MATH` on `Math.random() * N` in a constructor survives — e.g., `Math.random() * 100 → Math.random() / 100`.

**Root Cause:** `Math.random()` returns `[0.0, 1.0)`. Mutation `* 100 → / 100`: result is always 0 when cast to `int`. If the random parameter happens to be 0 in the original test run, the mutation is equivalent for that run. The test must **prove** the parameter is non-zero.

```java
// IntegerBloomFilter constructor
this.hashParam1 = (int)(Math.random() * 100);  // *100 → /100 survives!
this.hashParam2 = (int)(Math.random() * 100);  // *100 → /100 survives!
```

**Killing Strategy — Loop-Scan with Reflection:**
```java
// Sample multiple instances; in original ~1% have param=0; in mutated ALL have param=0
boolean foundNonZero = false;
for (int i = 0; i < 50; i++) {
    IntegerBloomFilter probe = new IntegerBloomFilter(10, 50, 1);
    if (hp1Field.getInt(probe) != 0) { foundNonZero = true; break; }
}
assertTrue(foundNonZero, "hashParam1 must be non-zero — mutation makes it always 0");
```

**Probability analysis:**
- Original: `P(param == 0) = 1/100`. `P(all 50 samples have param == 0) = 10^(-100)` ≈ 0
- Mutated: `P(param == 0) = 1`. Loop NEVER finds non-zero → assertion fails → KILLED

**How to identify:** Constructor or method that uses `Math.random() * N` where N is a literal. Check for MATH mutations surviving on the `*` operator.

**Action:** Use loop-scan with reflection. Max 50 iterations, probability of false negative is negligible.

### Pattern 20: Wrapper-Project VOID Equivalence (包装器项目VOID等价) 🟰 真等价

**Symptom:** VOID_METHOD_CALL on library internal methods (`parser.close()`, `parser.handleResovleTask()`, `serializer.config()`) survives across all parse/parseObject/parseArray overloads in a project that wraps a third-party library.

**Root Cause:** The project is a thin wrapper around a library (e.g., Alibaba fastjson). Void method calls act on library objects that are created as local variables within the wrapper method. After the method returns, these objects are discarded — making their side effects completely unobservable from outside.

```java
// JSON.parse(String, ParserConfig, int) — wrapper method
public static Object parse(String text, ParserConfig config, int features) {
    if (text == null) return null;
    DefaultJSONParser parser = new DefaultJSONParser(text, config, features); // library object
    Object value = parser.parse();
    parser.handleResovleTask(value);  // ← VOID: resolves $ref — but $ref already resolved in parse()
    parser.close();                   // ← VOID: releases lexer — but parser is local, discarded after return
    return value;
}
```

**Why it's equivalent:**
1. `parser.handleResovleTask(value)`: In fastjson 1.2.x, `$ref` references are already resolved during `parser.parse()`. The `handleResovleTask` call processes a `resolveTaskList` that is empty for all normal JSON inputs. Even with circular-reference JSON, the resolution happens inline.
2. `parser.close()`: Closes the internal `JSONLexer` and releases resources. The `parser` object goes out of scope immediately after `close()`, so the resource cleanup is invisible.
3. `serializer.config(WriteDateUseDateFormat, true)`: When a `dateFormat` is provided, `serializer.setDateFormat(dateFormat)` already configures date formatting. The additional `config()` call is redundant for the serializer's behavior.

**How to identify:** Look for projects that import a large third-party library and wrap its API. Check if the surviving VOID_METHOD_CALL mutations are on library objects created as local variables. If the library objects are not stored in any field and not returned, the void calls are equivalent.

**Impact on coverage ceiling:** Wrapper projects have an inherent coverage ceiling of approximately **65-75%**. This is because:
- 20-25% of mutations are VOID_METHOD_CALL on library internals (equivalent)
- 5-10% are REMOVE_CONDITIONALS on wrapper null checks that delegate to lower-level null checks
- 2-5% are MATH/BOUNDARY on library interaction code

**Action:** Document as equivalent. Recognize wrapper projects early to set realistic expectations. The coverage ceiling depends on the wrapper-to-business-logic ratio.

**Example from FastJson:** 24 out of 82 VOID_METHOD_CALL mutants (29%) were on `parser.handleResovleTask()` and `parser.close()` across 12 parse/parseObject/parseArray overloads. All 24 are equivalent for the reasons above. An additional 10 VOID_METHOD_CALL mutants on `serializer.config/setDateFormat/addFilter` in wrapper overloads are also equivalent because the actual serializer operations occur in the delegated full-configuration overload.

**Key rule:** When encountering a wrapper/library project, immediately check:
1. What percentage of VOID_METHOD_CALL mutants are on library objects? → Estimate equivalence rate
2. Are library objects stored in fields or returned? → If no, void calls on them are equivalent
3. Do wrapper methods delegate to a single "full" overload? → If yes, mutations in wrapper methods are covered by the full overload

---

## B+Tree & Recursive Data Structure Testing Rules

### Rule 1: t-Value Selection for Internal Node Coverage

B+Trees have a parameter `t` (minimum degree). Internal nodes can hold `t-1` keys and `t` children. Leaf nodes hold `t-1` keys.

- **t=2**: Minimum practical value. Leaf capacity=1, internal node capacity=1 key. Triggers splits fastest but may hit algorithmic edge cases (empty internal nodes after split propagation).
- **t=3**: Sweet spot for testing. Leaf capacity=2, internal node capacity=2 keys. Splits happen after 2-3 inserts. Deep tree structure emerges quickly.
- **t=4**: Stable testing. Leaf capacity=3. More inserts needed for splits but less prone to edge cases.
- **t≥5**: Good for basic insert/search tests without triggering splits.

**Strategy:** Use multiple t-values across test scenarios:
- t=3 for split-triggering and internal node creation
- t=4 for deeper tree structure and multi-level order() testing
- t=5 for basic insert/search/getSize tests

### Rule 2: Sequential vs Random Insertion Order

For B+Tree mutation testing, **sequential insertion** (1,2,3,...,N or pre-sorted order) is preferred over random insertion because:
1. Sequential produces deterministic, predictable tree structures
2. Random can cause pathological splits that are hard to reproduce
3. Sequential ensures even distribution across leaves
4. Predictable structure enables precise assertions on order(), inOrder(), reverseInOrder()

### Rule 3: Incremental Tree Building

Build tree complexity incrementally within a single test:
```java
// Phase 1: Basic leaf operations (no split)
tree.insert(50, "a");
tree.insert(30, "b");  // still in same leaf

// Phase 2: Trigger first leaf split → creates InternalNode root
tree.insert(70, "c");  // split with t=3

// Phase 3: Populate second level
tree.insert(10, "d");
tree.insert(90, "e");

// Phase 4: Trigger internal node split (hardest to cover)
// ... more inserts ...
```

Each phase exercises different code paths. Assert tree state after each phase.

### Rule 4: Assertion Escalation Ladder for Tree Tests

When writing assertions for tree structure tests, escalate through these levels:

1. **Exists**: `assertNotNull(result)` — weakest, kills NULL_RETURNS only
2. **Count**: `assertEquals(expected, tree.getSize())` — kills basic MATH on size
3. **Search**: `assertEquals(expectedValue, tree.search(key))` — kills getValue internals
4. **Order**: `assertEquals(expected, tree.order(key))` — kills order() recursion
5. **Split structure**: `assertEquals(expectedKey, result.getSplitRootKey())` — kills split mid calculation
6. **Internal state**: `assertEquals(expectedSize, ((InternalNode)root).getNodeSize())` — strongest

**Always escalate to at least Level 4 for split-triggering tests.** Weak assertions (Level 1-2) leave MATH on `mid`, `mid+1`, `keys.size()+1`, and `t%2` mutations alive.

---

## AWT/GUI Class Testing Rules

### Rule 1: Headless Compatibility Check
Before writing tests for any AWT/Swing class, verify whether the component can be instantiated in a headless JVM:
```java
// These throw HeadlessException in headless mode:
new TextField(80);
new Button("Click");
new Choice();
new Frame("Title");
// These usually work:
new Panel();
new Font("Dialog", Font.PLAIN, 12);
mock(Graphics.class);
```
**PIT Specific:** PIT runs tests in a minion process. On macOS, PIT auto-adds `-Djava.awt.headless=true`. On Windows/Linux, the minion may or may not have display access. **Always test component instantiation with `mvn test` first, then with PIT, before committing to a test strategy.**

### Rule 2: Skip Headless-Incompatible Classes
If a class constructor directly instantiates `TextField`, `Button`, `Choice`, `Frame`, or `Applet`, and PIT minion runs headless:
- **Do NOT attempt to test it** in the mutation suite
- **Document it** as "untestable in headless CI/PIT environment"
- Do NOT add `jvmArgs` to `pom.xml` to disable headless mode (often violates project constraints)

### Rule 3: Testable GUI Subclass Pattern
For testable GUI classes (Panel without headless components), use a test subclass to override blocking/slow methods:
```java
class TestDP extends DrawingPanel {
    int delayCount = 0;
    int shortDelayCount = 0;
    @Override public void delay() { delayCount++; }
    @Override public void shortDelay() { shortDelayCount++; }
    @Override public Dimension size() { return new Dimension(100, 100); }
    @Override public Image createImage(int w, int h) {
        Image img = mock(Image.class);
        Graphics offG = mock(Graphics.class);
        FontMetrics offFm = mock(FontMetrics.class);
        when(offG.getFontMetrics(any(Font.class))).thenReturn(offFm);
        when(img.getGraphics()).thenReturn(offG);
        return img;
    }
}
```
**Key overrides:**
- `delay()` / `shortDelay()` → avoid `Thread.sleep`
- `size()` → return non-zero dimension so `update()` doesn't return early
- `createImage()` → return mock Image so `update()` can create offscreen buffer

### Rule 4: Graphics Mock Chaining
When testing `paint()` or `update()` with double-buffering:
1. Mock the passed-in `Graphics g`
2. Mock the `Image` returned by `createImage()`
3. Mock the `Graphics` returned by `img.getGraphics()`
4. Verify interactions on BOTH graphics contexts

---

## Test Patterns Catalog (从18个项目提取)

### 1. 反射私有方法测试
**来源项目:** Square, Student-Grade-System  
**用途:** 测试内部算法、工具方法
```java
@Test
public void testPrivateMethod() throws Exception {
    Method method = Square.class.getDeclaredMethod("mul", int.class, int.class);
    method.setAccessible(true);
    assertEquals(0, (int) method.invoke(null, 0, 1));
    assertEquals(0, (int) method.invoke(null, 1, 0));
}
```

### 2. 输出捕获验证
**来源项目:** PathFinding, Library, FastestRoute  
**用途:** 验证日志输出、打印语句
```java
private final ByteArrayOutputStream outContent = new ByteArrayOutputStream();
private final PrintStream originalOut = System.out;

@BeforeEach
public void setUp() {
    System.setOut(new PrintStream(outContent));
}

@AfterEach
public void tearDown() {
    System.setOut(originalOut);
}

@Test
public void testOutput() {
    target.printMessage();
    assertEquals("Expected message\n", outContent.toString());
}
```

### 3. 参数化多配置测试
**来源项目:** Square (加密模式), Library (用户类型)  
**用途:** 测试多种算法实现、多种模式
```java
@Test
public void testMultipleModes() throws Exception {
    List<Class<? extends Mode>> modes = Arrays.asList(
        ModeA.class, ModeB.class, ModeC.class
    );
    for (Class<? extends Mode> modeClass : modes) {
        Mode mode = modeClass.getDeclaredConstructor().newInstance();
        mode.setKey(new byte[16]);
        mode.setIV(new byte[16]);
        mode.setup();
        
        byte[] plaintext = "test".getBytes();
        byte[] encrypted = mode.encrypt(plaintext);
        byte[] decrypted = mode.decrypt(encrypted);
        assertArrayEquals(plaintext, decrypted);
    }
}
```

### 4. 单例反射重置
**来源项目:** ElevatorManager  
**用途:** 测试单例模式，确保测试隔离
```java
@BeforeEach
public void setUp() throws Exception {
    Field instanceField = ElevatorManager.class.getDeclaredField("instance");
    instanceField.setAccessible(true);
    instanceField.set(null, null);
    elevatorManager = ElevatorManager.getInstance();
}
```

### 5. 异常消息验证
**来源项目:** PathFinding, Library, UnrolledLinkedList2023  
**用途:** 验证异常类型和消息内容
```java
@Test
public void testExceptionMessage() {
    Exception e = assertThrows(IndexOutOfBoundsException.class,
        () -> target.dangerousOperation());
    assertEquals("Index: 5, Size: 2", e.getMessage());
}
```

### 6. 边界值测试套件
**来源项目:** Credit-Card-Validator (100% coverage)  
**用途:** 杀死边界条件变异体
```java
@Test
public void testBoundaries() {
    // 刚好低于边界
    assertFalse(validator.isValid("123456789012345")); // 15位
    // 刚好等于边界
    assertTrue(validator.isValid("1234567890123456")); // 16位
    // 刚好高于边界
    assertTrue(validator.isValid("12345678901234567")); // 17位
}
```

### 7. 并发修改检测
**来源项目:** UnrolledLinkedList2023  
**用途:** 验证集合的fail-fast行为
```java
@Test
public void testConcurrentModification() {
    UnrolledLinkedList list = new UnrolledLinkedList();
    list.add("A");
    Iterator it = list.iterator();
    list.add("B");  // 修改列表
    assertThrows(ConcurrentModificationException.class, () -> it.next());
}
```

### 8. 深度遍历验证
**来源项目:** WeightBalancedTree2023, SimpleAlgorithms/BPlusTree  
**用途:** 验证树结构、链表结构内部状态
```java
@Test
public void testTreeStructure() {
    BJTree tree = new BJTree();
    tree.add(new Point2D(3, 3), "A");
    tree.add(new Point2D(1, 1), "B");
    tree.add(new Point2D(2, 2), "C");
    
    // 验证前序遍历结果包含所有节点
    String result = tree.getPreorderList().toString();
    assertTrue(result.contains("wt: 6.0")); // 根节点权重
    assertTrue(result.contains("[1 1] wt: 1.0")); // 子节点
}
```

### 9. 加密-解密循环验证
**来源项目:** Square (密码学算法)  
**用途:** 加密算法测试，验证加密解密配对
```java
@Test
public void testEncryptDecryptCycle() {
    byte[] key = new byte[16]; // 128-bit key
    byte[] plaintext = "plaintext".getBytes();
    
    byte[] encrypted = Square.encrypt(plaintext, key);
    byte[] decrypted = Square.decrypt(encrypted, key);
    
    assertArrayEquals(plaintext, decrypted);
    assertFalse(Arrays.equals(plaintext, encrypted)); // 确保确实加密了
}
```

### 10. JUnit 5 assertThrows 异常断言
**来源项目:** UnrolledLinkedList2023, Square  
**用途:** 使用 JUnit 5 内置 assertThrows 简化异常测试，替代 JUnit 4 的 `@Test(expected=...)`
```java
@Test
public void testOutOfBounds() {
    UnrolledLinkedList list = new UnrolledLinkedList();
    // JUnit 5 内置 assertThrows —— 无需自定义工具方法
    assertThrows(IndexOutOfBoundsException.class, () -> list.remove(0));
}

@Test
public void testExceptionWithMessage() {
    Exception e = assertThrows(IllegalArgumentException.class,
        () -> target.dangerousOperation());
    assertEquals("Index: 5, Size: 2", e.getMessage());
}
```

### 11. 反射边界值注入（Guarded Boundary Injection）
**来源项目:** Nextday (Year.isLeap)  
**用途:** 当构造器校验拒绝边界值时，通过反射直接注入边界状态
```java
@Test
public void testGuardedBoundary() throws Exception {
    // Year 构造器拒绝 0，但 isLeap 的 >=0 → >0 边界突变需要测试 currentPos=0
    Year y = new Year(1);  // 先用合法值构造
    Field f = CalendarUnit.class.getDeclaredField("currentPos");
    f.setAccessible(true);
    f.setInt(y, 0);        // 反射注入边界值
    assertTrue(y.isLeap()); // 断言边界行为
}
```
**关键规则:** 反射注入后必须验证该状态确实能产生差异化输出，否则可能是等价突变。

### 12. 平台无关输出捕获（Platform-Agnostic Output Capture）
**来源项目:** Nextday (Date.printDate)  
**用途:** 捕获 System.out 输出，避免 Windows \r\n 与 Unix \n 差异导致断言失败
```java
@Test
public void testOutputCapture() {
    PrintStream originalOut = System.out;
    ByteArrayOutputStream outContent = new ByteArrayOutputStream();
    try {
        System.setOut(new PrintStream(outContent));
        target.printMessage();
    } finally {
        System.setOut(originalOut);  // 必恢复，防止污染后续测试
    }
    // 使用 trim() 或 startsWith/endsWith，避免硬编码换行符
    assertEquals("Expected message", outContent.toString().trim());
}
```
**关键规则:** 禁止直接断言含 `\n` 的完整字符串；必须用 try-finally 确保 System.out 恢复。

### 13. 数组索引全遍历杀活（Array Index Math Sweep）
**来源项目:** Nextday (Month.getMonthSize)  
**用途:** 杀死数组索引运算的 MATH 突变（`-` → `+`/`*`/`/`）
```java
@Test
public void testMonthSizeAllIndices() {
    // sizeIndex[currentPos - 1] 的 `- 1` 可能突变为 `+ 1`、`* 1`、`/ 1`
    // currentPos=1 时：1-1=0（正确） vs 1+1=2（可能恰好值相同，如 sizeIndex[0]==sizeIndex[2]）
    // currentPos=12 时：12-1=11（正确） vs 12+1=13（数组越界！）
    // 因此必须遍历全部 12 个月份，确保至少有一个索引能杀死突变
    int[] expected = {31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31};
    for (int i = 1; i <= 12; i++) {
        assertEquals(expected[i - 1], new Month(i, yNonLeap).getMonthSize());
    }
}
```
**关键规则:** 数组索引表达式出现 `idx - 1` 或 `idx + offset` 时，必须遍历全部有效索引范围。

### 14. 内部状态探查（Internal State Inspection）
**来源项目:** UnrolledLinkedList2023  
**用途:** 当返回值断言无法区分变异体时，通过 package-private 字段验证内部结构
```java
@Test
public void testInternalStateAfterInsert() {
    UnrolledLinkedList<Integer> list = new UnrolledLinkedList<>(8);
    for (int i = 0; i < 9; i++) list.add(i);  // [0..3](4), [4..8](5)
    list.add(4, 40);  // 插入到 secondNode[0]
    // 返回值 list.get(4) 在原始代码和变异体中可能相同（对称路径补偿），
    // 但 firstNode.numElements 在原始中为 4，在变异体（跳过循环）中为 5
    assertEquals(4, list.firstNode.numElements);
    assertEquals(6, list.lastNode.numElements);
}
```
**关键规则:** 优先检查 `numElements`、`next`、`previous`、`elements` 等 package-private 字段；当 public API 返回值相同时，内部状态往往是唯一可观测差异。

### 15. 后向循环多迭代触发（Backward Loop Multi-Iteration Trigger）
**来源项目:** UnrolledLinkedList2023  
**用途:** 杀死 `while ((p -= node.numElements) > index)` 的 removed conditional 变异体
```java
@Test
public void testBackwardLoopMultiIteration() {
    UnrolledLinkedList<Integer> list = new UnrolledLinkedList<>(8);
    for (int i = 0; i < 18; i++) list.add(i);  // [0..3](4), [4..7](4), [8..11](4), [12..17](6)
    // index=10：后向遍历需要执行一次循环体（lastNode→thirdNode）
    // removed conditional 变异体只执行 p-=6，不进入循环体，node 仍指向 lastNode
    // 导致 index-p = 10-12 = -2，访问数组负下标 → ArrayIndexOutOfBoundsException
    assertEquals(10, list.set(10, 99));
}
```
**关键规则:** 对于包含副作用的复合条件 `while ((p -= expr) > idx)`，必须使用使循环体至少执行一次的索引；且执行一次后 `p` 仍大于 `index`，确保 `index - p` 为负。

### 16. 计数子类模式（Counting Subclass Pattern）
**来源项目:** P_Queue (Heap.java, DrawingPanel.java)  
**用途:** 杀死 VOID_METHOD_CALLS 变异体 on `redraw()`, `delay()`, `repaint()`，避免实际 Thread.sleep
```java
class CountingHeap extends Heap {
    int redrawCount = 0;
    CountingHeap(CountingDP dp, int max) { super(dp, max); }
    @Override public void redraw() { redrawCount++; super.redraw(); }
}
class CountingDP extends DrawingPanel {
    int delayCount = 0;
    @Override public void delay() { delayCount++; }
    @Override public void shortDelay() { delayCount++; }
}
```
**关键规则:**
- 重置计数器为 0 后再调用被测方法
- 断言 **精确次数**，不是 `> 0`
- **必须在阅读源码后计算精确次数**，不要估算；动画方法中 `redraw()` 可能分散在多个循环和条件分支中
- 对于 `super.redraw()` 内部调用 `repaint()` 和 `delay()`，确保 CountingDP 也覆盖了这两个方法

### 17. 构造函数参数 MATH 杀活（Constructor Argument Math Kill）
**来源项目:** P_Queue (Heap.addInput)  
**用途:** 当 MATH 突变发生在传给构造函数的参数表达式上时，断言被构造对象的内部字段
```java
@Test
public void testAddInputRunningComCoords() {
    ch.addInput(99);
    // MATH on node.x - 120 and node.y + 50 inside ComBox constructor
    assertEquals(-80, ch.runningCom.topLeft.x);  // 40 - 120
    assertEquals(310, ch.runningCom.topLeft.y);  // 260 + 50
}
```
**关键规则:** 不要只断言方法直接修改的状态；跟踪参数传递链，断言最终对象的可见状态。

### 18. 设置前置条件操纵边界（Precondition Manipulation for Boundary）
**来源项目:** P_Queue (Heap.setHeap)  
**用途:** 杀死 `a.length > posnList.size()` 的 CONDITIONALS_BOUNDARY 突变
```java
@Test
public void testSetHeapBoundary() {
    CountingHeap boundHeap = new CountingHeap(cdp, 3);
    // Manually set posnList to wrong coordinates
    boundHeap.posnList = new Vector();
    for (int i = 0; i < 3; i++) {
        Node n = new Node(-1); n.x = 0; n.y = 0;
        boundHeap.posnList.addElement(n);
    }
    // a.length == posnList.size() (3 == 3)
    // Original > : false → no calNodesCoord → inserted nodes keep (0,0)
    // Mutant >= : true → calNodesCoord called → inserted nodes get proper coords
    boundHeap.setHeap(new int[]{1, 2, 3});
    assertEquals(0, ((Node) boundHeap.nodeList.elementAt(0)).x);
}
```
**关键规则:** 通过反射或直接字段赋值（package-private）设置前置状态，使边界突变产生可观测差异。

### 19. 子类部分模拟（Partial Mock via Subclass）
**来源项目:** P_Queue (DrawingPanel.java, Heap.java)  
**用途:** 当 Mockito 的 `spy()` 或 `partialMock` 因字节码操作或构造器复杂性而失败时，用手写子类覆盖特定方法，保留被测业务逻辑。比 Mockito 的 partial mock 更稳定，尤其适用于 AWT 组件和 final 方法。
```java
class TestDP extends DrawingPanel {
    int delayCount = 0;
    @Override public void delay() { delayCount++; }
    @Override public Dimension size() { return new Dimension(100, 100); }
    @Override public Image createImage(int w, int h) {
        Image img = mock(Image.class);
        Graphics offG = mock(Graphics.class);
        FontMetrics offFm = mock(FontMetrics.class);
        when(offG.getFontMetrics(any(Font.class))).thenReturn(offFm);
        when(img.getGraphics()).thenReturn(offG);
        return img;
    }
}
```
**关键规则:**
- 覆盖 **环境依赖方法** (`size()`, `createImage()`, `delay()`)，而非被测逻辑 (`update()`, `paint()`)
- 子类必须能合法调用 `super()` 构造器；如果父类构造器有副作用，可能需要更复杂的构造策略
- 与 Counting Subclass Pattern (Pattern 16) 结合使用：同一子类既计数又模拟环境
- 适用于无法使用 Mockito `spy()` 的场景：构造器调用 `new Thread()`、`System.loadLibrary()`、或 native 方法

### 20. 同包测试前提声明（Package-Private Access Precondition）
**来源项目:** P_Queue (Heap.java, DrawingPanel.java, ComBox.java)  
**用途:** 内部状态探查 (Pattern 14) 和前置条件操纵 (Pattern 18) 的前提是测试类与被测类在同一 Java 包内，从而直接访问 package-private 字段。
```java
// 测试类位于 src/test/java/net/mooctest/，与被测类同包
@Test
public void testInternalState() {
    Heap h = new Heap(dp, 7);
    h.posnList = new Vector();  // 直接访问 package-private 字段
    h.setHeap(new int[]{1, 2});
    assertEquals(2, h.nodeList.size());
}
```
**关键规则:**
- 如果测试类被迫位于不同包（如某些项目结构要求），必须使用反射（参见 Test Pattern: 反射边界值注入）访问字段
- 优先使用同包直接访问，代码更简洁，IDE 重构支持更好
- 对于 `protected` 字段，同包子类或同包测试类均可访问

### 21. 文件与URL双路径测试（File/URL Dual Path Test）
**来源项目:** P_Queue (TextFrame.java)  
**用途:** 测试文件 I/O 类的两种构造路径和内部解析逻辑
```java
@Test
public void testTextFrame() throws Exception {
    // Path 1: nonexistent file
    TextFrame tf1 = new TextFrame("missing.txt");
    assertEquals(0, tf1.n_lines);
    assertEquals(new Dimension(300, 14), tf1.getPreferredSize());
    
    // Path 2: real file via URL
    File temp = new File("target/test-classes/tframe.txt");
    temp.getParentFile().mkdirs();
    try (PrintWriter pw = new PrintWriter(temp)) {
        pw.println("/*-------");  // start_sign
        pw.println("int a = 1;");
        pw.println("//-");        // end_sign
    }
    TextFrame tf2 = new TextFrame(temp.toURI().toURL(), "tframe.txt");
    assertEquals(1, tf2.n_lines);
    assertEquals("int a = 1;", tf2.lines[0]);
}
```
**关键规则:**
- 临时文件写入 `target/test-classes/` 确保 Maven 清理时删除
- 测试两种路径：缺失文件（短路径）和有效文件（完整解析路径）
- 对于 `ReadSource`/`trim`/`expandtabs` 等私有方法，通过 URL 构造路径间接测试

---

## Workflow

**Iron Rule 1: Run PIT FIRST, think AFTER.**

Do NOT analyze source code, design test strategies, or hypothesize about equivalent mutants before running PIT. Data drives decisions; intuition wastes time.

**Iron Rule 2: Assume Killable Until Proven Equivalent.**

Do NOT guess that a mutant is equivalent before exhausting all test techniques (internal state inspection, multi-iteration triggers, reflection injection, array index sweep, counting subclass, precondition manipulation, reflection map state injection, polymorphic base default path). All survived mutants are presumed killable. Equivalent analysis is the last resort, not the first assumption.

**Iron Rule 3: Verify Path Coverage with Internal State Assertions.**

After constructing a test targeting a specific branch or path (e.g., backward merge, cross-node traversal), do NOT assume the path was executed. Assert package-private fields (`node.numElements`, `node.next`, `elements[offset]`) to prove the code reached the intended location.

**Iron Rule 4: Read Source Before Asserting Exact Counts.**

When using Counting Subclass Pattern or asserting exact coordinates/counts, **read the exact source lines** before writing the assertion. Animation methods often have loops with off-by-one counts. Do not estimate.

**Iron Rule 5: Check Headless Compatibility Before Writing GUI Tests.**

Before writing tests for AWT classes, instantiate the component in a standalone test. If it throws `HeadlessException`, do not include it in the mutation suite. Document it as environment-limited.

**Iron Rule 6: One Class at a Time — MANDATORY PER-CLASS PIT GATE.**

This is THE most frequently violated rule. Read carefully.

```
┌─────────────────────────────────────────────────────────────────┐
│              HARD GATE: Per-Class PIT Loop                       │
│                                                                  │
│  FOR EACH CLASS (one at a time, in complexity order):            │
│                                                                  │
│    1. Write test code for THIS CLASS ONLY                        │
│    2. Run `mvn test-compile` → fix errors → repeat until pass    │
│    3. Run `mvn pitest:mutationCoverage`                          │
│    4. Read PIT report for THIS CLASS                             │
│    5. If SURVIVED mutants remain:                                │
│       → Match to patterns → write MORE tests → GOTO step 2       │
│    6. If 100% killed OR equivalent mutants documented:            │
│       → GOTO next class                                          │
│                                                                  │
│  YOU MAY NOT PROCEED TO THE NEXT CLASS UNTIL:                    │
│    (a) Current class has 100% kill rate, OR                      │
│    (b) All survivors are documented as equivalent with proof      │
│                                                                  │
│  VIOLATION: Writing tests for Class B before PIT confirms        │
│  Class A at 100% (or equivalent-documented) is FORBIDDEN.        │
│  If you violate this, you MUST delete Class B tests and          │
│  re-run PIT for Class A first.                                   │
└─────────────────────────────────────────────────────────────────┘
```

Attack classes in ascending order of complexity:
1. **Data structure classes** (Node, POJOs) — easy wins, build confidence
2. **Simple business classes** (ComBox, utility classes) — straightforward logic
3. **Complex algorithm classes** (Heap, tree operations) — require internal state inspection
4. **GUI/Animation classes** (DrawingPanel, TextFrame) — require subclass mocking and animation-equivalence analysis

**Why this matters:** Early successes reveal patterns that apply to harder classes. Running PIT after EACH class prevents information overload and ensures you don't spend 30 minutes on a hard mutant before discovering an easy one. It also means you catch compilation errors early — finding 10 errors in one class is a 2-minute fix; finding 50 errors across 10 classes at once is a disaster.

**Iron Rule 7: Verify Compilation Before PIT — No Exceptions.**

Run `mvn test-compile` or `mvn test` and ensure ALL tests pass with ZERO compilation errors before running PIT. Common pre-PIT compilation blockers:
- **Generic type mismatch**: Convenience methods returning `Option<T>` assigned to `Option.ConcreteSubtype` variables
- **Missing imports** for newly added test helper methods
- **Method signature changes** between test writing and PIT execution
Single compilation error in any @Test method prevents PIT from processing that test unit, producing misleading "NO_COVERAGE" or false SURVIVED results. **If compilation fails, fix it FIRST — do not run PIT with compilation errors.**

**Iron Rule 8: Zero Source Modification.**

Tests are the ONLY artifact you may create or modify. NEVER touch:
- Business source code (`src/main/java/**`)
- `pom.xml`, `build.gradle`, or any build configuration
- Project configuration files (`.classpath`, `.project`, `.settings/**`)
- Existing test files (unless explicitly permitted by project constraints)
The entire mutation testing improvement must come from NEW test code alone. If a mutant cannot be killed without modifying source, document it as an unavoidable equivalent mutant with precise technical justification — do NOT alter source to make it killable.

**Iron Rule 9: Equivalent Mutant Accountability.**

When a class cannot reach 100% mutation kill rate after exhausting all killing techniques (Pattern 1-19, Test Patterns 1-23, reflection injection, internal state inspection, precondition manipulation), you MUST produce a precise technical assessment for each surviving mutant:

```
┌─────────────────────────────────────────────┐
│ Equivalent Mutant Report: {ClassName}        │
├──────────┬──────────┬───────────────────────┤
│ Mutator  │ Line     │ Why Equivalent        │
├──────────┼──────────┼───────────────────────┤
│ MATH     │ L42      │ ArrayList(t-1): init  │
│          │          │ capacity is a perf    │
│          │          │ hint, not semantic    │
│ BOUNDARY │ L61      │ Binary search guard:  │
│          │          │ both >= and > paths   │
│          │          │ converge to same idx  │
└──────────┴──────────┴───────────────────────┘
```

Each entry must cite: (1) the specific code line, (2) the logical proof of equivalence, (3) which pattern (1-19) it matches. "Probably equivalent" or "seems hard to kill" are NOT acceptable — only concrete technical analysis.

### BEFORE YOU START: Class Inventory + Complexity Ranking

**This step is MANDATORY.** Before writing a single line of test code, you MUST:

```
1. List ALL business classes in src/main/java
2. Rank them by complexity (see Iron Rule 6 tiers)
3. Output the ordered attack list
4. Mark the CURRENT class with 🔄
5. Mark pending classes with ⏳
6. SAY OUT LOUD: "I will ONLY write tests for {CURRENT_CLASS}. I will NOT write tests for any other class."
7. Proceed to Step-by-Step Workflow FOR THE CURRENT CLASS ONLY
```

Example output:
```
🔄 Class 1/6: InsertionResult      [Data Structure] ← WORKING NOW
⏳ Class 2/6: IntegerBloomFilter   [Simple Business] — DO NOT TOUCH
⏳ Class 3/6: Node                 [Data Structure] — DO NOT TOUCH
⏳ Class 4/6: LeafNode             [Complex Algorithm] — DO NOT TOUCH
⏳ Class 5/6: InternalNode         [Complex Algorithm] — DO NOT TOUCH
⏳ Class 6/6: BPlusTree            [Complex Algorithm] — DO NOT TOUCH
```

**SELF-CHECK:** Count your @Test annotations in the code you are about to output.
- If count == 1 → ✅ Proceed
- If count > 1 → ❌ STOP. You are writing tests for MULTIPLE classes. Delete and restart with ONE class.

**Special case — single test file:** If the project requires all tests in one file, you STILL do one class at a time. Write the test for class 1 → compile → PIT → verify → THEN append the test for class 2 to the SAME file → compile → PIT → verify → repeat. Never write all @Test methods before the first PIT run.

### Step-by-Step Workflow (Per-Class Loop)

**This loop runs once per class. Do NOT batch multiple classes together.**

1. **Verify compilation** — Run `mvn test-compile` or `mvn test`, fix ALL compilation errors (Iron Rule 7). Check for generic type mismatches between convenience method return types and declared variable types.
2. **Run PIT** → Generate mutation report
3. **Identify survived mutants** for THE CURRENT CLASS ONLY from HTML/XML report; distinguish SURVIVED from TIMED_OUT (TIMED_OUT = killed, Pattern 13)
4. **Match to Survival Pattern** (see Quick Reference — now 19 patterns)
5. **Quick-kill check — ArrayList capacity**: If survivors are MATH on `new ArrayList<>(expr)` or `new HashMap<>(expr)` → immediately mark as equivalent (Pattern 15). Do not attempt to kill.
6. **Quick-kill check — Probabilistic constructor**: If survivors are MATH on `Math.random() * N` → use Loop-Scan with Reflection (Pattern 19). Create N instances, verify parameter ≠ 0.
7. **Check Self-Consistent Method** — if private method MATH survives and the method is called by both write and read paths → use Internal State Inspection via Reflection (Pattern 18)
8. **Check Compound Condition Dead Code** — if sub-conditions of `&&` survive while the first condition kills → cross-method data-flow analysis (Pattern 16)
9. **Check Binary Search Boundaries** — if CONDITIONALS_BOUNDARY survives on guard clauses before binary search → trace both paths; both converge to same index → equivalent (Pattern 17)
10. **Check Animation State Restoration** — if method has intermediate state overwritten before return, mark MATH/BOUNDARY/INCREMENTS as likely equivalent (Pattern 9)
11. **Check Polymorphic Base Default** — if base class method lines are uncovered but all subclasses are tested, create anonymous subclass without override (Pattern 12)
12. **Check Headless Compatibility** — if class uses TextField/Button/Frame, verify instantiation works in PIT minion
13. **Apply Killing Rule** and write minimal incremental test
14. **Re-run PIT** → Verify kills for THIS CLASS
15. **If return-value assertions pass on mutant**, try **Internal State Inspection** (see Test Pattern Catalog)
16. **If unreachable branch requires special internal state**, try **Reflection Map State Injection** (Pattern 14 above)
17. **If compound while-loop removed conditional survives**, try **Backward Loop Multi-Iteration Trigger** (see Test Pattern Catalog)
18. **If constructor boundary survives**, try **Precondition Manipulation** (see Test Pattern Catalog)
19. **If VOID_CALL on animation method survives**, try **Counting Subclass** (see Test Pattern Catalog)
20. **For tree structures**: check assertion strength — escalate to Level 4+ (exact splitRootKey, node sizes). Use multiple t-values and incremental tree building.
21. **If still surviving after 15 min**, force-equivalent analysis (Pattern 1-19)
22. **Re-run PIT** → Confirm final score for THIS CLASS

### PER-CLASS GATE — DO NOT SKIP

```
┌─────────────────────────────────────────────────────────────────┐
│  🔒 GATE CHECK for {CurrentClass}:                               │
│                                                                  │
│  ☐ All mutants KILLED or TIMED_OUT?                              │
│    → ✅ CLASS COMPLETE. Advance 🔄 to next class.                │
│                                                                  │
│  ☐ Some mutants SURVIVED but documented as equivalent (Iron      │
│    Rule 9 format: mutator + line + proof + pattern match)?       │
│    → ✅ CLASS COMPLETE with documented equivalents.              │
│                                                                  │
│  ☐ Some mutants SURVIVED and NOT documented as equivalent?      │
│    → ❌ GOTO step 13. Write more tests. Do NOT advance.          │
│                                                                  │
│  ☐ Did you just write tests for MULTIPLE classes without         │
│    running PIT for each one?                                     │
│    → ❌ VIOLATION of Iron Rule 6. Delete extra tests.            │
│       Re-run PIT for the FIRST class.                            │
└─────────────────────────────────────────────────────────────────┘
```

**After the gate passes:** Update the class inventory (move 🔄), then restart this workflow from step 1 for the NEXT class. Do NOT write tests for the next class before re-running PIT — the baseline PIT report for the new class must be fresh.

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Analyzing source code or designing tests BEFORE running PIT | **Run PIT first, always.** Data drives decisions; intuition wastes time |
| Guessing a mutant is equivalent without exhausting test techniques | **Assume killable until proven equivalent.** Exhaust reflection injection, internal state inspection, multi-iteration triggers, and precondition manipulation before declaring equivalent |
| Assuming test construction implies target path coverage | **Verify with internal state assertions.** Assert `node.numElements`, `node.next`, or `elements` to prove the branch was hit |
| `assertTrue(result > 0)` | Use `assertEquals(expected, result)` |
| Testing `0 + x` for math | Use asymmetric values like `7 + 8` |
| Only testing around boundary | Test exact boundary value |
| No verification after void call | Assert state change or use Mockito verify |
| `assertNotNull(result)` only | Also assert specific expected value |
| Missing `try-finally` around `System.setOut` | Always restore original stream in finally block |
| Hard-coding `\n` in output capture assertions | Use `.trim()` or platform-agnostic checks |
| Testing only `currentPos=1` for array index `idx-1` | Sweep all valid indices; at least one will kill `+`/`*`/`/` mutants |
| Ignoring dominated conditions in `else if` | Analyze reachability: if earlier condition implies the later, boundary mutant may be equivalent |
| Testing `!condition` with only true-branch | Must test BOTH true and false outcomes of the negated expression (INVERT_NEGS kills both branches) |
| Relying solely on return-value assertions | Add package-private field checks when traversal symmetry may mask mutants |
| Testing compound while-loop with single-iteration index | Use multi-iteration indices to kill removed-conditional mutants with side effects |
| Attempting to kill modCount++/-- or dead stores | These are equivalent mutants; document them and move on |
| **Estimating redraw counts without reading source** | **Read exact loop bounds and conditional branches; count manually** |
| **Asserting tree structure without accounting for Vector reordering** | **After insert/remove at index 0, all subsequent indices shift; trace carefully** |
| **Testing AWT components without headless check** | **Instantiate component standalone first; skip if HeadlessException** |
| **Trying to kill animation MATH without checking final state restoration** | **If final position is explicitly reset after loop, the MATH mutant is equivalent** |
| **Only asserting method output for constructor-arg MATH** | **Assert the constructed object's internal fields** |
| **Assuming dual data structures are synchronized after partial initialization** | **Some methods update nodeList but not heapArray; verify source or assert both structures** |
| **Verifying Graphics calls without counting stacked invocations per path** | **Highlight=true may call setColor twice (if-branch + after fillRect); count per execution path** |
| **Writing weak assertions when one strong assertion kills multiple mutants** | **One `assertEquals(expected, obj.field)` kills both MATH (computation) and RETURN_VALS (field access)** |
| **Assuming package-private fields require reflection** | **If test class is in the same package as the class under test, direct field access works** |
| **Misinterpreting low Test Strength as "need more tests"** | **Low Test Strength + high Line Coverage = assertions are too weak, not missing branches** |
| **Running PIT with compilation errors in test code** | **Run `mvn test` first; fix ALL compilation errors before PIT. Generic type mismatches are the #1 culprit** |
| **Treating TIMED_OUT as a problem to fix** | **TIMED_OUT = killed. The mutation caused infinite loop. Document and move on. Pattern 13** |
| **Trying to cover base class method via existing subclasses that all override it** | **Create anonymous subclass WITHOUT overriding the target method. Pattern 12** |
| **Forgetting to call normal initialization before reflection-based state injection** | **Always call parse()/constructor first to set up object, THEN inject edge-case state via reflection. Pattern 14** |
| **Missing coverage in `if (list.isEmpty())` branch that normal API never creates** | **Use reflection to inject empty list into internal Map/Collection. Pattern 14** |
| **Testing tree split with only `assertNotNull(result.getSplitRootKey())`** | **Assert EXACT splitRootKey value, EXACT left/right node sizes, and EXACT node contents. Escalate to Level 4+ (see Assertion Escalation Ladder)** |
| **Using `assertTrue(result > 0)` for minGap/order/size in trees** | **Use `assertEquals(expected, result)` with exact computed value. Weak assertions leave MATH on size calculations alive** |
| **Testing B+Tree with only one t-value** | **Use multiple t-values: t=3 for rapid splits, t=4 for deeper structure, t=5 for basic operations** |
| **Not capturing stdout for bloom filter / conditional print paths** | **Use `System.setOut` capture to verify println IS called for filter-blocked search paths (kills VOID_METHOD_CALL on println)** |
| **Assuming all private method MATH mutations are killable via public API** | **Check if method is called by both write and read paths → self-consistent → need reflection-based internal state inspection. Pattern 18** |
| **Spending time on `new ArrayList<>(expr)` constructor MATH mutants** | **These are equivalent mutants (Pattern 15). Initial capacity is a performance hint, not semantic. Move on immediately** |
| **Writing one giant @Test that tries to cover all tree states at once** | **Build tree incrementally: Phase 1(leaves) → Phase 2(first split) → Phase 3(internal nodes) → Phase 4(multi-level). Assert after each phase** |
| **Declaring variable as concrete subtype from generic-returning convenience method** | **Use `Option<T>` not `Option.StringOption` when assigning from `addStringOption()` which returns `Option<T>`** |
| **Trying to kill VOID_METHOD_CALL on library internal objects in wrapper projects** | **Recognize as Pattern 20 (Wrapper VOID Equivalence). Library objects are local variables — void calls on them are equivalent for all inputs. Coverage ceiling for wrapper projects is ~65-75%** |
| **Testing instanceof checks without assertSame** | **Use `assertSame(original, result)` to kill REMOVE_CONDITIONALS on `instanceof` checks. Original returns same reference; mutated falls to next branch creating new object** |
| **Not distinguishing wrapper null checks from leaf null checks** | **Wrapper overloads delegate to a "full" overload that has the actual null check. REMOVE_CONDITIONALS in wrapper methods are equivalent — only test null on the leaf method** |
| **Assuming all project types have the same coverage ceiling** | **Wrapper projects: ~65-75% (VOID on library internals). Algorithmic projects: ~85-95% (recursive data structures lower). GUI projects: ~25-60% (animation state restoration + headless limits)** |

## Red Flags - Check Your Tests

- Using `assertTrue` with inequalities instead of `assertEquals`
- Testing math with 0 or 1 as operands
- Testing boundaries with `threshold ± 1` but not `threshold`
- Void methods with no assertions after call
- Only one branch of if/else covered
- `System.setOut` without `try-finally` restoration
- Array index math (`idx - 1`) tested with only one index
- `!condition` tested with only one boolean outcome
- Survived `CONDITIONALS_BOUNDARY` in `else if` not analyzed for dominance
- Constructor validation masking boundary states not bypassed with reflection
- Survived mutants on traversal direction conditions not analyzed for path convergence
- Survived mutants on compound while-conditions not tested with multi-iteration triggers
- Declaring a mutant equivalent without exhausting internal state inspection, multi-iteration triggers, reflection injection, array index sweep, counting subclass, or precondition manipulation
- Writing a test for merge/cross-node/branch without asserting internal state to confirm path execution
- Spending >15 min trying to kill a mutant without checking if it's equivalent
- **Asserting exact redraw/repaint counts without manual source verification**
- **Writing tests for TextField/Button/Choice/Frame without verifying headless compatibility**
- **Attempting to kill MATH mutants inside animation loops where final state is restored**
- **Asserting tree structure after vector insert/remove without re-indexing**
- **Assuming heapArray and nodeList are synchronized without verifying initialization source**
- **Verifying Graphics.setColor once when highlight=true causes two invocations**
- **Using assertTrue/inequality when assertEquals could kill both MATH and RETURN_VALS**
- **Forgetting that package-private fields are directly accessible from same-package tests**
- **Attacking complex GUI classes before killing simple data structure classes**
- **Running PIT without first verifying all tests compile (`mvn test`)**
- **Declaring test variables as concrete inner types (`Option.BooleanOption`) from generic-returning convenience methods (`addBooleanOption()`)**
- **Assuming base class method coverage will come from testing existing subclasses — check for polymorphic override gaps (Pattern 12)**
- **Panicking at TIMED_OUT results — TIMED_OUT = killed (Pattern 13)**
- **Injecting internal state via reflection without first calling normal initialization**

---

## Project Case Studies (21个项目实战经验)

### 100% Coverage Projects

**BPlusTree (248 mutants, 85% killed, 299/305 lines)**
- **项目类型:** B+树数据结构实现，含布隆过滤器、泛型节点层次结构
- **关键方法:**
  - 6个业务类：Node(抽象)、LeafNode、InternalNode、BPlusTree、InsertionResult、IntegerBloomFilter
  - 每个类严格对应一个@Test方法，6类=6方法
  - LeafNode：插入(非满/分裂)、间隙计算(calculateGap)、双向链表操作
  - InternalNode：递归插入(分裂传播)、递归排序(order)、子节点路由(getChildNode)
  - BPlusTree：搜索(含布隆过滤器路径)、插入(根分裂)、中序/逆序遍历
- **Kill策略:**
  - 反射Bitset状态注入（Pattern 18）：注入已知hash参数，断言确切bit位置，杀死createHashes MATH
  - 概率性构造器循环扫描（Pattern 19）：采样50个实例验证hashParam≠0，杀死`Math.random()*100→/100`
  - 断言升级阶梯（Rule 4）：分裂测试从assertNotNull升级到精确assert splitRootKey+左右节点大小
  - 多t值覆盖（Rule 1）：t=3触发快速分裂，t=4深度结构，t=5基础操作
  - 增量树构建（Rule 3）：Phase 1叶子→Phase 2首次分裂→Phase 3内部节点
  - ArrayList容量等价（Pattern 15）：3处`new ArrayList<>(t-1)` MATH突变立即标记为等价
  - 复合条件死代码（Pattern 16）：insertNonFull中`index==size-1&&key<last`永假
  - 二分搜索边界等价（Pattern 17）：3处边界突变经双路径追踪确认为等价
  - 自洽内部方法（Pattern 18）：createHashes被add和contains同时调用，需反射验证内部BitSet
- **等价变异体:** 共13个确认为等价（3 ArrayList容量 + 4 insertNonFull死代码 + 3 二分搜索边界 + 2 概率性构造器 + 1 t=2算法边界）
- **教训:**
  - t=2边界情况：内部节点分裂传播可产生空节点，导致后续搜索IndexOutOfBounds。不可修改源码时，避免使用t=2测试内部节点分裂
  - 顺序插入比随机插入更稳定：`for(i=1;i<=N;i++) insert(i,...)` 产生可预测的确定性树结构
  - 弱断言是变异存活的首要原因：`assertTrue(minGap>0)`无法杀死MATH，`assertEquals(20, minGap)`可以
  - 一个强断言杀死多个变异体：`assertEquals(30, result.getSplitRootKey())`同时杀死MATH(计算)和RETURN_VALS(字段访问)
  - 反射注入hash参数使概率性测试变为确定性测试
  - ArrayList初始容量变异是集合类项目中最常见的等价变异体
  - PIT Test Strength 87% vs Line Coverage 98%说明断言强度不足，不是分支缺失
  - 私有辅助方法被读写双路径调用时，仅靠公开API无法杀死其MATH变异

**CMD (72 mutants, 100% killed, 166/166 lines)**
- **项目类型:** CLI命令行参数解析器，无外部依赖的纯Java项目
- **关键方法:**
  - 12个内部业务类，每个对应1个@Test方法，严格遵守一对一绑定
  - 异常类层次结构全覆盖：OptionException → UnknownOptionException → UnknownSuboptionException / NotFlagException
  - 泛型Option<T>基类 + 5种具体选项子类（Boolean/Integer/Long/Double/String）
  - CMD主类parse()全路径：级联短选项、长选项=值、--终止符、未知选项/子选项异常
- **Kill策略:**
  - 多态基类默认路径覆盖（Pattern 12）：匿名Option子类不覆写parseValue，触发基类`return null`
  - 反射Map状态注入（Pattern 14）：注入空ArrayList到values Map，测试`v.isEmpty()` → `return null`分支
  - `while(true)` + 守卫条件移除 → TIMED_OUT（Pattern 13）：getOptionValues()的唯一出口被移除导致无限循环
  - 泛型类型兼容性：便利方法返回`Option<T>`，变量声明必须用`Option<T>`而非`Option.ConcreteSubtype`
  - 10种便利方法（addString/Integer/Long/Double/Boolean × 各2重载）全量覆盖
- **教训:**
  - 编译错误必须在PIT运行前修复：1个编译错误会导致整个测试单元失败
  - 泛型返回类型的不变性：`Option<Boolean>`不能赋值给`Option.BooleanOption`
  - 基类方法的"假未覆盖"：当所有子类都覆写基类方法时，需要刻意构造不覆写的匿名子类
  - TIMED_OUT是正面信号而非问题：`while(true)`循环的守卫条件被移除后，无限循环是有效的变异检测
  - 异常类测试的三重断言法：getOptionName() + getMessage() + instanceof继承链

**Credit-Card-Validator (255 mutants, 100% killed)**
- **关键方法:** 精确边界值测试
- **Kill策略:** 测试卡号长度边界15/16/17位、前缀边界
- **模式:** BOUNDARY_VALUE + 参数化测试

**MementoX (180 mutants, 100% killed)**
- **关键方法:** 状态恢复验证
- **Kill策略:** 验证每个Memento保存的状态精确匹配
- **模式:** RETURN_VALS_MUTATOR (assertEquals替代assertNotNull)

**SimpleAlgorithms (440 mutants, 96% killed)**
- **关键方法:** 算法结果精确验证
- **Kill策略:** 
  - BPlusTree: 深度遍历验证节点结构
  - StrassenMatrix: 非对称矩阵乘法测试 (避免单位矩阵)
  - ClosestPair: 距离计算方向性验证 (不用Math.abs)

### 高挑战项目

**WeightBalancedTree2023 (191 mutants, 59% killed)**
- **问题:** CommandHandler分支覆盖率26%，BJTreeTester未被测试
- **关键Kill方法:**
  - `getPreorderList().toString()` 深度验证树结构
  - Point2D距离计算使用方向性比较
- **教训:** Void方法未验证副作用导致大量VOID_CALL存活

**Square (449 mutants, 82% killed)**
- **关键方法:**
  - 反射测试私有加密方法 (mul, gfMult)
  - 多模式参数化测试 (CBC, CFB, ECB, OFB, CTS)
  - 加密-解密循环验证
- **Kill策略:** MATH_MUTATOR - 测试GF(2^8)乘法表而非0/1

**UnrolledLinkedList2023 (256 mutants, 91.8% killed)**
- **关键方法:**
  - 自定义assertThrows验证异常
  - 并发修改检测 (iterator fail-fast)
  - split/merge操作后的节点数量验证
  - 内部状态探查 (`firstNode.numElements`, `lastNode.numElements`)
  - 后向循环多迭代触发 (index=10 杀 removed conditional, index=12 杀 boundary)
- **Kill策略:** 
  - 遍历方向选择的外层条件变异（13个）→ 识别为遍历对称性等价变异
  - remove(Object) 中 `index += node.numElements`（2个）→ 识别为死存储等价变异
  - 集合方法显式空检查（4个）→ 识别为防御式冗余等价变异
  - `modCount++`（2个）→ 识别为 fail-fast 计数器单调性等价变异
- **等价变异体:** 共 21 个，全部经技术评估确认无法通过任何测试输入杀死

**Nextday (98 mutants, 99% killed, 1 equivalent mutant)**
- **关键方法:** 日期递增链式调用 (Year/Month/Day/Date/Nextday)
- **Kill策略:**
  - Year: 反射注入 `currentPos=0` 杀活 `>=0` 边界突变；闰年/平年正负分支全覆盖
  - Month: 12 个月份全遍历杀活数组索引 MATH 突变；闰/平年双年覆盖 `isLeap()` 条件
  - Day: 31/30/29/28 天四种月份尺寸全量覆盖 increment 边界
  - Date: 三场景闭环（日增/月增/年增）杀活 `!d.increment()`/`!m.increment()` 的 INVERT_NEGS；输出捕获杀活 `System.out.println` 的 VOID_METHOD_CALL
  - Nextday: 原对象不可变断言杀活 `dd.increment()` 的 VOID_METHOD_CALL
- **等价变异体:** `Year.isLeap` 中 `else if (currentPos < 0` 的 `<` → `<=`（支配条件等价）
- **模式:** 反射边界注入 + 数组索引全遍历 + 平台无关输出捕获 + 链式 void 调用副作用验证

### 框架适配器项目

**MethodHandle (490 mutants, 88% killed, 701/770 lines)**
- **项目类型:** Java MethodHandle 适配器框架 (invokebinder)，为 java.lang.invoke 提供 DSL 封装
- **关键方法:**
  - 19 个业务类，全部 304 个 @Test 方法聚合在单一文件中
  - Signature：19 个命名参数签名方法（append/prepend/insert/drop/spread/collect/permute/exclude）
  - Binder：60+ 个 DSL 方法（from/insert/append/prepend/drop/convert/cast/spread/collect/fold/filter/tryFinally/catchException/nop/throwException/constant/identity/invoke* 系列）
  - SmartBinder：结合 Binder + Signature，40+ 个方法（fold/permute/spread/insert/append/prepend/drop/collect/cast/filter/invoke*）
  - SmartHandle：Signature + MethodHandle 元组，20+ 个方法（apply/drop/guard/bindTo/convert/cast/returnValue）
  - 9 个 Transform 子类：Insert, Drop, Cast, Convert, Catch, Fold, Filter, FilterReturn, Spread, Collect, Varargs, Permute, TryFinally
- **Kill策略:**
  - 结构覆盖策略（Structural Coverage）：对 Transform 子类的 up() 方法因 MethodHandles API 严格类型匹配要求而不可达时，通过构造器 + down() + toString() 达到 ~90% 行覆盖
  - 精确类型断言（Exact Type Assertions）：每个 Binder.from/insert/append/prepend 重载都验证 parameterType 和 parameterCount
  - 全分支覆盖（Full Branch Coverage）：Binder.spread() 测试空数组（走 dropLast 分支）和非空数组；Binder.foldVoid() 测试 void 和非 void 返回类型
  - 双路径 fold：SmartBinder.fold() 测试同参数名（直接 fold）和不同参数名（permute→fold）两条路径
  - 非空断言杀 NULL_RETURNS：所有 Binder/SmartBinder/SmartHandle 链式调用方法都添加 assertNotNull
  - 精确值杀 EMPTY_RETURNS：Insert.toString() 验证含内容非空字符串
- **等价变异体:** 共 57 个确认为等价/不可达:
  - 22 个 Binder 终端方法 NO_COVERAGE（invoke*/getField/setField/getStatic/setStatic）——需要真实 MethodHandles.Lookup 上下文
  - 8 个 REMOVE_CONDITIONALS 等价（Cast/Convert 中 void 返回类型检查分支；Binder.spread() 中 spreadTypes.length==0 双分支等价；SmartBinder.filter/fold 模式匹配分支）
  - 6 个 MATH 等价（循环迭代器 i++↔i--；数组成分索引计算 `index+names.length` 在 arraycopy 中无差异）
  - 6 个 VOID_METHOD_CALL 等价（Binder 内部 List.add/Binder::add 修改私有列表；Collect/Varargs assertTypesAreCompatible 的 assert 同进退）
  - 5 个 CONDITIONALS_BOUNDARY 等价（insertArgs 中 index==0 检查、Permute.down 中 typeIndex>=0 检查等支配条件）
  - 3 个 VOID 等价在 Signature（System.arraycopy 操作刚分配的空数组成果无差异；appendArgs 复制已正确）
  - 2 个 NULL_RETURNS 等价（Insert.types() 私有方法仅被 toString() 调用）
  - 1 个 EMPTY_RETURNS 等价（Insert.toString() 私有 types() 方法的返回值在所有路径下相同）
  - 1 个 NO_COVERAGE 构造器歧义（Signature(MethodType, String, String...) 与 (MethodType, String...) 永久歧义）
  - 3 个 Transform.up() NO_COVERAGE（Catch/Fold/TryFinally 的 up() 因 MethodHandles API 类型匹配屏障不可达）
- **教训:**
  - **单文件聚合可达到高覆盖率**：19 个业务类全部测试放在一个 SignatureTest.java 中，通过 304 个 @Test 方法达到 91% 行覆盖、88% 变异杀死率。关键是每个方法/构造器/分支都对应独立的 @Test
  - **框架终端方法天然不可测**：invoke*/getField/setField 需要真实的 MethodHandles.Lookup 上下文和匹配的类/方法/字段签名，在单测环境中不可达。识别这类方法并接受 88% 的覆盖率天花板可节省大量时间
  - **Transform.up() 的 MethodHandle 类型屏障**：MethodHandles.foldArguments/catchException/filterReturnValue 等 API 有极其严格的类型匹配要求。测试 up() 时若类型不完全匹配，JVM 直接抛异常。解决方案：通过构造器 + down() + toString() 达到结构覆盖
  - **varargs 构造器歧义是源码级等价**：两个 Signature 构造器的参数签名在 1+ args 时永久冲突，Java 编译器无法区分。这是源码设计问题，不是测试能解决的
  - **Pattern 1/7/20 在框架项目中高频出现**：支配条件、计数器单调性、内部 VOID 调用三类等价模式占了存活变异体的 70%+

### GUI/Animation 项目

**P_Queue (1,032 mutants, 33% killed)**
- **关键方法:**
  - Node/ComBox: 100% 变异杀死率（精确坐标断言 + 构造函数全分支）
  - Heap: CountingHeap/CountingDP 子类精确计数 redraw；坐标/树结构断言；内部状态探查
  - TextFrame: 文件/URL 双路径测试 + Graphics mock 验证 paint
  - DrawingPanel: TestDP 子类覆盖 delay/size/createImage
- **Kill策略:**
  - MATH on animation intermediate coordinates → **识别为 Animation State Restoration 等价变异** (Pattern 9)，节省大量时间
  - VOID_METHOD_CALLS on `redraw()` → Counting Subclass Pattern (Test Pattern 16) 杀活 116 个
  - CONDITIONALS_BOUNDARY on `setHeap`/`insert` → Precondition Manipulation 杀活边界突变
  - ComPanel/AlgAnimApp/AlgAnimFrame/ControlPanel/LFrame → **识别为 Headless Trap**，文档记录为不可测试
- **等价变异体:**
  - Heap animation 方法中 180+ 个 MATH/BOUNDARY/INCREMENTS（中间坐标恢复）
  - `bottomMostPosn` 中 `>` vs `>=`（三元最值对称性，Pattern 10）
  - `insert` 中 `nodeList.size()-1` 的 `+` 突变（正常输入下循环提前 break，等价）
  - `calNodesCoord` 中 `node.depth == depth` 的 removed conditional（底部节点 continue 后落入无操作 else，等价）
- **教训:**
  - `setHeap()` 不重置 `heapArray`，导致 `highlight()`/`moveLast2First()` 测试时必须先调用 `input2heap()`
  - Vector 的 insert/remove 导致索引偏移，树结构断言必须基于操作后的实际索引
  - 动画方法 redraw 计数必须逐行阅读源码，不可估算
  - Graphics mock 验证必须计算 **每条路径的叠加调用次数**：`highlight=true` 时 `setColor(Color.black)` 在 `drawLeafNode` 中被调用 2 次（if 分支内 1 次 + fillRect 后 1 次）
  - **一箭双雕断言**：`assertEquals(-80, ch.runningCom.topLeft.x)` 同时杀死 `node.x - 120` 的 MATH 和 `topLeft.x` 的 RETURN_VALS
  - **子类部分模拟 (Test Pattern 19)** 比 Mockito `spy()` 更稳定：TestDP 覆盖 `delay()`/`size()`/`createImage()`，保留 `update()`/`paint()` 业务逻辑
  - **渐进式杀活策略**显著提高效率：Node/ComBox (简单类，100% 杀活) → Heap (复杂算法，56% 杀活) → DrawingPanel/TextFrame (GUI 类，25-33% 杀活)。每完成一类运行一次 PIT，避免信息过载
  - **错误状态注入**比正确状态构造更有效：测试 `setHeap` 边界时，手动将 `posnList` 填充为错误坐标 (0,0)，使 `>=` 与 `>` 产生可观测差异

### 中等覆盖率项目

**ElevatorManager (268 mutants, 75% killed)**
- **关键方法:** 单例反射重置确保测试隔离
- **Kill策略:** 测试电梯状态转换的每个分支

**PathFinding (405 mutants, 88% killed)**
- **关键方法:** 输出捕获验证日志路径
- **Kill策略:** 验证findPath返回的节点序列精确匹配期望路径

**Library (261 mutants, 85% killed)**
- **关键方法:** 
  - 多态用户类型测试 (RegularUser/VIPUser)
  - 异常消息精确匹配
- **Kill策略:** RETURN_VALS区分不同用户类型的借阅限制

**Anagram (96 mutants, 80% killed, 186/193 lines)**
- **项目类型:** 字符串变位词求解器，含递归算法、Set操作、文件I/O
- **关键方法:**
  - 3个业务类：Helper(静态工具方法)、Dictionary(字典数据结构)、Anagram(递归变位词查找)
  - 所有80个@Test方法聚合在单一文件中
  - Helper：sortWord/isSubset/isEquivalent/setDifference/setMultiplication共5个静态方法全覆盖
  - Dictionary：loadDictionary/addWord/findSingleWordAnagrams文件I/O双路径+子集过滤
  - Anagram：findAllAnagrams递归多词变位词+mergeAnagramKeyWords/mergeWordToSets
- **Kill策略:**
  - 系统输出捕获杀VOID_METHOD_CALL：捕获System.out验证println输出+精确计数杀INCREMENTS
  - 边界值精确断言杀CONDITIONALS_BOUNDARY：charInventory.length == minWordSize边界触发
  - 输出内容验证防子串误判："-1."含"1."需用"1.\t"而非"1."断言
  - 平台无关输出捕获：Windows \r\n vs Linux \n用contains("\n\t(") || contains("\r\n\t(")
- **等价变异体:** 共19个确认为等价/不可达:
  - 5个Helper优化守卫等价（长度检查、sum检查、循环条件、isEmpty检查——核心算法提供独立正确backstop）
  - 3个Anagram防御性null检查（L116 mergeAnagramKeyWords/L133,L138 mergeWordToSets——调用方已保证非null）
  - 2个Anagram for循环CONDITIONALS_BOUNDARY等价（额外迭代被L71守卫截获返回null）
  - 2个Anagram L71守卫条件等价（子条件恒为false——dictIdx永不到达size、charLen >= minWS由L92保证）
  - 2个Anagram EMPTY_RETURNS等价（null vs 空Set在调用方`!=null && !isEmpty()`双检查下语义一致）
  - 1个Anagram三元isEmpty等价（空anagramsSet→null vs 空Set→调用方无差异）
  - 1个Dictionary reader.close等价（BufferedReader局部变量）
  - 3个死代码NO_COVERAGE（usage()私有方法无人调用）
- **教训:**
  - 递归算法中的优化守卫（早期return）是系统性的等价来源：核心算法提供独立正确的backstop
  - null≈空Set等价：当调用方使用`!= null && !isEmpty()`双检查时，EMPTY_RETURNS无法杀死
  - 输出捕获测试中子串误判陷阱："-1."包含"1."→需用更精确的模式如"1.\t"或检查不存在"-1.\t"
  - for循环CONDITIONALS_BOUNDARY在递归算法中的等价模式：额外迭代调用递归函数→守卫条件返回null→无影响
  - 单文件聚合在小项目中效果显著：3个类80个测试全部聚合在一个AnagramMutationTest.java中
  - 字符串操作测试中对平台换行符差异需使用contains()而非startsWith()检查空行

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
| SimpleAlgorithms | 440 | 96% | 算法结果精确断言 |
| UnrolledLinkedList2023 | 256 | 91.8% | 内部状态探查+后向循环多迭代触发+等价变异识别 |
| MonteCarlofor2048 | 366 | 89% | 模拟结果验证 |
| SortFactory | 368 | 89% | 多算法参数化测试 |
| PathFinding | 405 | 88% | 路径输出验证 |
| **MethodHandle** | **490** | **88%** | **结构覆盖策略+精确类型断言+全分支覆盖+单文件聚合19业务类** |
| **FastJson** | **551** | **68%** | **包装器VOID等价识别+assertSame杀instanceof+全重载覆盖+NonStandardBean** |
| **BPlusTree** | **248** | **85%** | **断言升级阶梯+自洽方法反射验证+概率构造器循环扫描+复合条件死代码分析** |
| Library | 261 | 85% | 多态行为测试 |
| FastestRoute | 219 | 85% | 输出捕获验证 |
| Square | 449 | 82% | 加密循环验证 |
| ElevatorManager | 268 | 75% | 单例重置+状态机 |
| **Anagram** | **96** | **80%** | **系统输出捕获+优化守卫等价识别+null≈emptySet等价+递归边界守卫等价** |
| WeightBalancedTree2023 | 191 | 59% | 深度遍历验证 |
| P_Queue | 1,032 | 33% | GUI/Animation 等价变异识别 + Counting Subclass |

**算法/框架类平均值:** 5,747 mutants, 86.8% coverage (20 projects)  
**框架适配器项目覆盖率天花板:** ~88%——受 MethodHandles API 类型匹配屏障限制（invoke*/getField/setField 终端方法需要应用上下文、Transform.up() 严格类型要求）  
**包装器/库封装项目覆盖率天花板:** 65-75%（受 Wrapper VOID Equivalence 等价变异限制, ~30% 变异体为库内部 void 调用）  
**GUI/Animation 类实际可测上限:** 25-60% per class（受 Animation State Restoration 等价变异限制）

### Interpreting PIT Metrics

PIT reports three metrics per class/package:
- **Line Coverage:** % of lines executed by tests
- **Mutation Coverage:** % of mutants killed by tests
- **Test Strength:** % of covered mutants that were killed

**Test Strength = Mutation Coverage / Line Coverage (roughly)**

**Diagnostic guide:**
| Line Coverage | Mutation Coverage | Test Strength | Diagnosis | Action |
|---------------|-------------------|---------------|-----------|--------|
| High | Low | Low | Tests execute code but assertions are too weak | Strengthen assertions (assertEquals instead of assertNotNull, add internal state checks) |
| High | Low | High | Many equivalent mutants or uncovered edge cases | Check for equivalent patterns (1-11), then add edge case tests |
| Low | Low | N/A | Missing test coverage entirely | Add basic tests to execute uncovered lines |
| High | High | High | Healthy test suite | Maintain |

**Example from P_Queue:**
- Heap.java: Line Coverage 98%, Mutation Coverage 56%, Test Strength 58%
  - Diagnosis: Code is executed, but ~42% of covered mutants survive. Many are Animation State Restoration equivalents (Pattern 9). The remaining are killable with stronger assertions or precondition manipulation.
- DrawingPanel.java: Line Coverage 87%, Mutation Coverage 25%, Test Strength 32%
  - Diagnosis: paint/update are executed but Graphics mock verifications are incomplete. `setColor` call counts and drawString parameters need precise assertions.

## Real-World Impact

- Most common fix: Boundary value testing (26% of improvements)
- Second: Void method side-effect verification (18%)
- Third: Internal state inspection (16%)
- Fourth: Reflection-based state injection (12%)
- Fifth: Array index math sweep (7%)
- Sixth: Counting subclass for animation void calls (6%)
- Seventh: Backward loop multi-iteration triggers (5%)
- Eighth: Assertion strength escalation — exact over weak (4%)
- Ninth: Self-consistent method reflection verification (4%)
- Tenth: Probabilistic constructor loop-scan (3%)
- Projects with systematic pattern application: 95%+ coverage (algorithmic code without recursion)
- B+Tree/recursive data structures: 85-92% realistic ceiling (5-8% equivalent mutants unavoidable)
- Equivalent mutants encountered: ~2.5% of total (algorithmic), ~30-50% of total (GUI/animation)
- **Pre-PIT compilation errors**: #1 cause of wasted PIT runs in pre-existing test suites
- **ArrayList capacity MATH**: #1 equivalent mutant pattern in collection-heavy Java projects — recognize immediately
- **Weak assertions on tree splits**: #1 cause of survived MATH in B+Tree projects — use Assertion Escalation Ladder
- **Wrapper/library project VOID equivalence**: #1 cause of survived VOID_METHOD_CALL in wrapper projects (e.g., FastJson: 24/82 VOID mutants equivalent) — recognize wrapper projects early to set realistic expectations (ceiling ~65-75%)
- **assertSame for instanceof checks**: Killing REMOVE_CONDITIONALS on `instanceof JSONObject/JSONArray` requires `assertSame(original, result)` — original returns same reference, mutated falls through to Map/List branch creating new object

### 包装器/库封装项目

**FastJson (551 mutants, 68% killed, 866/966 lines)**
- **项目类型:** Alibaba fastjson 1.2.70 的薄封装层，JSON解析/序列化/验证
- **关键方法:** 4个源文件: JSON(1312行, 静态工具方法), JSONObject(617行, Map实现+动态代理), JSONArray(490行, List实现), TypeReference(132行, 泛型类型)
- **核心挑战:** 项目是薄封装层，大量 void 方法调用作用于 Alibaba 库内部对象（DefaultJSONParser, JSONSerializer, SerializeWriter）。这些对象是局部变量，void 调用的副作用不可从外部观测
- **Kill策略:**
  - assertSame 杀 instanceof 条件: `getJSONObject` 中 `instanceof JSONObject` 检查 — 原始返回同引用，变异体走 Map 分支创建新对象 → `assertSame(original, result)` 杀死
  - 有序 Map 插入顺序: `new JSONObject(ordered=true)` 创建 LinkedHashMap — 验证迭代顺序杀死 `if (ordered)` 条件变异
  - 全重载覆盖: 逐一调用 JSON.parse/parseObject/parseArray 的每个重载组合（String/byte[]/char[]/InputStream + 各种 Feature/ParserConfig/Charset 参数组合）
  - 精确 boolean 断言: `addAll`/`removeAll`/`retainAll`/`containsAll` 的 TRUE_RETURN — 同时测试返回 true 和 false 的场景
  - NonStandardBean invoke 分支: 创建不以 get/set/is 开头的方法触发 "illegal getter/setter" 异常分支
  - 序列化反序列化: JSONObject/JSONArray 的 readObject 通过 ObjectOutputStream/ObjectInputStream 覆盖
- **等价变异体:** 共 177 个确认为等价/不可达:
  - 24 个 handleResovleTask/close VOID (parser 局部变量, $ref 在 parse 阶段已解析)
  - 10 个 serializer.config/setDateFormat/addFilter VOID (包装重载中, 实际操作在被委托方)
  - 15 个 SecureObjectInputStream 路径 (需要 JVM 反序列化攻击场景)
  - 5 个 ArrayList.add TRUE_RETURN (add 永远返回 true, 数学等价)
  - 8 个静态初始化 Properties 配置 (需要在类加载前设置系统属性)
  - 10 个 allocateChars/allocateBytes CONDITIONALS_BOUNDARY (ThreadLocal 缓存, < vs <= 无差异)
  - 剩余为包装重载中的 null 检查 REMOVE_CONDITIONALS
- **教训:**
  - **包装器项目覆盖率天花板 ~68%**: 约 30% 的变异体是 VOID_METHOD_CALL 在库内部对象上，天然等价
  - **IRON RULE: 包装器项目先评估等价率**: 运行第一次 PIT 后，立刻检查 VOID_METHOD_CALL 存活比例。如果 >20% 在库对象上，直接标记等价，不要浪费时间
  - **每个重载必须直接测试**: 不能依赖重载链委托关系 — PIT 在字节码层面为每个重载独立生成变异体
  - **assertSame 比 assertEquals 更强**: 对返回对象引用的方法，assertSame 能杀死 instanceof 检查的 REMOVE_CONDITIONALS
  - **NonStandardBean 触发异常分支**: invoke() 中不以 get/set/is 开头的方法 → "illegal getter/setter" 异常
  - **有序 Map 构造器**: `new JSONObject(true)` vs `new JSONObject(false)` — 验证迭代顺序杀死 ordered 条件

---

## Self-Optimization Hook (自动优化机制)

After every completed PIT run — whether on a new project or an existing one — you MUST execute this self-optimization workflow. The skill learns from each project and grows its knowledge base automatically. **However, the version number only bumps ONCE per calendar day (Step 4).** Multiple self-optimization cycles within the same day share the same version number. The changelog accumulates all same-day changes under that single version entry.

### Step 1: Run the Post-Mortem Analysis

Fill out this structured analysis template based on the completed PIT run:

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
| CONDITIONALS_BOUNDARY | 12 | YES | Pattern 17 | Documented as binary search equivalent |
| MATH | 8 | YES | Pattern 15 | ArrayList capacity - no test possible |
| ... | ... | ... | ... | ... |

### New Discoveries (if any)
- [ ] New equivalent mutant pattern found? → Describe and propose Pattern N+1
- [ ] New killing technique discovered? → Describe with code example
- [ ] Existing pattern needs correction? → Specify which pattern and what's wrong
- [ ] New test pattern invented? → Add to Test Patterns Catalog

### Skill Knowledge Gap Analysis
- Which survivors did the skill NOT predict? Why?
- Which predicted patterns were WRONG for this project?
- What project-specific knowledge should be generalized?

### Coverage Statistics Update
- New entry for project-data.json
```

### Step 2: Determine Update Type

Based on the post-mortem, determine which of these actions apply:

| Condition | Action | Tool |
|-----------|--------|------|
| New equivalent pattern discovered | Add to Survival Patterns section, assign next Pattern ID | `Edit` skill.md |
| New killing technique found | Add to Killing Techniques section | `Edit` skill.md |
| Existing pattern confirmed correct | No change needed | — |
| Pattern description inaccurate | Update pattern section with correction | `Edit` skill.md |
| New test pattern invented | Add to Test Patterns Catalog | `Edit` skill.md |
| New project completed | Add to Project Case Studies + update stats | `Edit` skill.md |
| New project completed | Add entry to project-data.json | `Edit` project-data.json |
| Common Mistakes table has gap | Add new mistake+fix row | `Edit` skill.md |
| Quick Reference table has gap | Add new row | `Edit` skill.md |

### Step 3: Execute the Update

For each action identified in Step 2, apply the edit IMMEDIATELY after the PIT run completes. Do NOT wait for user to ask. The `settings.json` already grants Edit permission.

**Example — adding a new equivalent pattern:**
```
1. Locate the last True Equivalent Mutants section in skill.md
2. Insert new pattern with next available ID
3. Follow the existing format: Symptom / Root Cause / How to identify / Action
4. Add a row to Quick Reference table
5. Increment the pattern count in Overview line
```

**Example — updating project-data.json:**
```
1. Read project-data.json
2. Add new entry to "projects" array
3. Update summary statistics (total mutants, avg coverage)
4. If new pattern: add to "survivalPatterns" array
```

### Step 4: Determine Version Bump

Follow **strict semantic versioning** (vMAJOR.MINOR.PATCH). Current version is in [project-data.json](./project-data.json) → `skill_metadata.version`.

**Version format: vMAJOR.MINOR.PATCH**
- **v**: 版本前缀（Version 英文缩写），如 v1.0.0
- **MAJOR (主版本号)**: 功能模块有较大变动，如增加模块或整体架构变化。由项目经理决定是否修改。
- **MINOR (副版本号)**: 功能有一定增加或变化，如增加权限控制、自定义视图等。由项目经理决定是否修改。
- **PATCH (修订版本号)**: Bug 修复或小变动，修复一个严重 Bug 即可发布。由项目经理决定是否修改。

```
PATCH (vX.Y.Z → vX.Y.Z+1):  Bug fixes, corrections, stats-only updates
  v2.4.1 → v2.4.2: Fixed misleading description in Pattern 7
  v2.4.2 → v2.4.3: Corrected JUnit version in code example

MINOR (vX.Y.Z → vX.Y+1.0):  New project case, new pattern, new test pattern
  v2.4.9 → v2.5.0: Added Anagram project + Pattern 20
  v2.5.0 → v2.6.0: Added 2 new killing techniques

MAJOR (vX.Y.Z → vX+1.0.0):   Fundamental restructuring, breaking changes
  v2.6.0 → v3.0.0: Rewrote entire Survival Patterns classification
```

**Version bump decision matrix:**

| Delta Type | Bump | Example |
|-----------|------|---------|
| Stats update only (new project, no new patterns) | PATCH | v2.4.1 → v2.4.2 |
| New project + confirmed existing patterns only | PATCH | v2.4.2 → v2.4.3 |
| Minor correction to existing pattern text | PATCH | v2.4.3 → v2.4.4 |
| New equivalent mutant pattern (Pattern N+1) | MINOR | v2.4.4 → v2.5.0 |
| New killing technique (adds to Techniques section) | MINOR | v2.5.0 → v2.6.0 |
| New test pattern in Test Patterns Catalog | MINOR | v2.6.0 → v2.7.0 |
| New Iron Rule or workflow restructure | MINOR | v2.7.0 → v2.8.0 |
| Multiple MINOR-level changes in one update | MINOR (once) | v2.5.0 → v2.6.0 |
| Breaking restructuring of entire sections | MAJOR | v2.9.0 → v3.0.0 |

**Rule:** Same-day session updates the version number ONLY ONCE. All changes within the same calendar day are grouped under a single version bump. When the day changes (next calendar day), the next self-optimization cycle triggers a new version bump. Read the latest version from project-data.json each time — never use a cached value. Version numbers are strictly sequential: v2.4.1 → v2.4.2 → v2.4.3 → ... → v2.4.9 → v2.5.0 is the only allowed sequence. Never skip versions.

### Step 5: Update CHANGELOG.md

Append a changelog entry with the correct bumped version:

```
## [v{NEW_VERSION}] - {DATE}
### Added
- {Project} project case study ({N} mutants, {X}% killed)
- Pattern {N}: {name} ({category})

### Changed
- {What was modified and why}

### Verified
- {Which existing patterns were confirmed by this project}
```

### Step 6: Update README.md

**Every time** the skill is modified, the following README.md fields MUST be checked and updated:

| README Field | When to Update | Example |
|-------------|---------------|---------|
| Header line: "X 个项目、Y 个变异体" | New project added | `18 → 19 个项目, 5,642 → 5,890 个变异体` |
| "提炼自 18 个真实 Java 项目" | New project added | `18 → 19` |
| "19 个已知存活模式" | New pattern added (MINOR bump) | `19 → 20` |
| "21 个测试模式" | New test pattern added | `21 → 22` |
| "11 种真等价变异体" | New equivalent pattern added | `11 → 12` |
| "7 条 Iron Rules" | New Iron Rule added | `7 → 9` (we added 8+9) |
| Project data table (项目数/变异体数/覆盖率) | Stats change | Update all numbers |
| `skill.md（1475 行）` | skill.md line count changes | Count and update |
| `22 步完整工作流` | Workflow steps change | Update count |
| `30+ 个高频踩坑点` | Common Mistakes grow | Update count |

**README update checklist (same order as the file):**
```
☐ Line 1:  "X 个项目、Y 个变异体" — update counts
☐ Line 14: "提炼自 X 个真实 Java 项目" — update count
☐ Line 16: "19 个已知存活模式" — update if new pattern
☐ Line 17: "21 个测试模式" — update if new test pattern
☐ Line 18: "11 种真等价变异体" — update if new equivalent pattern
☐ Line 64: "skill.md（XXXX 行）" — recount and update
☐ Line 71: "7 条 Iron Rules + 22 步完整工作流" — update if changed
☐ Line 73: "30+ 个高频踩坑点" — recount and update
☐ Line 77-85: Project data table — update all stats numbers
☐ Line 91: CONTRIBUTING.md link — verify still valid
```

### Step 7: Update project-data.json version

In `skill_metadata.version`, set the new version string:
```json
"version": "v2.4.2"
```
And update `last_updated` to the current timestamp.

### Auto-Optimization Trigger Checklist

After EVERY completed PIT run, verify in order:
- [ ] Post-mortem template filled
- [ ] All survivors matched to known patterns OR new patterns created
- [ ] Equivalent mutants documented with proof (Iron Rule 9 format)
- [ ] Version bump determined (Step 4 — semantic versioning)
- [ ] CHANGELOG.md updated with new version entry (Step 5)
- [ ] project-data.json updated (new project stats + version + timestamp)
- [ ] If new pattern: skill.md Quick Reference + Survival Patterns sections updated
- [ ] If new test pattern: Test Patterns Catalog updated
- [ ] Overview statistics recalculated (total projects, mutants, avg coverage)
- [ ] README.md updated (Step 6 — all affected fields)
- [ ] Iron Rule count in README matches skill.md

### Delta Detection: When to Actually Edit the Skill

You ONLY need to edit the skill when there's a DELTA — something the skill doesn't already know:

| Situation | Delta? | Action | Version |
|-----------|--------|--------|---------|
| Survivor matches Pattern 1-19 exactly | NO | Document in post-mortem only | PATCH |
| Survivor matches a pattern but with a new sub-type | YES | Add sub-type to existing pattern | PATCH |
| Survivor requires a completely new pattern | YES | Create Pattern N+1 → update README | MINOR |
| All survivors already covered by skill | NO | Just update project-data.json stats | PATCH |
| Skill's prediction was wrong for a mutant | YES | Correct the pattern description | PATCH |
| Found a more efficient killing method | YES | Update the pattern's killing strategy | MINOR |

**Iron Rule for self-optimization: Add knowledge, don't duplicate it.** If the skill already explains how to handle a situation, don't add another explanation. Add only genuinely new information. When in doubt, check if the post-mortem's "New Discoveries" section has any checked boxes.
