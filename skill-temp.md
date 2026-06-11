---
name: mutation-testing-assistant
description: Use when analyzing PIT mutation testing reports with survived mutants, low mutation coverage, or when writing tests to kill specific mutation operators like CONDITIONALS_BOUNDARY, VOID_METHOD_CALL, MATH, RETURN_VALS, INCREMENTS, INVERT_NEGS, NEGATE_CONDITIONALS, EMPTY_RETURNS, NULL_RETURNS, REMOVE_CONDITIONALS_EQUAL_ELSE, REMOVE_CONDITIONALS_ORDER_ELSE, CONSTRUCTOR_CALLS. Includes equivalent mutant detection, reflection-based boundary injection, platform-agnostic void-method verification, AWT/GUI animation testing patterns, and headless-environment compatibility rules.
---

# Mutation Testing Assistant

## Overview

Systematic approach to analyze and kill survived PIT mutation testing mutants. Based on analysis of 23 Java projects, 7,568+ mutants, 87.7% average coverage on algorithmic/framework code. Covers 20 survival patterns, 11 mutation operators, 23 test patterns, and 9 Iron Rules.

**Core principle:** Match survived mutants to known survival patterns, apply corresponding killing strategy. **Compilation verification is mandatory before any PIT run.**

**Structured data:** [project-data.json](./project-data.json) contains canonical operator list, survival pattern index, killing rules dispatch table, test pattern→source project mapping, and per-project statistics.

## When to Use

- Running PIT mutation testing on Java projects with mutation coverage below target
- Specific mutation operators surviving (BOUNDARY, VOID_CALL, MATH, RETURN_VALS)
- Writing tests specifically to improve mutation score
- Need to distinguish killable mutants from equivalent mutants
- GUI/AWT/Animation classes, headless-environment PIT issues, or pre-existing compilation errors
- Generic-heavy projects, inheritance-heavy projects, or wrapper/library projects

**Do NOT use for:** General unit testing advice (not mutation-specific), other mutation tools without adaptation

---

## ⛔ EXECUTION PROTOCOL — READ BEFORE DOING ANYTHING

