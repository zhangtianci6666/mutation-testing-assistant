# Test Patterns Catalog (从24个项目提取)

22 reusable test patterns for killing specific mutation types. Each pattern includes source project, use case, and code example.

---

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
public void setUp() { System.setOut(new PrintStream(outContent)); }

@AfterEach
public void tearDown() { System.setOut(originalOut); }

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
    List<Class<? extends Mode>> modes = Arrays.asList(ModeA.class, ModeB.class, ModeC.class);
    for (Class<? extends Mode> modeClass : modes) {
        Mode mode = modeClass.getDeclaredConstructor().newInstance();
        mode.setKey(new byte[16]); mode.setIV(new byte[16]); mode.setup();
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
    assertFalse(validator.isValid("123456789012345"));   // 15位 — 低于边界
    assertTrue(validator.isValid("1234567890123456"));    // 16位 — 边界
    assertTrue(validator.isValid("12345678901234567"));   // 17位 — 高于边界
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
    list.add("B");
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
    String result = tree.getPreorderList().toString();
    assertTrue(result.contains("wt: 6.0"));
    assertTrue(result.contains("[1 1] wt: 1.0"));
}
```

### 9. 加密-解密循环验证
**来源项目:** Square (密码学算法)
**用途:** 加密算法测试，验证加密解密配对
```java
@Test
public void testEncryptDecryptCycle() {
    byte[] key = new byte[16];
    byte[] plaintext = "plaintext".getBytes();
    byte[] encrypted = Square.encrypt(plaintext, key);
    byte[] decrypted = Square.decrypt(encrypted, key);
    assertArrayEquals(plaintext, decrypted);
    assertFalse(Arrays.equals(plaintext, encrypted));
}
```

### 10. JUnit 5 assertThrows 异常断言
**来源项目:** UnrolledLinkedList2023, Square
**用途:** 使用 JUnit 5 内置 assertThrows 简化异常测试
```java
@Test
public void testOutOfBounds() {
    UnrolledLinkedList list = new UnrolledLinkedList();
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
    for (int i = 0; i < 9; i++) list.add(i);
    list.add(4, 40);
    assertEquals(4, list.firstNode.numElements);
    assertEquals(6, list.lastNode.numElements);
}
```
**关键规则:** 优先检查 `numElements`、`next`、`previous`、`elements` 等 package-private 字段。

### 15. 后向循环多迭代触发（Backward Loop Multi-Iteration Trigger）
**来源项目:** UnrolledLinkedList2023
**用途:** 杀死 `while ((p -= node.numElements) > index)` 的 removed conditional 变异体
```java
@Test
public void testBackwardLoopMultiIteration() {
    UnrolledLinkedList<Integer> list = new UnrolledLinkedList<>(8);
    for (int i = 0; i < 18; i++) list.add(i);
    // index=10：后向遍历需要执行一次循环体（lastNode→thirdNode）
    assertEquals(10, list.set(10, 99));
}
```
**关键规则:** 对于包含副作用的复合条件 `while ((p -= expr) > idx)`，必须使用使循环体至少执行一次的索引。

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
- 断言 **精确次数**，不是 `> 0`
- **必须在阅读源码后计算精确次数**，不要估算
- 对于 `super.redraw()` 内部调用 `repaint()` 和 `delay()`，确保 CountingDP 也覆盖了这两个方法

### 17. 构造函数参数 MATH 杀活（Constructor Argument Math Kill）
**来源项目:** P_Queue (Heap.addInput)
**用途:** 当 MATH 突变发生在传给构造函数的参数表达式上时，断言被构造对象的内部字段
```java
@Test
public void testAddInputRunningComCoords() {
    ch.addInput(99);
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
    boundHeap.posnList = new Vector();
    for (int i = 0; i < 3; i++) {
        Node n = new Node(-1); n.x = 0; n.y = 0;
        boundHeap.posnList.addElement(n);
    }
    boundHeap.setHeap(new int[]{1, 2, 3});
    assertEquals(0, ((Node) boundHeap.nodeList.elementAt(0)).x);
}
```
**关键规则:** 通过反射或直接字段赋值设置前置状态，使边界突变产生可观测差异。

### 19. 子类部分模拟（Partial Mock via Subclass）
**来源项目:** P_Queue (DrawingPanel.java, Heap.java)
**用途:** 当 Mockito 的 `spy()` 或 `partialMock` 因字节码操作或构造器复杂性而失败时，用手写子类覆盖特定方法
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
- 适用于无法使用 Mockito `spy()` 的场景：构造器调用 `new Thread()`、`System.loadLibrary()`、或 native 方法

### 20. 同包测试前提声明（Package-Private Access Precondition）
**来源项目:** P_Queue (Heap.java, DrawingPanel.java, ComBox.java)
**用途:** 内部状态探查 (Pattern 14) 和前置条件操纵 (Pattern 18) 的前提
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
**关键规则:** 优先使用同包直接访问；如果测试类被迫位于不同包，必须使用反射（参见 Pattern 11）。

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
        pw.println("/*-------"); pw.println("int a = 1;"); pw.println("//-");
    }
    TextFrame tf2 = new TextFrame(temp.toURI().toURL(), "tframe.txt");
    assertEquals(1, tf2.n_lines);
    assertEquals("int a = 1;", tf2.lines[0]);
}
```
**关键规则:** 临时文件写入 `target/test-classes/` 确保 Maven 清理时删除。

