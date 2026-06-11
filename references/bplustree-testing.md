# B+Tree & Recursive Data Structure Testing Rules

## Rule 1: t-Value Selection for Internal Node Coverage

B+Trees have a parameter `t` (minimum degree). Internal nodes can hold `t-1` keys and `t` children. Leaf nodes hold `t-1` keys.

- **t=2**: Minimum practical value. Leaf capacity=1, internal node capacity=1 key. Triggers splits fastest but may hit algorithmic edge cases (empty internal nodes after split propagation).
- **t=3**: Sweet spot for testing. Leaf capacity=2, internal node capacity=2 keys. Splits happen after 2-3 inserts. Deep tree structure emerges quickly.
- **t=4**: Stable testing. Leaf capacity=3. More inserts needed for splits but less prone to edge cases.
- **t>=5**: Good for basic insert/search tests without triggering splits.

**Strategy:** Use multiple t-values across test scenarios:
- t=3 for split-triggering and internal node creation
- t=4 for deeper tree structure and multi-level order() testing
- t=5 for basic insert/search/getSize tests

## Rule 2: Sequential vs Random Insertion Order

For B+Tree mutation testing, **sequential insertion** (1,2,3,...,N or pre-sorted order) is preferred over random insertion because:
1. Sequential produces deterministic, predictable tree structures
2. Random can cause pathological splits that are hard to reproduce
3. Sequential ensures even distribution across leaves
4. Predictable structure enables precise assertions on order(), inOrder(), reverseInOrder()

## Rule 3: Incremental Tree Building

Build tree complexity incrementally within a single test:
```java
// Phase 1: Basic leaf operations (no split)
tree.insert(50, "a");
tree.insert(30, "b");  // still in same leaf

// Phase 2: Trigger first leaf split -> creates InternalNode root
tree.insert(70, "c");  // split with t=3

// Phase 3: Populate second level
tree.insert(10, "d");
tree.insert(90, "e");

// Phase 4: Trigger internal node split (hardest to cover)
// ... more inserts ...
```
Each phase exercises different code paths. Assert tree state after each phase.

## Rule 4: Assertion Escalation Ladder for Tree Tests

When writing assertions for tree structure tests, escalate through these levels:

1. **Exists**: `assertNotNull(result)` — weakest, kills NULL_RETURNS only
2. **Count**: `assertEquals(expected, tree.getSize())` — kills basic MATH on size
3. **Search**: `assertEquals(expectedValue, tree.search(key))` — kills getValue internals
4. **Order**: `assertEquals(expected, tree.order(key))` — kills order() recursion
5. **Split structure**: `assertEquals(expectedKey, result.getSplitRootKey())` — kills split mid calculation
6. **Internal state**: `assertEquals(expectedSize, ((InternalNode)root).getNodeSize())` — strongest

**Always escalate to at least Level 4 for split-triggering tests.** Weak assertions (Level 1-2) leave MATH on `mid`, `mid+1`, `keys.size()+1`, and `t%2` mutations alive.
