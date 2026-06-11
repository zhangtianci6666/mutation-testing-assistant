# Mutation Operators & Killing Strategies

Detailed killing strategies with code examples for each of the 11 major PIT mutation operators.

---

## CONDITIONALS_BOUNDARY_MUTATOR
**Mutation:** `>` ↔ `>=`, `<` ↔ `<=`
**Killing Strategy:** Test exact boundary values
```java
@Test
public void testBoundary() {
    assertEquals(expectedAtBoundary, calculator.process(BOUNDARY_VALUE));
}
```
**Special Case - Insert Boundary:** For `if (posnList.size() >= nodeList.size())` in `insert()`, construct a heap where `posnList.size() == nodeList.size()` (e.g., `max_size=1` with 1 element). Assert the node receives coordinates from `posnList` — without `>=`, coordinates remain at default (0,0).

## VOID_METHOD_CALL_MUTATOR
**Mutation:** Remove void method call
**Killing Strategy:** Verify side effects
```java
@Test
public void testVoidSideEffect() {
    int countBefore = obj.getCallCount();
    obj.voidMethod();
    assertEquals(countBefore + 1, obj.getCallCount());
}
```
**Animation Special Case:** For `redraw()`, `delay()`, `repaint()` in animation classes, use **Counting Subclass Pattern** (see `references/test-patterns-catalog.md` Pattern 16):
```java
class CountingHeap extends Heap {
    int redrawCount = 0;
    @Override public void redraw() { redrawCount++; super.redraw(); }
}
```
Then assert exact counts: `assertEquals(34, ch.redrawCount)`. **Rule:** Always verify exact count, not just `> 0`. But **read source carefully** before asserting exact counts.

## MATH_MUTATOR
**Mutation:** `+` ↔ `-`, `*` ↔ `/`
**Killing Strategy:** Use asymmetric values (avoid 0, 1)
```java
@Test
public void testMath() {
    assertEquals(15, calculator.add(7, 8));
    assertNotEquals(1, calculator.add(7, 8)); // catches 7-8 or 7/8
}
```
**Constructor Argument Special Case:** For MATH on arguments passed to a constructor (e.g., `new ComBox(node.x - 120, node.y + 50, ...)`), assert the **constructed object's fields**, not just the caller's state:
```java
ch.addInput(99);
assertEquals(-80, ch.runningCom.topLeft.x); // kills MATH on node.x - 120
assertEquals(310, ch.runningCom.topLeft.y); // kills MATH on node.y + 50
```

**Multi-t-value Precision Kill (Astronomical/Trigonometric MATH):** When MATH mutations on `+`/`*` inside sin/cos functions survive at t=0 (where operands cancel out), use multiple t values:
```java
// t1=0: GXC_l[1]*0 = 0, so +→- or *→/ has no effect
// t1=-1,0,1,2: ensures EVERY MATH line produces detectable difference at some t
double[] zb = {3.0, 0.5};
addGxc.invoke(st, jd - 36525.0, zb); // t1=-1
assertEquals(EXPECTED_TN1, zb[0], 1e-10);
addGxc.invoke(st, jd, zb);           // t1=0
assertEquals(EXPECTED_T00, zb[0], 1e-10);
addGxc.invoke(st, jd + 36525.0, zb); // t1=1
assertEquals(EXPECTED_TP1, zb[0], 1e-10);
addGxc.invoke(st, jd + 73050.0, zb); // t1=2 (extreme)
assertEquals(EXPECTED_TP2, zb[0], 1e-10);
```
**Key insight:** Any `+→-` or `*→/` mutation changes at least one output across t=-1,0,1,2 because the operands have different relative magnitudes at each t.

## RETURN_VALS_MUTATOR (PRIMITIVE_RETURNS / NULL_RETURNS / EMPTY_RETURNS)
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

## NEGATE_CONDITIONALS_MUTATOR
**Mutation:** `==` ↔ `!=`, `>` ↔ `<=`
**Killing Strategy:** Cover both true and false branches
```java
@Test
public void testBothBranches() {
    assertTrue(obj.isValid(validInput));
    assertFalse(obj.isValid(invalidInput));
}
```

