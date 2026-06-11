# Project Case Studies (23个项目实战经验)

## 高覆盖率项目 (85%+)

### LunarCalendar (527 mutants, 90% killed, 546/552 lines, 99%)

农历日历库。8个类：Festivals/Gregorian/Lunar(数据)、TextUtils/LunarCalendar(业务)、SolarTerm(天文算法)、DPCNCalendar/DPCManager(日历转换)。

**关键发现：**
1. **PIT 反射覆盖不稳定**: 用 `Method.invoke()` 杀死的 VOID_METHOD_CALL 在后续 PIT 运行中会复活。解决方案：改走 public API 路径 (`DPCManager.getInstance().obtainDPInfo()`) 而非反射调用 `buildDPInfo`。
2. **多t值精确断言**: SolarTerm 天文公式中 `+→-` / `*→/` 在 t=0 时操作数抵消无法检测。使用 t=-1,0,1,2 四组输入确保任一 MATH 突变至少在一组产生差异。
3. **DPCManager.setFestivals = 真 P6**: buildDPInfo 中 `setFestivals(strF[i][j])` 与 `getFestivals()` 懒加载 (`DPCNCalendar.buildDayFestivals()`) 完全冗余——两者对同一日期产生相同结果。
4. **moonCal 死代码**: `jiaoCai(lx=0)` 在 L190 return，永不调用 `moonCal`。反射测试覆盖但公共 API 不触及。
5. **SolarTerm 等价体**: addGxc 光行差修正 ~8分钟，不足以跨越日期边界。angleCal 收敛阈值 1e-15/1e-8 变化产生 <0.1秒差异。全部在 `(int)D` 截断后不变。

**操作符级结果:** INCREMENTS/TRUE_RETURNS/FALSE_RETURNS/PRIMITIVE_RETURNS/NULL_RETURNS 100%, MATH 93%, EMPTY_RETURNS 96%, REMOVE_CONDITIONALS_EQUAL_ELSE 89%

**4个类100%杀死:** Festivals, Gregorian, Lunar, DPCManager

### BPlusTree (248 mutants, 85% killed, 299/305 lines)
- **项目类型:** B+树数据结构实现，含布隆过滤器、泛型节点层次结构
- **关键方法:** 6个业务类：Node(抽象)、LeafNode、InternalNode、BPlusTree、InsertionResult、IntegerBloomFilter
- **Kill策略:**
  - 反射Bitset状态注入（Pattern 18）：注入已知hash参数，断言确切bit位置
  - 概率性构造器循环扫描（Pattern 19）：采样50个实例验证hashParam≠0
  - 断言升级阶梯（Rule 4）：分裂测试从assertNotNull升级到精确assert splitRootKey+左右节点大小
  - 多t值覆盖（Rule 1）：t=3触发快速分裂，t=4深度结构，t=5基础操作
  - ArrayList容量等价（Pattern 15）：3处`new ArrayList<>(t-1)` MATH突变立即标记为等价
  - 复合条件死代码（Pattern 16）：insertNonFull中`index==size-1&&key<last`永假
  - 二分搜索边界等价（Pattern 17）：3处边界突变经双路径追踪确认为等价
  - 自洽内部方法（Pattern 18）：createHashes被add和contains同时调用
- **等价变异体:** 共13个（3 ArrayList容量 + 4 insertNonFull死代码 + 3 二分搜索边界 + 2 概率性构造器 + 1 t=2算法边界）
- **教训:**
  - t=2边界情况：内部节点分裂传播可产生空节点，导致后续搜索IndexOutOfBounds
  - 顺序插入比随机插入更稳定：`for(i=1;i<=N;i++) insert(i,...)` 产生可预测的确定性树结构
  - 弱断言是变异存活的首要原因：`assertTrue(minGap>0)`无法杀死MATH，`assertEquals(20, minGap)`可以
  - 一个强断言杀死多个变异体：`assertEquals(30, result.getSplitRootKey())`同时杀死MATH和RETURN_VALS
  - PIT Test Strength 87% vs Line Coverage 98%说明断言强度不足，不是分支缺失