---

### 22. Setter去耦构造器关联值（Setter Decoupling for Constructor-Correlated Values）
**来源项目:** Hotel (Hotel.java addRoom + getValue)
**用途:** 当工厂方法/构造器自动关联计算多个字段值时，用setter覆写去耦，使MATH变异体可被单独击杀
**场景:** `addRoom(type, code, capacity)` 自动设置 `price = f(type, capacity)`。`getValue()` 中 `type*1e6` 与 `price*1000` 共变，MATH 变异 `*1e6→/1e6=0` 被 price 差异补偿而存活。
```java
// 去耦：用setPrice()使所有房间价格相等 → type的MATH成为唯一区分因子
Hotel.rooms.get(0).setPrice(100.0);
Hotel.rooms.get(1).setPrice(100.0);
// 再用roomCode逆向验证顺序反转
// Advanced(210,price=100) vs Standard(211,price=100):
//   Original: type*1e6 → Advanced(3M+210) > Standard(1M+211) ✓
//   Mutated(type→0): Standard(211) > Advanced(210) → 反转 → KILLED!
```
**关键规则:**
1. 识别工厂方法中自动关联的字段组
2. 用setter逐一覆写到相同值，消除共变补偿
3. 利用非关联字段(如ID/roomCode)的差值来验证排序反转

---

### 23. 公共API优先于反射（Public API Over Reflection）
**来源项目:** LunarCalendar
**用途:** 当反射调用的方法杀死变异体后，在下一次 PIT 运行中这些变异体可能"复活"——PIT 的字节码插桩无法可靠追踪通过 `Method.invoke()` 覆盖的代码行。应优先使用公共 API 路径。
```java
// ❌ 不好 — 反射杀死的变异体可能复活
@Test
public void testViaReflection() throws Exception {
    Method m = DPCManager.class.getDeclaredMethod("buildDPInfo");
    m.setAccessible(true);
    m.invoke(manager); // 杀死的 VOID_METHOD_CALL 变异体可能在其他 PIT 运行中显示为 SURVIVED
}

// ✅ 好 — 公共 API 路径，PIT 可稳定追踪
@Test
public void testViaPublicAPI() {
    DPCManager manager = DPCManager.getInstance();
    LunarCalendar calendar = manager.obtainDPInfo(year); // 公共 API 调用相同内部路径
    assertNotNull(calendar);
    // PIT 稳定杀死 VOID_METHOD_CALL
}
```
**关键规则:**
1. 优先公共 API 路径 → 2) 同包 package-private 直接访问 → 3) 反射作为最后手段
2. 如果反射是唯一选择，接受 PIT 报告可能因运行而异
3. 对静态内部方法，如果测试类与被测类同包，直接调用 package-private 方法而非反射

---

### Pattern 24: Single-File Aggregation with @Nested Classes

**适用场景:** 用户要求在单个测试文件中聚合所有业务类的变异测试，禁止拆分多文件。

