# Survival Patterns & Killing Strategies

**Core principle:** Not all survived mutants are equivalent. Three categories: **True Equivalent** (mathematically impossible to kill), **Conditionally Killable** (hard but killable with advanced techniques), and **Killing Techniques** (methods to reach and kill specific mutants).

---

## True Equivalent Mutants (不可杀等价变异体)

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
**Action:** Document as equivalent if proven.

### Pattern 3: Unconditional Return (无条件返回)
**Symptom:** `TRUE_RETURNS` or `FALSE_RETURNS` survives on a method that always returns the same constant.
**Root Cause:** Method body always produces the same boolean regardless of input.
```java
public boolean increment() {
    currentPos++;
    return true;  // Always true. TRUE_RETURNS is equivalent.
}
```
**Action:** Document as equivalent.

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
**Action:** Document as equivalent. No test can distinguish them.

### Pattern 5: Dead Store (死存储)
**Symptom:** `MATH` on `index += node.numElements` survives in `remove(Object)`. Also: `MATH` and `CONDITIONALS_BOUNDARY` on any variable that is reset by a cleanup/init method called at the end of the enclosing method.
**Root Cause:** The variable is updated but its value is either never read OR is explicitly reset before any subsequent read. **Reset-method variant:** Methods like `initate(cells)` that reinitialize `data`, `dataPointer`, `charPointer` at the end of `interpret()` make ALL intermediate mutations on these fields unobservable.
```java
// Standard dead store:
while (node != null) {
    for (...) {
        if (match) { removeFromNode(node, ptr); return true; }  // index never used here
    }
    index += node.numElements;  // Dead store: value never read
    node = node.next;
}

// Reset-method variant:
public void interpret(String str) throws Exception {
    for (; cp < str.length(); cp++)
        process(str.charAt(cp));           // MATH on data[dp]++, dataPointer+=, cp+= — all dead
    initate(data.length);                  // ← resets data, dataPointer, charPointer
}
```
**Action:** Document as equivalent. Check for reset/init methods called at end of public methods before investing effort in killing intermediate-state MATH/CONDITIONALS_BOUNDARY mutants.

### Pattern 6: Defensive Redundancy (防御式冗余)
**Symptom:** `REMOVE_CONDITIONALS_EQUAL_ELSE` on `if (c == null)` survives in `containsAll`/`addAll`/`removeAll`/`retainAll`. Also: `VOID_METHOD_CALL`/`REMOVE_CONDITIONALS` on setters whose effect is overwritten by lazy-loading or downstream recomputation. **Bracket-matching variant:** `REMOVE_CONDITIONALS` on BK_LEFT/BK_RIGHT branch conditions survives — the backward scan in BK_RIGHT compensates for removed BK_LEFT forward-skip, creating self-correcting behavior.
**Root Cause:** Removing the explicit null check does not change behavior because the next statement (`c.iterator()`) implicitly throws the same `NullPointerException` on null input. **Lazy-loading variant:** `setFestivals()` called in `buildDPInfo()` is redundant because `getFestivals()` lazy-loads the same data via `buildDayFestivals()` — both paths compute identical results. **Bracket-matching variant:** In Brainfuck-derivative interpreters with BK_LEFT forward-skip + BK_RIGHT backward-scan, removing individual bracket-matching conditions (L167 BK_LEFT check, L168 data==0 check, L173/L175 inner BK_LEFT/BK_RIGHT checks) does not change observable loop behavior because the BK_RIGHT backward-scan independently recomputes the matching bracket position.
**How to identify:** Check if: (1) the removed check/method call guards against a condition that the NEXT statement also guards against, (2) the setter writes data that a downstream getter recomputes identically via lazy-loading/caching, OR (3) the code has dual forward/backward traversal that converges to the same target regardless of direction choice.
**Action:** Document as equivalent.