### CMD (72 mutants, 100% killed, 166/166 lines)
- **项目类型:** CLI命令行参数解析器，无外部依赖的纯Java项目
- **Kill策略:**
  - 多态基类默认路径覆盖（Pattern 12）：匿名Option子类不覆写parseValue
  - 反射Map状态注入（Pattern 14）：注入空ArrayList到values Map
  - `while(true)` + 守卫条件移除 -> TIMED_OUT（Pattern 13）
  - 泛型类型兼容性：便利方法返回`Option<T>`，变量声明必须用`Option<T>`
- **教训:**
  - 编译错误必须在PIT运行前修复：1个编译错误会导致整个测试单元失败
  - 泛型返回类型的不变性：`Option<Boolean>`不能赋值给`Option.BooleanOption`
  - 基类方法的"假未覆盖"：当所有子类都覆写基类方法时，需要刻意构造不覆写的匿名子类
  - TIMED_OUT是正面信号而非问题
  - 异常类测试的三重断言法：getOptionName() + getMessage() + instanceof继承链

### Credit-Card-Validator (255 mutants, 100% killed)
- **关键方法:** 精确边界值测试
- **Kill策略:** 测试卡号长度边界15/16/17位、前缀边界
- **模式:** BOUNDARY_VALUE + 参数化测试

### MementoX (180 mutants, 100% killed)
- **关键方法:** 状态恢复验证
- **Kill策略:** 验证每个Memento保存的状态精确匹配
- **模式:** RETURN_VALS_MUTATOR (assertEquals替代assertNotNull)

### SimpleAlgorithms (440 mutants, 96% killed)
- **关键方法:** 算法结果精确验证
- **Kill策略:**
  - BPlusTree: 深度遍历验证节点结构
  - StrassenMatrix: 非对称矩阵乘法测试 (避免单位矩阵)
  - ClosestPair: 距离计算方向性验证 (不用Math.abs)

---

## 高挑战项目

### WeightBalancedTree2023 (191 mutants, 59% killed)
- **问题:** CommandHandler分支覆盖率26%，BJTreeTester未被测试
- **关键Kill方法:** `getPreorderList().toString()` 深度验证树结构
- **教训:** Void方法未验证副作用导致大量VOID_CALL存活

### Square (449 mutants, 82% killed)
- **关键方法:** 反射测试私有加密方法 (mul, gfMult)；多模式参数化测试 (CBC, CFB, ECB, OFB, CTS)；加密-解密循环验证
- **Kill策略:** MATH_MUTATOR - 测试GF(2^8)乘法表而非0/1

### UnrolledLinkedList2023 (256 mutants, 91.8% killed)
- **关键方法:** 自定义assertThrows验证异常；并发修改检测；split/merge操作后的节点数量验证；内部状态探查
- **等价变异体:** 共21个（遍历对称性13个 + 死存储2个 + 防御式冗余4个 + 计数器单调性2个）

### Nextday (98 mutants, 99% killed, 1 equivalent mutant)
- **关键方法:** 日期递增链式调用 (Year/Month/Day/Date/Nextday)
- **Kill策略:**
  - Year: 反射注入 `currentPos=0` 杀活 `>=0` 边界突变
  - Month: 12 个月份全遍历杀活数组索引 MATH 突变
  - Day: 31/30/29/28 天四种月份尺寸全量覆盖 increment 边界
  - Date: 三场景闭环（日增/月增/年增）杀活 INVERT_NEGS
  - Nextday: 原对象不可变断言杀活 VOID_METHOD_CALL
- **等价变异体:** `Year.isLeap` 中 `<` -> `<=`（支配条件等价）