**代码示例:**
```java
class MutationTest {
    @Nested @DisplayName("TaskPolicy") class TaskPolicyTests { /* ~50 tests */ }
    @Nested @DisplayName("TaskStateMachine") class TaskStateMachineTests { /* ~20 tests */ }
    @Nested @DisplayName("AttendancePolicy") class AttendancePolicyTests { /* ~30 tests */ }
    // ... 10+ more @Nested classes for all business classes
}
```

**关键规则:**
1. 使用 `@Nested` + `@DisplayName` 组织每个业务类的测试
2. 在顶层类中定义共享工厂方法（private static helpers）
3. 使用完全限定类名避免 import 冲突和编译问题
4. 每个 `@Nested` 类可拥有自己的 `@BeforeEach`/helper 方法
5. 保持所有测试在单个 `.java` 文件中 — 禁止创建额外测试文件

**适用于:** 需要单文件交付的考试/比赛项目。

---

### Pattern 25: JaCoCo + PIT Dual Coverage Analysis

**适用场景:** 需要同时达成行/分支/方法覆盖率（JaCoCo）和变异覆盖率（PIT）目标。

**分析流程:**
1. **先 PIT** → 识别存活变异体 → 杀死 → 循环直到瓶颈
2. **同时 JaCoCo** → 读取 `.java.html` 源级报告 → 精确找到未覆盖的 RED（行）和 YELLOW（分支）
3. **JaCoCo 用于行/分支**: 所有红色行 = 需要测试；黄色行 = 部分分支未覆盖
4. **PIT 用于变异**: SURVIVED = 测试不够强；NO_COVERAGE = 行未覆盖

**互补性:**
| 维度 | JaCoCo | PIT |
|-----|--------|-----|
| 行覆盖 | ✅ 精确 | 近似 |
| 分支覆盖 | ✅ 每个分支 | ❌ |
| 方法覆盖 | ✅ | ❌ |
| 测试质量 | ❌ | ✅ |
| 等价体检测 | ❌ | ✅ |

**关键规则:**
1. 先达成 JaCoCo 100% 方法/类覆盖（快速胜利）
2. 再追求分支覆盖 → 读 `.java.html` 找到每个黄色行
3. 最后用 PIT 杀死剩余变异体
4. `mvn test` 后 JaCoCo 报告在 `target/site/jacoco/index.html`


---

### Pattern 26: 黄金序列 + 位布局反射（PRNG / ID 生成器）

**适用场景:** xorshift / LCG 伪随机、`System.nanoTime() ^ (millis << k)` 这类混合位运算的 ID 生成器。`MATH`（移位方向、加减乘除）变异体在“取值范围合法”“唯一性”这类弱断言下全部存活。

**失效的弱断言:** `assertTrue(v >= 0 && v < 1)`、`assertTrue(id > 0)`、`ids.add(id)` —— 移位方向反了仍然满足。

**两级杀法:**

1. **黄金序列**（PRNG）：固定种子必然产生确定序列，用真实实现的输出作为黄金值，逐位精确比较（delta = 0.0）。
```java
RiskAnalyzer a = new RiskAnalyzer();          // seed = 2463534242
assertEquals(0.9372512804277798, a.rnd(), 0.0);
assertEquals(0.5291417429544768, a.rnd(), 0.0);
```
   一处黄金值同时杀死 `<<`→`>>`、`>>>`→`<<` 等所有移位变异体。

2. **位布局反射**（ID 生成器）：读私有计数器字段，再在“毫秒不变”的窗口内反算期望值。
```java
Field f = IdGenerator.class.getDeclaredField("COUNTER");
f.setAccessible(true);
AtomicLong counter = (AtomicLong) f.get(null);
for (int i = 0; i < 20; i++) {
    long before = System.currentTimeMillis();
    long id = IdGenerator.nextId();
    long after = System.currentTimeMillis();
    if (before == after) {                    // 毫秒稳定才断言，避免抖动
        assertEquals((before << 20) ^ counter.get(), id);
        break;
    }
}
```

