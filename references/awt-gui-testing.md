# AWT/GUI Class Testing Rules

## Rule 1: Headless Compatibility Check

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

## Rule 2: Skip Headless-Incompatible Classes

If a class constructor directly instantiates `TextField`, `Button`, `Choice`, `Frame`, or `Applet`, and PIT minion runs headless:
- **Do NOT attempt to test it** in the mutation suite
- **Document it** as "untestable in headless CI/PIT environment"
- Do NOT add `jvmArgs` to `pom.xml` to disable headless mode (often violates project constraints)

## Rule 3: Testable GUI Subclass Pattern

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
- `delay()` / `shortDelay()` -> avoid `Thread.sleep`
- `size()` -> return non-zero dimension so `update()` doesn't return early
- `createImage()` -> return mock Image so `update()` can create offscreen buffer

## Rule 4: Graphics Mock Chaining

When testing `paint()` or `update()` with double-buffering:
1. Mock the passed-in `Graphics g`
2. Mock the `Image` returned by `createImage()`
3. Mock the `Graphics` returned by `img.getGraphics()`
4. Verify interactions on BOTH graphics contexts
