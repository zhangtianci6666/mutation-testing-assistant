# Common Mistakes & Red Flags

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Analyzing source code or designing tests BEFORE running PIT | **Run PIT first, always.** Data drives decisions; intuition wastes time |
| Guessing a mutant is equivalent without exhausting test techniques | **Assume killable until proven equivalent.** Exhaust all techniques before declaring equivalent |
| Assuming test construction implies target path coverage | **Verify with internal state assertions.** Assert `node.numElements`, `node.next`, or `elements` |
| `assertTrue(result > 0)` | Use `assertEquals(expected, result)` |
| Testing math with 0 or 1 as operands | Use asymmetric values like `7 + 8` |
| Only testing around boundary | Test exact boundary value |
| No verification after void call | Assert state change or use Mockito verify |
| `assertNotNull(result)` only | Also assert specific expected value |
| Missing `try-finally` around `System.setOut` | Always restore original stream in finally block |
| Hard-coding `\n` in output capture assertions | Use `.trim()` or platform-agnostic checks |
| Testing only `currentPos=1` for array index `idx-1` | Sweep all valid indices; at least one will kill `+`/`*`/`/` mutants |
| Ignoring dominated conditions in `else if` | Analyze reachability: if earlier condition implies the later, boundary mutant may be equivalent |
| Testing `!condition` with only true-branch | Must test BOTH true and false outcomes of the negated expression |
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
| **Writing weak assertions when one strong assertion kills multiple mutants** | **One `assertEquals(expected, obj.field)` kills both MATH and RETURN_VALS** |
| **Assuming package-private fields require reflection** | **If test class is in the same package as the class under test, direct field access works** |
| **Misinterpreting low Test Strength as "need more tests"** | **Low Test Strength + high Line Coverage = assertions are too weak, not missing branches** |
| **Running PIT with compilation errors in test code** | **Run `mvn test` first; fix ALL compilation errors before PIT. Generic type mismatches are the #1 culprit** |
| **Treating TIMED_OUT as a problem to fix** | **TIMED_OUT = killed. The mutation caused infinite loop. Document and move on. Pattern 13** |
| **Trying to cover base class method via existing subclasses that all override it** | **Create anonymous subclass WITHOUT overriding the target method. Pattern 12** |
| **Forgetting to call normal initialization before reflection-based state injection** | **Always call parse()/constructor first to set up object, THEN inject edge-case state via reflection. Pattern 14** |
| **Missing coverage in `if (list.isEmpty())` branch that normal API never creates** | **Use reflection to inject empty list into internal Map/Collection. Pattern 14** |
| **Testing tree split with only `assertNotNull(result.getSplitRootKey())`** | **Assert EXACT splitRootKey value, EXACT left/right node sizes. Escalate to Level 4+** |
| **Using `assertTrue(result > 0)` for minGap/order/size in trees** | **Use `assertEquals(expected, result)` with exact computed value** |
| **Testing B+Tree with only one t-value** | **Use multiple t-values: t=3 for rapid splits, t=4 for deeper structure, t=5 for basic operations** |
| **Not capturing stdout for bloom filter / conditional print paths** | **Use `System.setOut` capture to verify println IS called for filter-blocked search paths** |
| **Assuming all private method MATH mutations are killable via public API** | **Check if method is called by both write and read paths -> self-consistent -> need reflection** |
| **Spending time on `new ArrayList<>(expr)` constructor MATH mutants** | **These are equivalent mutants (Pattern 15). Initial capacity is a performance hint** |
| **Writing one giant @Test that tries to cover all tree states at once** | **Build tree incrementally: Phase 1->Phase 2->Phase 3->Phase 4. Assert after each phase** |
| **Declaring variable as concrete subtype from generic-returning convenience method** | **Use `Option<T>` not `Option.StringOption` when assigning from `addStringOption()`** |
| **Trying to kill VOID_METHOD_CALL on library internal objects in wrapper projects** | **Recognize as Pattern 20 (Wrapper VOID Equivalence). Coverage ceiling ~65-75%** |
| **Trying to kill MATH/BOUNDARY on variables reset by cleanup/init method at end of public method** | **Recognize as Pattern 5 (Dead Store). Check for initate()/reset()/clear() calls at end of method — they make ALL intermediate state mutations unobservable** |
| **Testing instanceof checks without assertSame** | **Use `assertSame(original, result)` to kill REMOVE_CONDITIONALS on `instanceof` checks** |
| **Not distinguishing wrapper null checks from leaf null checks** | **Wrapper overloads delegate to a "full" overload. Only test null on the leaf method** |
| **Assuming all project types have the same coverage ceiling** | **Wrapper: ~65-75%, Algorithmic: ~85-95%, GUI: ~25-60%** |
| **Killing mutants via reflection tests that later "resurrect" as SURVIVED** | **PIT coverage tracking through `Method.invoke()` is UNRELIABLE. Mutants killed by reflection tests may survive in later runs. Replace with public API path tests whenever possible. For package-private methods in same package, call directly without reflection** |
| **Using reflection to test private methods and expecting stable PIT coverage** | **Reflection bypasses PIT's bytecode instrumentation for individual lines inside the reflected method. PIT may not select the test for specific mutations. Prefer: 1) public API path, 2) package-private direct access, 3) reflection as last resort** |