**关键规则:**
1. 黄金值必须由**真实实现**产出（跑一次打印），不要手推；Python 复现的浮点末位可能差 1 ULP（`0.012847983763020765` vs `0.01284798376302076`），以 JVM 输出为准。
2. 时间相关表达式必须用 `before == after` 的稳定窗口保护，否则是偶发失败的测试。
3. 若某位分支（如 `if (id < 0) id = -id;`）在数学上永不可达（两个操作数第 63 位恒为 0），该分支的所有变异体等价，不要试图构造。

---

### Pattern 27: 异常消息区分（捕获兜底掩盖变异）

**适用场景:** 入参校验 `if (s == null || s.isEmpty()) throw new DomainException("id string invalid");` 外面套了 `catch (NumberFormatException e) { throw new DomainException("id parse failed", e); }`。

**症状:** `REMOVE_CONDITIONALS` 把整条 `if` 变成 `if (false)`，`null` 继续流入 `Long.parseUnsignedLong(null)` → `NumberFormatException` → 被 catch 包成**同一个** `DomainException`。`assertThrows(DomainException.class, ...)` 依然通过，变异体存活。

**杀法:** 断言异常消息，而不是只断言异常类型。
```java
DomainException nullEx = assertThrows(DomainException.class, () -> IdGenerator.fromString(null));
assertEquals("id string invalid", nullEx.getMessage());   // 变异体抛出 "id parse failed"
DomainException zeroEx = assertThrows(DomainException.class, () -> IdGenerator.fromString("0"));
assertEquals("id zero invalid", zeroEx.getMessage());
```

**关键规则:**
1. 只要源码存在“统一异常出口”（catch 后重新包装、统一 `IllegalArgumentException` 工厂），异常**类型**就不再具备区分力，必须升级到消息/`getCause()`。
2. 反过来，先确认哪条路径抛哪个消息，再写断言；断言错消息会误判。

---

### Pattern 28: 边界等价体的三类逃生口（±0.0 / 隐藏状态 / 容器身份）

**适用场景:** 面对 `CONDITIONALS_BOUNDARY` 存活体，准备写“等价”之前。实测经验：30 个存活里 6 个（20%）是能杀的，判错的代价是永久损失分数。

**逃生口① ±0.0 符号位**

`assertEquals(double, double, delta)` 与 `==` 都把 `-0.0` 和 `+0.0` 视为相等，所以常规断言看不见差异；但 `Double.doubleToRawLongBits` 可以。

```java
@Test
public void budgetItemKeepsNegativeZeroCost() {
    Budget.Item item = new Budget.Item("zero", -0.0, -0.0, "c");
    // -0.0 不满足 cost < 0，钳制不应改写符号位
    assertEquals(Double.doubleToRawLongBits(-0.0), Double.doubleToRawLongBits(item.getCost()));
    assertEquals(Double.doubleToRawLongBits(-0.0), Double.doubleToRawLongBits(item.getValue()));
}
```
一处断言可同时击杀同一表达式里的多个边界变异体（本例 L14 与 L15）。

**逃生口② 隐藏状态破坏不变量**

守卫后面还有第二个归一动作时，去找**能让不变量本来就已越界**的入口。典型是构造器不做上限校验、而方法里又做上限归一。

```java
@Test
public void researcherReleaseNonPositiveDoesNotNormaliseOversizedCapacity() {
    Researcher r = new Researcher("big", 100);   // 构造器允许 100，超过 40 上限
    assertEquals(100, r.getCapacity());
    r.releaseHours(0);                            // 非正数必须直接返回
    assertEquals(100, r.getCapacity());           // 变异体会 +=0 后被归一成 40
}
```

**逃生口③ 容器可变性 / 实例身份（EMPTY_RETURNS 专用）**

`return res;`（刚 new 的空集合）被换成 `Collections.emptyList()` 时，内容永远相同，但**可变性和实例身份**不同。

```java
@Test
public void matchingEmptyResultIsWritableList() {
    List<MatchingEngine.Assignment> empty = engine.match(null, new ArrayList<>());
    assertTrue(empty.isEmpty());
    empty.add(new MatchingEngine.Assignment(new Task("t", 1, Medium), null, 0.0));
    assertEquals(1, empty.size());   // 变异体抛 UnsupportedOperationException
}
```