## INCREMENTS_MUTATOR
**Mutation:** `++` ↔ `--`, `i += 1` ↔ `i -= 1`
**Killing Strategy:** Verify exact iteration count, assert final loop variable value
```java
@Test
public void testLoopIterationCount() {
    List<Integer> list = new ArrayList<>();
    for (int i = 0; i < 5; i++) { list.add(i); }
    assertEquals(5, list.size());
    assertEquals(Arrays.asList(0, 1, 2, 3, 4), list);
}
```

## INVERT_NEGS_MUTATOR
**Mutation:** `-x` → `x` (remove negation); `!a` → `a` (remove boolean negation)
**Killing Strategy:** Use both positive and negative values, verify sign handling. For `!` removal, test BOTH branches.
```java
@Test
public void testNegation() {
    assertEquals(-5, calculator.negate(5));  // kills -x → x
    assertEquals(5, calculator.negate(-5));
}
```
**⚠️ Path-Dependent Equivalence Warning:** INVERT_NEGS on variables that only affect sub-day-precision corrections (e.g., `sun[1] = -sun[1]` used only inside aberration correction for lx=0) is genuinely equivalent for the public API path. The negation changes the sign of a latitude term whose effect on the final integer day is zero. BUT the negation IS killable through the non-public lx≠0 path — it's NOT purely equivalent, just impossible to detect through the public API.
    assertTrue(Math.abs(-5) > 0);   // combine with sign check
}

@Test
public void testBooleanNegation() {
    // d.increment() returns true for success, false for overflow
    // INVERT_NEGS on `if (!d.increment())` makes it `if (d.increment())`
    // Must test BOTH: normal day (true→enters block) AND end-of-month (false→skips block)
    Date normal = new Date(1, 15, 2000);
    normal.increment();
    assertEquals(16, normal.getDay().getDay());

    Date endOfMonth = new Date(1, 31, 2000);
    endOfMonth.increment();
    assertEquals(1, endOfMonth.getDay().getDay());
}
```

## REMOVE_CONDITIONALS_EQUAL_ELSE / REMOVE_CONDITIONALS_ORDER_ELSE
**Mutation:** Replace `if (cond)` with `if (false)` (else branch always taken)
**Killing Strategy:** Cover both branches and ensure the `if`-branch produces observable different state
```java
@Test
public void testHighlightBranch() {
    Node noHl = new Node(5);
    ch.drawLeafNode(g, noHl);
    verify(g).setColor(Color.blue); // kills removed conditional (would be black)

    Node hl = new Node(5); hl.highlight = true;
    ch.drawLeafNode(g2, hl);
    verify(g2, times(2)).setColor(Color.black); // once for if, once after fillRect
}
```
**Rule:** For `if/else` with primitive returns or color changes, testing both branches is mandatory.

## CONSTRUCTOR_CALLS_MUTATOR
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

## Quick-Kill Flowchart

When you see a surviving mutant, follow this decision tree:

```
SURVIVED mutant
├─ MATH on new ArrayList<>(expr) or new HashMap<>(expr)?
│  → Pattern 15: Equivalent. Document and move on. (30 min saved)
│
├─ MATH on Math.random() * N in constructor?
│  → Pattern 19: Loop-scan with reflection. 50 instances, assert param ≠ 0.
│
├─ CONDITIONALS_BOUNDARY on >= or < in binary search guard?
│  → Pattern 17: Trace both paths. Both converge → equivalent.
│
├─ Private method MATH with both read+write callers?
│  → Pattern 18: Self-consistent. Need reflection-based internal state inspection.
│
├─ Compound && condition, only sub-conditions survive?
│  → Pattern 16: Cross-method data-flow. Likely dead code → equivalent.
│
├─ VOID_METHOD_CALL on library objects in wrapper project?
│  → Pattern 20: Wrapper VOID equivalence. Document. Ceiling ~65-75%.
│
├─ TIMED_OUT in while(true) with guard-condition exit?
│  → Pattern 13: Valid kill. Do NOT try to "fix".
│
├─ Base class method uncovered, all subclasses override it?
│  → Pattern 12: Anonymous subclass without override.
│
├─ Animation method with intermediate state + final restore?
│  → Pattern 9: Equivalent. Skip intermediate MATH/BOUNDARY/INCREMENTS.
│
└─ None of the above?
   → See references/test-patterns-catalog.md for advanced techniques.
```