```
┌──────────────────────────────────────────────────────────────────────────┐
│                                                                          │
│   RULE 0: YOU MAY NOT ADVANCE TO THE NEXT CLASS UNTIL:                   │
│     ✅ ALL mutants in current class are KILLED or TIMED_OUT, OR           │
│     ✅ ALL survivors are documented as equivalent with PROOF (Iron Rule 9)│
│                                                                          │
│   ⛔ If even ONE mutant is SURVIVED and NOT documented as equivalent      │
│      with a specific WHY explanation, you MUST write MORE tests for       │
│      THIS SAME CLASS and run PIT AGAIN. No exceptions. No shortcuts.     │
│                                                                          │
│   ⛔ YOU MAY NOT:                                                        │
│      - Advance to the next class with ANY undocumented survivor          │
│      - Mark a mutant "equivalent" without explaining WHY it can't die    │
│      - Skip a survivor because "it's probably equivalent"                │
│      - Write tests for multiple classes in a single response             │
│      - Stop the loop to "summarize" or "ask the user" while survivors    │
│        that are NOT proven equivalent remain                              │
│                                                                          │
│   ────────────────────────────────────────────────────────────────────   │
│                                                                          │
│   CORRECT BEHAVIOR — THIS IS AN INFINITE LOOP UNTIL GATE PASSES:         │
│   1. List all classes → pick ONE → announce it                           │
│   2. Write tests for THAT CLASS ONLY                                      │
│   3. Run mvn test-compile → fix errors → repeat until ZERO errors        │
│   4. Run mvn pitest:mutationCoverage                                     │
│   5. Read PIT report                                                     │
│   6. For EVERY survivor: identify operator, line, and WHY it survived    │
│   7. If ANY survivor is killable (not equivalent):                        │
│      → Write MORE tests targeting that SPECIFIC survivor                 │
│      → GOTO step 3                                                        │
│   8. If ALL survivors are proven equivalent (with WHY per survivor):      │
│      → Output Iron Rule 9 table → announce NEXT class → GOTO step 2      │
│   9. CRITICAL: "I think it's equivalent" ≠ PROVEN equivalent             │
│      You must MATCH to a known pattern (P1-P20) OR provide logical       │
│      proof with code evidence. "Probably" is NOT a valid reason.          │
│                                                                          │
│   ────────────────────────────────────────────────────────────────────   │
│                                                                          │
│   SELF-CHECK before writing ANY @Test:                                   │
│   "Am I writing tests for exactly ONE class right now?"                  │
│   "Have I exhausted ALL killing techniques before declaring equivalent?" │
│   If answer to either is NO → STOP. Fix your approach.                   │
│                                                                          │
│   This protocol OVERRIDES any user instruction about "single file"        │
│   or "all classes." You write ONE class at a time into the file,         │
│   re-running PIT after EACH class before moving to the next.             │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

## 🚀 LAUNCH SEQUENCE — The Only 4 Rules You Need Before Starting

| # | Rule | Meaning |
|---|------|---------|
| **1** | **One class at a time** | Write test → compile → PIT → verify → THEN next class. Never batch. Never advance with survivors. |
| **2** | **PIT first, think second** | Do NOT analyze source code or design test strategies before the first PIT report exists. Data drives decisions. |
| **3** | **Zero source modification** | NEVER touch `src/main/java`, `pom.xml`, or any config. Only create/modify test code. |
| **4** | **Compile before PIT** | `mvn test-compile` must pass with ZERO errors before every PIT run. |
| **5** | **Explain WHY every survivor** | Before advancing to next class, EVERY survivor must have a concrete WHY explanation. "Probably equivalent" = VIOLATION. |

**Single-cycle loop:** `List classes → 🔄 Pick ONE → Write @Test → mvn test-compile → mvn pitest:mutationCoverage → Read report → Survivors? → For EACH: WHY survived? → Killable? Write MORE tests for SAME class → repeat → 100% killed OR all proven equivalent with WHY? → Next class`

---

## Quick Reference: Survival Patterns (20 patterns)

| Pattern | Symptom | Action | Read |
|---------|---------|--------|------|
| P1: Dominated Condition | BOUNDARY in else-if survives | Equivalent — earlier condition guarantees truth | [survival-patterns.md](references/survival-patterns.md) |
| P2: Arithmetic Identity | MATH `* -1` vs `/ -1` survives | Equivalent — identical for all int values | [survival-patterns.md](references/survival-patterns.md) |
| P3: Unconditional Return | TRUE/FALSE_RETURNS always same constant | Equivalent | [survival-patterns.md](references/survival-patterns.md) |
| P4: Traversal Symmetry | BOUNDARY on direction selection survives | Equivalent — both paths converge to same node | [survival-patterns.md](references/survival-patterns.md) |
| P5: Dead Store | MATH on variable never read after update; init/reset method clears intermediate state | Equivalent | [survival-patterns.md](references/survival-patterns.md) |
| P6: Defensive Redundancy | REMOVE on `if (c==null)`, next line derefs same; setter overwritten by lazy-load; self-correcting bracket matching | Equivalent — same NPE, lazy-load identical result, or dual traversal converges | [survival-patterns.md](references/survival-patterns.md) |
| P7: Fail-Fast Counter | MATH on `modCount++` survives | Equivalent — only used in `!=` comparison | [survival-patterns.md](references/survival-patterns.md) |
| P8: Compound Side-Effect | REMOVE on `while((p-=x)>idx)` survives | Killable — use multi-iteration trigger | [survival-patterns.md](references/survival-patterns.md) |
| P9: Animation Restore | MATH/VOID in animation loop survives | Equivalent — final state explicitly restored | [survival-patterns.md](references/survival-patterns.md) |
| P10: Ternary Symmetry | BOUNDARY on `rightBottom > leftBottom` survives; substring boundary cp+dTL==len | Equivalent — left >= right always; both branches same substring | [survival-patterns.md](references/survival-patterns.md) |
| P11: Default Value Defense | REMOVE on defensive init survives | Killable — inject non-default path | [survival-patterns.md](references/survival-patterns.md) |
| P12: Polymorphic Default | Base method uncovered, all subclasses override | Killable — anonymous subclass WITHOUT override | [survival-patterns.md](references/survival-patterns.md) |
| P13: Infinite Loop Timeout | TIMED_OUT on REMOVE in while(true) | **Valid kill** — DO NOT fix | [survival-patterns.md](references/survival-patterns.md) |
| P14: Reflection Map Injection | isEmpty() branch unreachable via API | Killable — inject empty list via reflection | [survival-patterns.md](references/survival-patterns.md) |
| P15: ArrayList Capacity | MATH on `new ArrayList<>(expr)` survives | Equivalent — capacity is perf hint only | [survival-patterns.md](references/survival-patterns.md) |
| P16: Compound Dead Code | Sub-conditions of `&&` always survive | Equivalent — cross-method data-flow proves constant | [survival-patterns.md](references/survival-patterns.md) |
| P17: Binary Search Boundary | BOUNDARY on guard `>=` survives | Equivalent — both paths converge to same index | [survival-patterns.md](references/survival-patterns.md) |
| P18: Self-Consistent Method | MATH in method called by read+write paths | Killable — reflection-based internal state inspection | [survival-patterns.md](references/survival-patterns.md) |
| P19: Probabilistic Constructor | MATH on `Math.random()*N` survives | Killable — loop-scan 50 instances, assert param≠0 | [survival-patterns.md](references/survival-patterns.md) |
| P20: Wrapper VOID Equiv. | VOID on library internals (parser.close, etc.) | Equivalent — local variables discarded after return | [survival-patterns.md](references/survival-patterns.md) |

---

## Mutation Operators — Quick Dispatch

When a specific operator survives, apply the corresponding strategy. Full code examples in [killing-strategies.md](references/killing-strategies.md).

| Operator | Mutation | Strategy |
|----------|----------|----------|
| CONDITIONALS_BOUNDARY | `>` ↔ `>=`, `<` ↔ `<=` | Test exact boundary values |
| VOID_METHOD_CALL | Remove void call | Verify side effects (state/logs/counts) |
| MATH | `+`↔`-`, `*`↔`/` | Asymmetric values (avoid 0, 1) |
| RETURN_VALS | Return null/0/false/"" | Assert exact values, not just non-null |
| NEGATE_CONDITIONALS | `==`↔`!=`, `>`↔`<=` | Cover BOTH branches |
| INCREMENTS | `++`↔`--`, `+=`↔`-=` | Exact iteration count + final value |
| INVERT_NEGS | `-x`→`x`, `!a`→`a` | Both positive/negative values; BOTH boolean outcomes |
| REMOVE_CONDITIONALS | `if(cond)`→`if(false)` | Both branches produce different observable state |
| CONSTRUCTOR_CALLS | Remove `new` → null | Assert fields non-null + properly initialized |

**Quick-kill flowchart:** See [killing-strategies.md](references/killing-strategies.md#quick-kill-flowchart) for the decision tree.

---

## Workflow

### Iron Rules (9 total)

**Iron Rule 1: Run PIT FIRST, think AFTER.** Do NOT analyze source code, design test strategies, or hypothesize about equivalent mutants before running PIT.

**Iron Rule 2: Assume Killable Until Proven Equivalent.** Do NOT guess a mutant is equivalent before exhausting all test techniques.

**Iron Rule 3: Verify Path Coverage with Internal State Assertions.** Assert package-private fields to prove code reached the intended location.

**Iron Rule 4: Read Source Before Asserting Exact Counts.** When using Counting Subclass Pattern, read exact source lines before writing assertions.

**Iron Rule 5: Check Headless Compatibility Before Writing GUI Tests.** Instantiate the component standalone first; skip if HeadlessException.

**Iron Rule 6: One Class at a Time — MANDATORY PER-CLASS PIT GATE.**

```
┌─────────────────────────────────────────────────────────────────┐
│              HARD GATE: Per-Class PIT Loop                       │
│                                                                  │
│  FOR EACH CLASS (one at a time, in complexity order):            │
│    1. Write test code for THIS CLASS ONLY                        │
│    2. Run `mvn test-compile` → fix errors → repeat until pass    │
│    3. Run `mvn pitest:mutationCoverage`                          │
│    4. Read PIT report for THIS CLASS                             │
│    5. If SURVIVED mutants remain:                                │
│       → Match to patterns → write MORE tests → GOTO step 2       │
│    6. If 100% killed OR equivalent mutants documented:            │
│       → GOTO next class                                          │
│                                                                  │
│  VIOLATION: Writing tests for Class B before PIT confirms        │
│  Class A at 100% (or equivalent-documented) is FORBIDDEN.        │
└─────────────────────────────────────────────────────────────────┘
```

Attack classes in ascending complexity order:
1. **Data structure classes** (Node, POJOs) — easy wins
2. **Simple business classes** (utilities) — straightforward logic
3. **Complex algorithm classes** (Heap, tree operations) — need internal state inspection
4. **GUI/Animation classes** — need subclass mocking and equivalence analysis

**Iron Rule 7: Verify Compilation Before PIT — No Exceptions.** Run `mvn test-compile` and ensure ZERO compilation errors before PIT. Generic type mismatches are the #1 culprit.

**Iron Rule 8: Zero Source Modification.** Only create/modify test code. NEVER touch `src/main/java`, `pom.xml`, or build config.

**Iron Rule 9: Equivalent Mutant Accountability — Mandatory WHY Per Survivor.** When a class cannot reach 100% kill rate after exhausting ALL killing techniques, produce a precise assessment for EVERY surviving mutant. Each entry MUST include: (1) specific code line and snippet, (2) logical proof of WHY it cannot be killed, (3) which pattern it matches (P1-P20), and (4) what techniques were tried and failed. "Probably equivalent" or "seems equivalent" is FORBIDDEN — only "proven equivalent" with evidence.
```
┌──────────────────────────────────────────────────────────────────────┐
│ Equivalent Mutant Report: {ClassName}                                 │
├──────────┬────────┬──────────────────────────────────────────────────┤
│ Mutator  │ Line   │ Why Equivalent (PROOF required)                   │
├──────────┼────────┼──────────────────────────────────────────────────┤
│ MATH     │ L42    │ new ArrayList(t-1): initial capacity is perf      │
│          │        │ hint only — list auto-grows. Same behavior for    │
│          │        │ all capacity values. Pattern P15. Tried: 3+ runs  │
│          │        │ with varying sizes — same result regardless.      │
├──────────┼────────┼──────────────────────────────────────────────────┤
│ BOUNDARY │ L67    │ else-if dominated: earlier `if(a>=0)` guarantees  │
│          │        │ a>=0 is false when else-if evaluated, so `a<0`    │
│          │        │ ≡ `a<=0` here. Pattern P1. Source lines: L65-68.  │
├──────────┼────────┼──────────────────────────────────────────────────┤
│ VOID     │ L103   │ parser.close(): parser is local var, discarded    │
│          │        │ after method returns. Side effects unobservable.  │
│          │        │ Pattern P20 (Wrapper VOID). Tried: Mockito spy,   │
│          │        │ Counting subclass — no accessible side channel.   │
└──────────┴────────┴──────────────────────────────────────────────────┘
```
**⛔ CRITICAL: Before advancing to the next class, you MUST output this table with a WHY for every survivor. If you cannot fill in a specific "Why Equivalent" for a survivor, that mutant is NOT equivalent — go back and write more tests.**

### BEFORE YOU START: Class Inventory + Complexity Ranking

**MANDATORY** before writing any test code:

```
1. List ALL business classes in src/main/java
2. Rank them by complexity (see Iron Rule 6 tiers)
3. Output the ordered attack list
4. Mark CURRENT class with 🔄, pending with ⏳
5. SAY OUT LOUD: "I will ONLY write tests for {CURRENT_CLASS}."
6. Proceed to Per-Class Loop FOR THE CURRENT CLASS ONLY
```

### Per-Class Loop — THIS IS AN INFINITE WHILE LOOP, NOT A CHECKLIST

**⛔ CRITICAL: This loop does NOT end until the gate passes — PERIOD. After every PIT run with survivors, you write MORE tests and run PIT AGAIN. You do NOT stop, summarize, ask the user, or advance — you keep going until 100% kill or ALL survivors are proven equivalent with a WHY explanation for EACH one.**

```
WHILE (class has SURVIVED mutants that are NOT documented as equivalent with WHY):
    FOR EACH survivor:
        1. Read the source line where the mutation occurred
        2. Identify WHY it's surviving (match to P1-P20 patterns)
        3. If killable: pick the right killing technique → write test
        4. If possibly equivalent: exhaust ALL techniques before declaring
    write MORE tests → mvn test-compile (ZERO errors) → mvn pitest → read report
    → survivors remain? → LOOP AGAIN. Do NOT stop.