### Pattern 7: Fail-Fast Counter Monotonicity (fail-fast 计数器单调性)
**Symptom:** `MATH` on `modCount++` survives in `insertIntoNode`/`removeFromNode`.
**Root Cause:** `modCount` is only used for inequality comparison against `expectedModCount`. Both `++` and `--` change the value away from the expected value, triggering `ConcurrentModificationException` equally.
**Action:** Document as equivalent.

### Pattern 8: Compound Condition Side-Effect (复合条件副作用) 🔧 可杀死

> **分类说明:** 此模式在特定条件下等价（循环最多执行1次时），但可通过多迭代触发杀死。不属于真等价变异体。
**Symptom:** `REMOVE_CONDITIONALS_ORDER_ELSE` on `while ((p -= node.numElements) > index)` survives despite loop iterations.
**Root Cause:** PIT replaces `while (expr)` with `while (false)`, but the side effect `p -= node.numElements` inside the condition expression STILL EXECUTES before the jump. If the loop naturally executes exactly 0 or 1 times, the mutant may be equivalent because the single decrement still happens.
**Action:** To kill, use an index where the original loop must execute 2+ times (e.g., target element is in a node at least 2 hops from the start/end). See `references/test-patterns-catalog.md` Pattern 15 (Backward Loop Multi-Iteration Trigger).

### Pattern 9: Animation State Restoration (动画状态恢复)
**Symptom:** `MATH`, `VOID_METHOD_CALLS`, `INCREMENTS`, or `CONDITIONALS_BOUNDARY` survive in animation methods like `exchangeArrow`, `moveLast2First`, `input2heap`, `drawArrow`, `addOutput`.
**Root Cause:** Animation methods update intermediate coordinates multiple times, call `redraw()` for each frame, but **restore final state** at the end. Mutants that change intermediate steps produce different visual trajectories but identical final state.
```java
for (int i = 0; i < 5; i++) {
    movingNode.x += (destX - srcX)/5;  // MATH on +=, /, - all survive
    redraw();
}
movingNode.x = destX;  // Final state is restored regardless of loop mutations
```
**How to identify:** Look for: (1) loop with incremental position changes, (2) `redraw()` inside loop, (3) explicit final position assignment after loop. If all three exist, MATH/BOUNDARY/INCREMENTS mutants inside the loop are likely equivalent.
**Action:** Document as equivalent. VOID_METHOD_CALLS on `redraw()` can sometimes be killed with Counting Subclass Pattern (see `references/test-patterns-catalog.md` Pattern 16).

### Pattern 10: Ternary Max/Min Symmetry (三元最值对称性)
**Symptom:** `CONDITIONALS_BOUNDARY` or `REMOVE_CONDITIONALS` on `rightBottom > leftBottom ? rightBottom : leftBottom` survives. Also: `CONDITIONALS_BOUNDARY` on `if (charPointer + tokenLen <= str.length())` survives at the exact boundary.
**Root Cause:** In a complete binary tree, left subtree depth is always >= right subtree depth. Thus `>` and `>=` produce the same result. **Substring boundary variant:** When `cp+dTL == len` exactly, both the if-branch (`substring(cp, cp+dTL)`) and the else-branch (`substring(cp, cp+(len-cp))`) produce identical substrings because `len-cp == dTL`. The CONDITIONALS_BOUNDARY mutation (`<=` → `<`) changes which branch is taken, but both produce the same token.
```java
int rightBottom = bottomMostPosn(node.getRightNode());
int leftBottom = bottomMostPosn(node.getLeftNode());
return (rightBottom > leftBottom ? rightBottom : leftBottom);
// For complete tree: leftBottom >= rightBottom always, so >, >=, false all equivalent

// Substring boundary variant:
if (charPointer + defaultTokenLength <= str.length())        // <= → < : at boundary cp+dTL==len,
    token = str.substring(cp, cp+dTL);                       // both branches produce substring(cp, len)
else
    token = str.substring(cp, cp + (len - cp));              // = substring(cp, cp + dTL) since len-cp=dTL
```
**Action:** Document as equivalent.