---

## Red Flags - Check Your Tests

- Using `assertTrue` with inequalities instead of `assertEquals`
- Testing math with 0 or 1 as operands
- Testing boundaries with `threshold +/- 1` but not `threshold`
- Void methods with no assertions after call
- Only one branch of if/else covered
- `System.setOut` without `try-finally` restoration
- Array index math (`idx - 1`) tested with only one index
- `!condition` tested with only one boolean outcome
- Survived `CONDITIONALS_BOUNDARY` in `else if` not analyzed for dominance
- Constructor validation masking boundary states not bypassed with reflection
- Survived mutants on traversal direction conditions not analyzed for path convergence
- Survived mutants on compound while-conditions not tested with multi-iteration triggers
- Declaring a mutant equivalent without exhausting all techniques
- Writing a test for merge/cross-node/branch without asserting internal state
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
- **Declaring test variables as concrete inner types from generic-returning convenience methods**
- **Assuming base class method coverage will come from testing existing subclasses**
- **Panicking at TIMED_OUT results — TIMED_OUT = killed (Pattern 13)**
- **Injecting internal state via reflection without first calling normal initialization**
- **Relying on reflection-called methods for PIT coverage stability** | **Prefer public API paths over `Method.invoke()`. PIT may not track coverage through reflection reliably — mutants killed via reflection tests can resurrect as SURVIVED in later runs**
- **Preferring reflection over public API for testing private methods** | **Try public API first, package-private direct access second, reflection last. Reflection-bypassed methods may have coverage gaps**
- **Maven using wrong source level (e.g. -source 8) despite pom.xml specifying Java 21** | **Pass `-Dmaven.compiler.source=21 -Dmaven.compiler.target=21` explicitly. Some Windows + Maven 3.9.x configurations ignore pom.xml properties. Check with `mvn -version` first**
- **Calling instance methods from Java Record compact constructor** | **Record fields are assigned AFTER the compact constructor completes. Calling `this.crossesMidnight()` which accesses `this.end` will NPE because `end` is still null. Workaround: inline the check in the compact constructor, or skip testing that path (Iron Rule 8)**
- **Writing huge test factories with too many required parameters** | **Task constructor needed `startedAt`+`completedAt` for specific statuses. Missing these caused `IllegalArgumentException` not test-logic failures. Always read record/constructor validation rules before writing factory methods**
- **PIT compiled with test-compile but using wrong Java source level** | **PIT uses its own compiler. If Maven test-compile requires `-Dmaven.compiler.source=21`, PIT also needs these flags. Compile failure = 0 mutants analyzed**
- **Using `assertThrows(NullPointerException.class)` when source throws `IllegalArgumentException` for null** | **Java Records' compact constructor wraps null checks in `requireText` which throws `IllegalArgumentException`, not `NullPointerException`. Read the source, not your assumptions**
- **Calling `Mockito.when()` on a real (non-mock) object** | **`when(new PricePolicy().normalizePrice(any()))` silently returns `null`/default at runtime instead of the expected value, causing confusing downstream failures. Always use `mock(PricePolicy.class)` before calling `when()`**
- **Using `List.of()` / `Set.of()` without explicit type witness causing constructor parameter mismatch** | **`Set.of()` without `<String>` yields `Set<Object>`, shifting subsequent parameters. Use `Set.<String>of()` or pre-declare typed variables. This is #1 cause of "constructor is undefined" errors in record instantiation**
- **Using `sed -i` or regex replacements to batch-edit Java source files** | **Can silently corrupt method boundaries, delete closing braces, or shift annotations. Always use the Edit tool for targeted replacements, or delete/re-add methods via Read+Edit. A single mangled `}` can cause dozens of cascading compilation errors**
- **Using `BigDecimal.ZERO` with `assertEquals(expected, actual)` without matching scale** | **`BigDecimal.ZERO` has scale 1; `money()` returns scale 2. `assertEquals(BigDecimal.ZERO, result.fee())` fails because `0 != 0.00`. Use `assertEquals(new BigDecimal("0.00"), result.fee())` or `assertTrue(result.fee().compareTo(BigDecimal.ZERO) == 0)`**
- **Setting `List.of((SomeType) null)` to test null element validation** | **`List.copyOf()` used in record compact constructors rejects null elements. The NPE occurs in the record constructor, not in the validation method. Use `new ArrayList<>()` + `add(null)` if you need a null-containing list, but be aware record constructors will still reject it**
- **Forgetting `mvn clean` after major test file edits** | **Maven's incremental compiler may not detect changes in large files after repeated edits. If `mvn test-compile` says "Nothing to compile" but you edited the file, run `mvn clean test-compile`**