```

**⛔ If you find yourself about to advance to the next class and there are survivors, STOP. Ask yourself: "Have I explained WHY each survivor can't be killed?" If the answer is NO, you MUST continue the loop.**

**⛔ Each response you send MUST end with one of these two lines:**

```
🔄 Class {X}/{N}: {ClassName} — {M} survivors remain ({S} SURVIVED, {T} TIMED_OUT). Every non-equivalent mutant WILL be killed. Reading {reference-file} to write next test...
```
```
✅ Class {X}/{N}: {ClassName} — {K} killed, {E} equivalent (each with WHY documented below). Self-opt: {no new knowledge | new P{N} added | {file} updated}. Advancing to next class.
```

**The "Self-opt" field in the ✅ line is MANDATORY. It forces you to run through the Self-Optimization Steps 1-3 before claiming a class is done. If you cannot write this field, you haven't done self-optimization.**

**If you end a response without one of these lines and survivors still exist, you have VIOLATED the loop.**

--- 

**⛔ HARD RULE: Before writing ANY test code for a pattern, you MUST `Read` the corresponding reference file(s). The Quick Reference table gives only 1-line summaries — NOT enough detail to write correct tests. Skipping the read = guessing = wasted PIT runs.**

**Analysis phase (after each PIT run):**
0. **MANDATORY — List EVERY survivor with WHY it survived:** For EACH survived mutant, state: operator, line number, and your hypothesis for WHY it survived. If you can't hypothesize why, you haven't read the source code carefully enough. Read the source line BEFORE writing any test.
1. **Identify survived mutants** for CURRENT CLASS ONLY; distinguish SURVIVED from TIMED_OUT (TIMED_OUT = killed, P13 in [survival-patterns.md](references/survival-patterns.md))
2. **Match to Survival Pattern** — see Quick Reference table above; for full details read [survival-patterns.md](references/survival-patterns.md). Every survivor MUST be matched: either to a known pattern (P1-P20) or identified as a new killable case.
3. **Quick-kill: ArrayList capacity** — MATH on `new ArrayList<>(expr)` → P15 in [survival-patterns.md](references/survival-patterns.md), equivalent — explain WHY: "capacity is perf hint, same behavior regardless"
4. **Quick-kill: Probabilistic** — MATH on `Math.random()*N` → P19 in [survival-patterns.md](references/survival-patterns.md), loop-scan with reflection
5. **Check Self-Consistent** — private method MATH, read+write callers? → P18 in [survival-patterns.md](references/survival-patterns.md); need [test-patterns-catalog.md](references/test-patterns-catalog.md) Pattern 14
6. **Check Compound Dead Code** — sub-conditions of `&&` survive? → P16 in [survival-patterns.md](references/survival-patterns.md), cross-method analysis — explain WHY: "earlier condition guarantees later conditions are never reached"
7. **Check Binary Search** — BOUNDARY on guard clauses? → P17 in [survival-patterns.md](references/survival-patterns.md), trace both paths — explain WHY: "both paths converge to same index"
8. **Check Animation Restore** — intermediate state overwritten? → P9 in [survival-patterns.md](references/survival-patterns.md), likely equivalent; also read [awt-gui-testing.md](references/awt-gui-testing.md). Explain WHY: "final state explicitly restored after loop"
9. **Check Polymorphic Base** — base method uncovered, subclasses override? → P12 in [survival-patterns.md](references/survival-patterns.md), anonymous subclass
10. **Check Headless** — TextField/Button/Frame? → read [awt-gui-testing.md](references/awt-gui-testing.md), verify in PIT minion
11. **Still surviving after exhausting ALL techniques?** → read [survival-patterns.md](references/survival-patterns.md) for force-equivalent analysis. MUST produce Iron Rule 9 table with WHY for EACH survivor BEFORE advancing.

**Action phase (write tests, then loop back):**
12. **Read the relevant reference file** for the pattern you matched (see file links in steps above)
13. **Apply Killing Rule** — write minimal incremental test; code examples in [killing-strategies.md](references/killing-strategies.md)
14. **Run `mvn test-compile`** — fix ALL errors before PIT (Iron Rule 7). For generic type mismatches, see [common-mistakes.md](references/common-mistakes.md).
15. **Run `mvn pitest:mutationCoverage`** — generate new report
16. **GOTO step 1** (Analysis phase) — check what's still alive, write more tests, repeat

**Advanced killing (when basic assertions fail):**
- Return-value ok but mutant survives? → read [test-patterns-catalog.md](references/test-patterns-catalog.md) Pattern 14 (Internal State Inspection)
- Unreachable branch? → P14 in [survival-patterns.md](references/survival-patterns.md) (Reflection Map State Injection)
- Compound while-loop removed conditional? → read [test-patterns-catalog.md](references/test-patterns-catalog.md) Pattern 15 (Backward Loop Multi-Iteration)
- Constructor boundary? → read [test-patterns-catalog.md](references/test-patterns-catalog.md) Pattern 18 (Precondition Manipulation)
- VOID_CALL on animation? → read [test-patterns-catalog.md](references/test-patterns-catalog.md) Pattern 16 (Counting Subclass)
- Tree structures? → read [bplustree-testing.md](references/bplustree-testing.md), escalate assertions to Level 4+

### PER-CLASS GATE — DO NOT SKIP. DO NOT ADVANCE WITH SURVIVORS.

```
┌────────────────────────────────────────────────────────────────────────┐
│  🔒 GATE CHECK for {CurrentClass}:                                     │
│                                                                        │
│  ☐ EVERY mutant is EITHER KILLED or TIMED_OUT?                         │
│    → ✅ ADVANCE to next class (clean kill — no equivalent report needed)│
│                                                                        │
│  ☐ Survivors remain — have ALL killing techniques been exhausted?      │
│    List what was tried:                                                │
│    ☐ Boundary value testing (exact threshold values)                   │
│    ☐ Reflection-based internal state inspection (Pattern 14)           │
│    ☐ Reflection Map/List state injection (Pattern 11)                  │
│    ☐ Counting subclass for void methods (Pattern 16)                   │
│    ☐ Multi-iteration loop trigger (Pattern 15)                         │
│    ☐ Anonymous subclass without override (Pattern 12)                  │
│    ☐ Setter decoupling for correlated values (Pattern 22)              │
│    ☐ Output capture via System.setOut (Pattern 2)                      │
│    ☐ Constructor argument field assertion (Pattern 17)                 │
│                                                                        │
│  ☐ Survivors NOT killable after exhausting ALL above?                  │
│    → MUST match each to a specific pattern (P1-P20) WITH proof         │
│    → MUST output Iron Rule 9 table with WHY for every survivor         │
│    → MUST explain: what was tried, why it failed, why it's proven eq. │
│    → Only THEN can you ✅ ADVANCE with documented equivalents           │
│                                                                        │
│  ☐ Any survivor WITHOUT a specific WHY?                                │
│    → ❌ NOT equivalent. GOTO Analysis phase step 1.                     │
│    Write more tests. Do NOT advance. Do NOT stop. Do NOT ask user.     │
│                                                                        │
│  ⛔ VIOLATION CHECK:                                                    │
│  ☐ Did you write tests for MULTIPLE classes without PIT between?      │
│    → ❌ VIOLATION of Iron Rule 6. Delete extra tests.                   │
│  ☐ Did you advance to the next class with undocumented survivors?      │
│    → ❌ VIOLATION of Rule 0. Go back. Fix it.                           │
│  ☐ Did you mark a mutant equivalent without explaining WHY?            │
│    → ❌ VIOLATION of Iron Rule 9. Write the proof or write more tests. │
└────────────────────────────────────────────────────────────────────────┘
```

**After gate passes:** Update class inventory (move 🔄), restart from Analysis step 1 for NEXT class.

**⛔ AFTER EVERY CLASS (gate pass = trigger): Execute Self-Optimization Steps 1-3 below IMMEDIATELY — before announcing the next class. Do NOT skip this. The skill must learn from each class.**

---

## Self-Optimization Hook

**This section is inline with the PER-CLASS GATE. After every class completes (gate passes), execute Steps 1-3 below BEFORE announcing the next class. After EVERY PROJECT completes (all classes done), execute the FULL AUDIT (Step 4) before declaring project finished.** The skill must learn from each project AND correct accumulated errors.

### Per-Class Self-Optimization (after EACH class gate passes)

#### Step 1: Post-Mortem (mental, no edits yet)

Identify what's NEW: new pattern? new project? correction to existing pattern? new test technique?

#### Step 2: Edit the RIGHT file (dispatch table)

| What's new | Edit THIS file | 
|-----------|---------------|
| New equivalent mutant pattern → Pattern N+1 | `references/survival-patterns.md` + SKILL.md Quick Reference row |
| New killing technique for a mutation operator | `references/killing-strategies.md` (add code example to operator section) |
| Existing pattern description wrong | `references/survival-patterns.md` (correct the pattern) |
| New test pattern invented | `references/test-patterns-catalog.md` (add pattern + code) |
| New project completed | `references/project-case-studies.md` (add case study) + `project-data.json` (add stats) |
| New common mistake found | `references/common-mistakes.md` (add row) |
| New B+Tree/tree testing rule discovered | `references/bplustree-testing.md` |
| New AWT/GUI testing rule discovered | `references/awt-gui-testing.md` |
| New PIT metric interpretation pattern | `references/pit-metrics.md` |
| No new knowledge (all survivors matched known patterns) | Only `project-data.json` (update stats) |

#### Step 3: Execute & Verify (checklist — run AFTER edits)

```
☐ 1. Post-mortem filled (mental or written) — what was learned this class?
☐ 2. All survivors matched to known patterns OR new patterns created
☐ 3. Equivalent mutants documented with proof (Iron Rule 9 format)
☐ 4. Dispatch table consulted → correct reference file(s) edited
☐ 5. If new pattern: also added 1 row to SKILL.md Quick Reference table
```

---

### ⛔ PROJECT-COMPLETION FULL AUDIT (after ALL classes done — MANDATORY)

**This is NOT optional. Before declaring a project finished, you MUST:**

```
┌──────────────────────────────────────────────────────────────────────────┐
│                    PROJECT-COMPLETION REFERENCE AUDIT                      │
│                                                                          │
│  For EACH reference file below, answer:                                   │
│  ☐ Is anything in this file WRONG based on what we learned this project? │
│  ☐ Is anything MISSING that this project revealed?                       │
│  ☐ Are cross-references between files still consistent?                  │
│  ☐ Are counts/stats in README + SKILL.md Overview still accurate?       │
│                                                                          │
│  AUDIT CHECKLIST (every file, every project completion):                 │
│                                                                          │
│  ☐ survival-patterns.md:                                                 │
│     - Any pattern description inaccurate? → CORRECT IT                    │
│     - Any pattern missing a newly discovered variant? → ADD variant       │
│     - Any pattern's "Action" field wrong or incomplete? → FIX IT         │
│     - Pattern count matches SKILL.md Quick Reference? → VERIFY           │
│                                                                          │
│  ☐ killing-strategies.md:                                                │
│     - Any operator strategy insufficient or wrong? → CORRECT IT          │
│     - Any code example that doesn't actually kill? → FIX OR REMOVE       │
│     - New killing sub-technique discovered? → ADD to operator section    │
│     - Quick-kill flowchart missing a branch? → ADD branch                │
│                                                                          │
│  ☐ test-patterns-catalog.md:                                             │
│     - Any pattern code has bugs or doesn't work? → FIX IT                │
│     - New pattern invented this project? → ADD pattern N+1              │
│     - Existing pattern missing a critical rule? → ADD rule              │
│     - Cross-refs to survival-patterns.md correct? → VERIFY               │
│                                                                          │
│  ☐ common-mistakes.md:                                                   │
│     - Any mistake we made this project not listed? → ADD row             │
│     - Any listed fix actually wrong? → CORRECT IT                        │
│     - Red flags checklist missing items? → ADD items                    │
│     - New anti-pattern discovered? → ADD with fix                       │
│                                                                          │
│  ☐ bplustree-testing.md (if tree project):                               │
│     - Any tree rule need refinement? → CORRECT                           │
│     - New assertion level or technique? → ADD                            │
│                                                                          │
│  ☐ awt-gui-testing.md (if GUI project):                                  │
│     - Any GUI pattern wrong? → CORRECT                                   │
│     - New headless workaround? → ADD                                     │
│                                                                          │
│  ☐ pit-metrics.md:                                                       │
│     - Diagnostic matrix still accurate? → CORRECT if needed              │
│     - Project comparison table up to date? → ADD new project row         │
│                                                                          │
│  ☐ SKILL.md:                                                             │
│     - Quick Reference table: all 20 patterns still correct? → FIX any    │
│     - Overview line: counts (projects, mutants, coverage) accurate?     │
│     - Launch Sequence: 5 rules still complete? → ADD if new rule needed │
│     - Iron Rules: any need refinement based on project experience?       │
│     - Reference Index: file descriptions still accurate?                 │
│                                                                          │
│  ☐ project-data.json:                                                    │
│     - Version bumped correctly?                                          │
│     - All stats recalculated (projects, mutants, killed, equivalents)?   │
│     - New project added to projects array?                               │
│     - Changelog entry accurate and complete?                             │
│                                                                          │
│  ☐ README.md:                                                            │
│     - "X 个项目" count accurate?                                          │
│     - "N 个已知存活模式" count accurate?                                   │
│     - "N 个测试模式" count accurate?                                       │
│     - "N 种真等价变异体" count accurate?                                   │
│     - Project data table: new project row added?                         │
│     - Any outdated claims? → CORRECT                                     │
│                                                                          │
│  ☐ CHANGELOG.md:                                                         │
│     - New version entry complete and accurate?                           │
│     - All reference file changes listed?                                 │
│     - Corrections mentioned, not just additions?                         │
│                                                                          │
│  ☐ self-optimization.md:                                                 │
│     - This audit procedure itself need refinement? → UPDATE              │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