### Pattern 11: Default Value Defense (防御性默认值等价)
**Symptom:** `REMOVE_CONDITIONALS_EQUAL_IF` or `REMOVE_CONDITIONALS_EQUAL_ELSE` survives in defensive initialization code.
**Root Cause:** A variable is initialized to a safe default before a conditional assignment. Removing the conditional leaves the default value, which is identical to the "else" branch outcome.
```java
int n_lines = 0;  // Default value
if (inStream != null) {
    // ... read lines into buffer ...
    n_lines = count;
}
// If inStream is null in tests, removing the if leaves n_lines=0, same as original
```
**Action:** To kill, construct a test where the conditional branch produces a NON-default value. If impossible via public API, use reflection or document as equivalent.

---

## Killing Techniques (杀活技巧)

These are NOT equivalent — they are advanced techniques for reaching and killing specific mutants.

### Pattern 12: Polymorphic Base Default Path (多态基类默认路径) 🛠️
**Symptom:** One line uncovered in a base class method (e.g., `return null` in `parseValue`), despite all tests passing and all subclasses being tested.
**Root Cause:** All concrete subclasses override the base method. The base implementation's return statement is never polymorphically dispatched.
```java
// Option<T> base class
protected T parseValue(String arg, Locale locale) {
    return null;  // ← uncovered — all subclasses override this
}
```
**How to kill:** Create an anonymous subclass that intentionally does NOT override the target method:
```java
CMD.Option<String> opt = new CMD.Option<String>("test", true) {};
String result = opt.getValue("anything", Locale.US);
assertNull(result, "Base parseValue must return null");
```

### Pattern 13: Infinite Loop TIMED_OUT via Removed Guard Condition (移除守卫条件的无限循环超时) 🛠️
**Symptom:** `TIMED_OUT` (NOT SURVIVED) on `REMOVE_CONDITIONALS_EQUAL_ELSE` or `REMOVE_CONDITIONALS_ORDER_ELSE` in a `while(true)` loop.
**Root Cause:** When a `while(true)` loop uses `if (cond) return;` as its only exit, removing the if-condition causes infinite loop → test timeout → PIT correctly labels this as TIMED_OUT = killed.
```java
while (true) {
    T o = getOptionValue(option, null);
    if (o == null) { return result; }  // ← REMOVE → if(false) → else always → infinite loop → TIMED_OUT
    else { result.add(o); }
}
```
**Action:** TIMED_OUT = killed. Do NOT try to "fix" this. Document as positive signal.

### Pattern 14: Reflection Map State Injection (反射Map状态注入) 🛠️
**Symptom:** An internal `Map` or `List` field controls a code path that cannot be reached through normal public API calls.
**Root Cause:** The normal public API never creates the specific internal state (e.g., an empty List in a Map value) that triggers the target code path.
```java
if (v == null) { return def; }
else if (v.isEmpty()) { return null; }  // ← unreachable via normal API
```
**How to kill:** Use reflection to inject the exact internal state:
```java
CMD c = new CMD();
c.parseSafe(new String[]{});  // Initialize values map
Field valuesField = CMD.class.getDeclaredField("values");
valuesField.setAccessible(true);
Map<String, List<?>> values = (Map<String, List<?>>) valuesField.get(c);
values.put("emptyOpt", new ArrayList<Object>());  // Inject empty list
assertNull(c.getOptionValue(opt, "def"));  // v.isEmpty() → return null
```
**Key rule:** Always call the normal initialization path first (e.g., `parse()`), then inject the edge-case state via reflection.

---

## True Equivalent Mutants (continued)