### Hotel (262 mutants, 94% killed, 386/390 lines)
- **项目类型:** 酒店管理系统 — 状态机(RoomState/FreeTime/Booked/CheckIn) + 排序(Hotel.sortByValue/getValue) + 业务逻辑(Order/Shop/Manager/Product)
- **关键方法:** 13个业务类、~228个@Test单文件聚合
- **Kill策略:**
  - MATH 100% (44/44): `getValue()`中的`res+=price*1000`和`res+=type*1e6`用**setPrice()去耦**+roomCode逆向法击杀
  - VOID_METHOD_CALL 95%: 通过System.out捕获+状态变更断言(Counting Subclass等价模式)
  - BOUNDARY: 多元素数组触发内循环`j<data.length`边界(3+元素使j达到data.length)
  - setPrice()去耦技术: 当addRoom()自动关联price与type/state时，用setPrice覆写使type/state的MATH成为唯一排序区分因子
- **等价变异体:** 共14个确定性等价
  - P1支配条件: `contains("00")`支配`roomCode<=100`(setRoomCode); 外循环`i<len`被内循环`j=i+1;j<len`支配(sortByValue)
  - P16复合死代码: 字符范围检查`(a-z)||(A-Z)`中`c<='Z'`被`'A'<=c`支配
  - P20包装器VOID: `setItems()`冗余(构造器已设置引用,lambda原地修改); 空`println()`无功能影响
  - P2算术恒等: 比较器else分支`return 1`与`return 0`功能等同(TimSort中均表示"不大于")
- **教训:**
  - **关联值去耦是关键**: addRoom自动计算price与type/state关联，使MATH在getValue中无法单独区分——必须用setPrice覆写解耦
  - **单文件聚合可达高覆盖率**: 所有13个业务类统一写入HotelTest.java，达94%变异覆盖
  - **7个算子100%**: FALSE_RETURNS/TRUE_RETURNS/EMPTY_RETURNS/NULL_RETURNS/REMOVE_EQUAL_ELSE/MATH/达到100%
  - **8个类100%**: 状态机三态+OrderItem+RoomType+Manager+ShopKeeper全部击杀
  - **一箭双雕断言**: `assertTrue(posX < posY)`输出顺序断言同时杀死getValue MATH + sortByValue VOID + swap VOID

---

## 框架适配器项目

### MethodHandle (490 mutants, 88% killed, 701/770 lines)
- **项目类型:** Java MethodHandle 适配器框架 (invokebinder)
- **关键方法:** 19 个业务类，全部 304 个 @Test 方法聚合在单一文件中
- **Kill策略:** 结构覆盖策略（Transform.up()不可达时通过构造器+down()+toString()达到~90%行覆盖）；精确类型断言；全分支覆盖；非空断言杀NULL_RETURNS
- **等价变异体:** 共57个（22个终端方法NO_COVERAGE + 8个REMOVE_CONDITIONALS等价 + 6个MATH等价 + 6个VOID等价 + 5个BOUNDARY等价 + 其他）
- **教训:**
  - **单文件聚合可达到高覆盖率**：19个业务类全部测试放在一个SignatureTest.java中，304个@Test达到91%行覆盖
  - **框架终端方法天然不可测**：invoke*/getField/setField需要真实的MethodHandles.Lookup上下文
  - **Transform.up()的MethodHandle类型屏障**：MethodHandles.foldArguments/catchException等API有极其严格的类型匹配要求
  - **Pattern 1/7/20在框架项目中高频出现**：占了存活变异体的70%+

---

## GUI/Animation 项目

### P_Queue (1,032 mutants, 33% killed)
- **关键方法:** Node/ComBox: 100%变异杀死率；Heap: CountingHeap/CountingDP子类精确计数redraw
- **Kill策略:**
  - MATH on animation intermediate coordinates -> 识别为Animation State Restoration等价 (Pattern 9)
  - VOID_METHOD_CALLS on `redraw()` -> Counting Subclass Pattern (Test Pattern 16) 杀活116个
  - CONDITIONALS_BOUNDARY on `setHeap`/`insert` -> Precondition Manipulation
  - ComPanel/AlgAnimApp/AlgAnimFrame/ControlPanel/LFrame -> Headless Trap