**⛔ CRITICAL: "Nothing to fix" is a VALID answer for each file — but only after you have actually READ and VERIFIED each file. Skipping a file because "it's probably fine" = VIOLATION.**

#### Step 4: Consolidate & Version

```
☐ 1. All reference files audited (NOT just the one with new knowledge)
☐ 2. Corrections made to any inaccurate descriptions, examples, or rules
☐ 3. Missing knowledge added to ALL relevant files (not just one)
☐ 4. Cross-references between files verified consistent
☐ 5. CHANGELOG.md lists BOTH additions AND corrections
☐ 6. project-data.json: stats recalculated, version bumped, timestamp updated
☐ 7. README.md: all counters + project table updated
☐ 8. SKILL.md Overview line recalculated
☐ 9. Version bump applied per rules below
☐ 10. Self-opt summary line: "Audited {N} reference files: {X} corrected, {Y} augmented, {Z} unchanged"
```

### Version Bump Rules

| Delta | Bump | Example |
|-------|------|---------|
| Stats only (no new patterns) | PATCH | v2.4.1 → v2.4.2 |
| New pattern / test pattern / project | MINOR | v2.4.9 → v2.5.0 |
| Multiple MINOR changes at once | MINOR (once) | |
| Breaking restructure | MAJOR | v2.9.0 → v3.0.0 |