**关键规则:**
1. 判等价前**先跑判定流程**，不要凭“数值相等”下结论。
2. 逃生口①只对 `double/float` 且有 `< 0` / `<= 0` 的条件成立；整数域（`long`/`int`）没有负零，`id == 0` 处 `-0 == 0` 是真等价。
3. 逃生口②要找“**写入该字段的所有入口**”，grep 字段名，确认有没有绕过归一化的一条。
4. 逃生口③会断言返回容器的可变性——属于实现细节，需在注释里说明动机；若团队禁止此类断言，则如实记录为等价。
5. 这三类都不成立时，等价证明写成三句话：“边界值映射到自身 + 无越界入口 + 结果不进入对符号零敏感的算术”。

---

### Pattern 29: Utility Class Instantiation（纯静态工具类的隐式构造器覆盖）

**场景:** JaCoCo 行覆盖率卡在 99%，缺的那几行全是 `public class XxxParser {`、`public class XxxChecker {` 这类**类声明行**，而类里所有静态方法都已被测试调用。

**根因:** 只含静态方法的工具类没有显式构造器，javac 会合成一个与类同访问级的无参构造器。JaCoCo 把这个隐式构造器的字节码**归到类声明行**上；只要从未 `new` 过，该行就永远是 `mi>0`。这不是测试没走到方法体，而是「构造器从未执行」。

**识别:** 打开 `jacoco.xml`，找 `mi>0` 且 `nr` 等于类声明行的条目；对照源文件确认该类只有静态成员。

```java
@Test
void utilityClassDefaultConstructors() {
    assertNotNull(new CreditCardParser());   // public class，隐式 public 无参构造
    assertNotNull(new DateParser());
    assertNotNull(new DateChecker());
    assertNotNull(new DateFormatter());      // 包级私有类 → 包内测试可直接 new
    assertNotNull(new TypeChecker());
}
```

**规则:**
1. 一个断言一行，全部写在同一个测试里即可；不要为每个工具类单开测试方法（噪音）。
2. 包级私有类在同包测试里可直接实例化，不需要反射。
3. 若类被显式声明为 `private Xxx() {}`（禁止实例化的工具类），那行本来就不会被计数，不要去“强行 new”。
4. 先确认 `mi>0` 的行确实是类声明行再动手——有些“类声明行未覆盖”是真·构造器里有逻辑。

---

### Pattern 30: Counterfactual Probe（对照实验取证等价变异体）

**场景:** 一批存活变异体都指向同一段代码，你已给出等价性证明，但需要**可复现的实验证据**说服他人（评审、队友、自己复核）。

**做法:** 在**临时副本**里只修掉疑似源码缺陷，源码其余一字不动，用**完全相同**的测试再跑一次 PIT。

```bash
cp -r src pom.xml /tmp/probe/          # 绝不改交付目录
cd /tmp/probe
python - <<'PY'                        # 只改那一处：复制的循环区间
import io; p='src/main/java/.../VerveValidator.java'
s=io.open(p,encoding='utf-8').read()
s=s.replace('for (int i = IINRange[0]; i <= IINRange[1]; i++) {\n                if (IIN == i) {',
            'for (int i = IINRange[2]; i <= IINRange[3]; i++) {\n                if (IIN == i) {')
io.open(p,'w',encoding='utf-8').write(s)
PY
mvn -o pitest:mutationCoverage -DoutputFormats=XML
```

**判读:**
- 修完存活体**成批死亡** → 等价性源于源码缺陷（重复区间 / 死数据 / 不可达分支），不是测试不足。把“修 4 个字符从 96% 跳到 99%”写进报告，比十段逻辑证明更有力。
- 修完**照样存活** → 你的等价判断可能错了，回去补测试。

**规则:**
1. 副本必须放在项目外（`/tmp`、`%TEMP%`），跑完即删；交付目录的源码时间戳不能变。
2. 只改“证明所需的最小一处”，不要顺手重构，否则实验不再单变量。
3. 实验结论要写成「现状 X% → 修复后 Y%」的对照表，并说明这属于**上报源码缺陷**，不是改源码交付。