### Pattern 15: ArrayList Initial Capacity Equivalence (集合初始容量等价) 🟰
**Symptom:** `MATH` on `new ArrayList<T>(t - 1)` survives — `t-1 → t+1` or `t-1 → t*1` etc.
**Root Cause:** ArrayList's constructor argument sets only the **initial capacity** — a performance hint, not semantic. The list auto-grows as needed.
**Action:** Document as equivalent. **This is the single most common equivalent mutant pattern.** Time saved by recognizing early: ~30 min per occurrence.

### Pattern 16: Compound Condition Dead Code (复合条件死代码)
**Symptom:** All mutations on the second/third part of a compound `&&` condition survive, even though the first part kills.
**Root Cause:** An earlier method call or guard clause guarantees the semantic invariant that makes later conditions unreachable.
```java
if (keys.isEmpty() ||                          // ← part 1: kills when removed
    (index == keys.size() - 1 &&                // ← part 2: NEVER TRUE, survives
     keys.get(index).compareTo(key) < 0)) {     // ← part 3: NEVER TRUE, survives
```
**Action:** Document as equivalent. All CONDITIONALS_BOUNDARY, MATH, and REMOVE_CONDITIONALS on dead sub-expressions are equivalent.

### Pattern 17: Binary Search Boundary Equivalence (二分搜索边界等价)
**Symptom:** `CONDITIONALS_BOUNDARY` on `>=` or `<` in binary search guard clauses survives.
**Root Cause:** Binary search implementations often have early-exit "guard" checks. When mutated, the binary search loop still finds the same index.
**Action:** Document as equivalent. Note: REMOVE_CONDITIONALS and NEGATE_CONDITIONALS mutations are usually **killable**.

---

## Conditionally Killable (条件可杀死)

### Pattern 18: Self-Consistent Internal Method (自洽内部方法) 🔧
**Symptom:** `MATH` mutations in a private helper method survive despite both the method and its callers being fully covered.
**Root Cause:** The mutated method is called by **both the write path and the read path** (e.g., `add()` and `contains()`). The mutation changes the internal computation, but since both paths use the same mutated version, they remain self-consistent.
```java
// createHashes — called by both add() and contains()
private int[] createHashes(int data, int hashes) {
    for (int i = 0; i < hashes; i++) {
        hashValues[i] = ((i + hashParam1) * data + hashParam2) % 701;
    }
    return hashValues;
}
// add() calls createHashes → sets bits
// contains() calls createHashes → checks same bits → always matches!
```
**Killing Strategy — Internal State Inspection via Reflection:** Inject known hash params via reflection, compute expected bit positions, verify exact bits via BitSet reflection. See `references/test-patterns-catalog.md` Pattern 14.

### Pattern 19: Probabilistic Constructor Parameter (概率性构造参数) 🔧
**Symptom:** `MATH` on `Math.random() * N` in a constructor survives.
**Root Cause:** Mutation `* 100 → / 100`: result is always 0 when cast to `int`. If the random parameter happens to be 0 in the original test run, it appears equivalent.
**Killing Strategy — Loop-Scan with Reflection:** Sample 50 instances, assert at least one has param ≠ 0. Original: P(param==0) = 1/100. Mutated: P(param==0) = 1 → never finds non-zero → assertion fails → KILLED.

### Pattern 20: Wrapper-Project VOID Equivalence (包装器项目VOID等价) 🟰
**Symptom:** VOID_METHOD_CALL on library internal methods (`parser.close()`, `parser.handleResovleTask()`, `serializer.config()`) survives across all overloads.
**Root Cause:** The project is a thin wrapper around a library. Void method calls act on library objects created as local variables — discarded after method returns, side effects unobservable from outside.
**How to identify:** Look for projects importing a large third-party library and wrapping its API. If library objects are not stored in any field and not returned, the void calls are equivalent.
**Impact on coverage ceiling:** Wrapper projects have an inherent ceiling of ~65-75%. ~20-25% of mutations are VOID on library internals (equivalent).
**Action:** Document as equivalent. Recognize wrapper projects early to set realistic expectations.