**Same calendar day = ONE version bump.** Add knowledge, don't duplicate it. Full details in [self-optimization.md](references/self-optimization.md).

---

## 📚 Reference Index — When to Read Which File

> **This is the routing table. Read the relevant file when the situation matches. Do NOT read all files at once.**

| Situation | File | What's Inside |
|-----------|------|---------------|
| Survivor matched a pattern (P1-P20), need details | [survival-patterns.md](references/survival-patterns.md) | 20 patterns: symptom, root cause, code example, action |
| Need operator-specific killing code | [killing-strategies.md](references/killing-strategies.md) | 11 operators with code + quick-kill decision tree |
| Need a specific test technique (reflection, counting subclass, etc.) | [test-patterns-catalog.md](references/test-patterns-catalog.md) | 23 reusable test patterns with code |
| Working on B+Tree, binary tree, or recursive data structure | [bplustree-testing.md](references/bplustree-testing.md) | t-value selection, assertion escalation ladder, incremental building |
| Working on AWT/Swing/GUI class | [awt-gui-testing.md](references/awt-gui-testing.md) | Headless compatibility, Graphics mock chaining, GUI subclass pattern |
| Want to sanity-check your tests | [common-mistakes.md](references/common-mistakes.md) | 40+ common mistakes + 30+ red flags checklist |
| Need to interpret PIT report metrics | [pit-metrics.md](references/pit-metrics.md) | Coverage statistics, diagnostic matrix, 22-project comparison table |
| Want to learn from similar past projects | [project-case-studies.md](references/project-case-studies.md) | 22 project deep-dives: strategies, equivalent mutants, lessons |
| Need canonical operator/pattern/project data | [project-data.json](./project-data.json) | Structured JSON: 16 operators, 20 patterns, 22 projects |

### Typical Read Sequence During a PIT Session

```
1. First PIT report arrives
   → Read Quick Reference table (above) to match survivors
2. Need to write killing test
   → Read killing-strategies.md for operator-specific code
3. Pattern matched (e.g., P14 Reflection Map Injection)
   → Read survival-patterns.md for detailed how-to
4. Need the actual test pattern code
   → Read test-patterns-catalog.md for the specific pattern
5. Special domain (B+Tree / GUI / Wrapper project)
   → Read bplustree-testing.md OR awt-gui-testing.md OR project-case-studies.md
6. After PIT completes for a class
   → Execute Self-Optimization Hook above (Steps 1-4)
```