- **等价变异体:** Heap animation中180+个MATH/BOUNDARY/INCREMENTS（中间坐标恢复）；bottomMostPosn三元最值对称性
- **教训:**
  - `setHeap()` 不重置 `heapArray`，导致测试时必须先调用 `input2heap()`
  - 动画方法redraw计数必须逐行阅读源码，不可估算
  - Graphics mock验证必须计算每条路径的叠加调用次数
  - **一箭双雕断言**：`assertEquals(-80, ch.runningCom.topLeft.x)` 同时杀死MATH和RETURN_VALS
  - **子类部分模拟 (Test Pattern 19)** 比 Mockito `spy()` 更稳定
  - **渐进式杀活策略**：Node/ComBox(简单类) -> Heap(复杂算法) -> DrawingPanel/TextFrame(GUI类)

---

## 中等覆盖率项目

### ElevatorManager (268 mutants, 75% killed)
- **关键方法:** 单例反射重置确保测试隔离
- **Kill策略:** 测试电梯状态转换的每个分支

### PathFinding (405 mutants, 88% killed)
- **关键方法:** 输出捕获验证日志路径
- **Kill策略:** 验证findPath返回的节点序列精确匹配期望路径

### Library (261 mutants, 85% killed)
- **关键方法:** 多态用户类型测试 (RegularUser/VIPUser)；异常消息精确匹配
- **Kill策略:** RETURN_VALS区分不同用户类型的借阅限制

### Anagram (96 mutants, 80% killed, 186/193 lines)
- **项目类型:** 字符串变位词求解器，含递归算法、Set操作、文件I/O
- **Kill策略:** 系统输出捕获杀VOID_METHOD_CALL；边界值精确断言杀CONDITIONALS_BOUNDARY；输出内容验证防子串误判
- **等价变异体:** 共19个（5个Helper优化守卫等价 + 3个防御性null检查 + 2个for循环BOUNDARY等价 + 2个守卫条件等价 + 2个EMPTY_RETURNS等价 + 1个三元isEmpty等价 + 1个reader.close等价 + 3个死代码NO_COVERAGE）
- **教训:**
  - 递归算法中的优化守卫是系统性的等价来源
  - null≈空Set等价：当调用方使用`!= null && !isEmpty()`双检查时，EMPTY_RETURNS无法杀死
  - 输出捕获测试中子串误判陷阱："-1."包含"1." -> 需用更精确的模式
  - 单文件聚合在小项目中效果显著

---

## 包装器/库封装项目

### FastJson (551 mutants, 68% killed, 866/966 lines)
- **项目类型:** Alibaba fastjson 1.2.70 的薄封装层
- **Kill策略:**
  - assertSame 杀 instanceof 条件：`getJSONObject` 中 `instanceof JSONObject` 检查
  - 有序 Map 插入顺序：`new JSONObject(ordered=true)` 创建 LinkedHashMap
  - 全重载覆盖：逐一调用 JSON.parse/parseObject/parseArray 的每个重载组合
  - 精确 boolean 断言：同时测试返回 true 和 false 的场景
  - NonStandardBean invoke 分支：创建不以 get/set/is 开头的方法
- **等价变异体:** 共177个（24个handleResovleTask/close VOID + 10个serializer.config VOID + 15个SecureObjectInputStream路径 + 其他）
- **教训:**
  - **包装器项目覆盖率天花板 ~68%**: 约30%的变异体是VOID_METHOD_CALL在库内部对象上
  - **IRON RULE: 包装器项目先评估等价率**: 运行第一次PIT后立刻检查VOID_METHOD_CALL存活比例
  - **每个重载必须直接测试**: 不能依赖重载链委托关系
  - **assertSame 比 assertEquals 更强**: 对返回对象引用的方法，assertSame能杀死instanceof检查的REMOVE_CONDITIONALS
