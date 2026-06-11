# Test Patterns Catalog (从22个项目提取)

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

