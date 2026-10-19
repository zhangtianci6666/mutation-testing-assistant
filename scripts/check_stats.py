#!/usr/bin/env python3
"""统计一致性校验器（只读）。

同一组数字散落在 5 个位置：
  1. project-data.json -> skill_metadata
  2. project-data.json -> project_statistics.summary
  3. project-data.json -> project_statistics.projects[]（明细累加）
  4. README.md（头部 + 项目数据表）
  5. SKILL.md（Overview 计数 + Quick Reference 实际行数）

用法：
    python scripts/check_stats.py          # 校验，FAIL 时退出码 1
"""
import io
import json
import re
import sys


def read(path):
    return io.open(path, encoding='utf-8').read()


def main():
    fails = []
    warns = []

    data = json.load(open('project-data.json', encoding='utf-8'))
    md = data['skill_metadata']
    summary = data['project_statistics']['summary']
    projects = data['project_statistics']['projects']

    # ---- 1) JSON 内部：metadata vs summary -------------------------------
    for key in ('total_mutants', 'killed_mutants', 'survived_mutants', 'equivalent_mutants'):
        if md.get(key) != summary.get(key):
            fails.append('metadata.%s=%s 与 summary.%s=%s 不一致'
                         % (key, md.get(key), key, summary.get(key)))

    # ---- 2) 恒等式 total = killed + survived -----------------------------
    total, killed, survived = md['total_mutants'], md['killed_mutants'], md['survived_mutants']
    if killed + survived != total:
        fails.append('恒等式不成立: killed(%d) + survived(%d) = %d, 但 total = %d（差 %d）'
                     % (killed, survived, killed + survived, total, total - killed - survived))

    # ---- 3) 明细累加 vs total -------------------------------------------
    detail = sum(p.get('mutants', 0) for p in projects)
    if detail != total:
        warns.append('projects[] 累加 %d 与 total %d 不等（项目表可能未覆盖历史项目）'
                     % (detail, total))

    # ---- 4) 模式计数：SKILL.md 宣称值 vs 实际表行数 ----------------------
    skill = read('SKILL.md')
    m = re.search(r'Covers (\d+) survival patterns', skill)
    claim_p = int(m.group(1)) if m else None
    actual_p = len(re.findall(r'^\| P\d+:', skill, re.M))
    if claim_p is not None and claim_p != actual_p:
        fails.append('SKILL.md: 宣称 %d 个存活模式，Quick Reference 实有 %d 行'
                     % (claim_p, actual_p))

    m = re.search(r'(\d+) test patterns', skill)
    claim_tp = int(m.group(1)) if m else None
    # catalog 存在两种标题风格：'### 1. 名称' 与 '### Pattern 24: 名称'
    catalog = read('references/test-patterns-catalog.md')
    actual_tp = len(re.findall(r'^### (?:\d+\.|Pattern \d+:)', catalog, re.M))
    if claim_tp is not None and claim_tp != actual_tp:
        fails.append('SKILL.md: 宣称 %d 个测试模式，catalog 实有 %d 个'
                     % (claim_tp, actual_tp))

    # ---- 5) README：头部与表格 ------------------------------------------
    readme = read('README.md')

    m = re.search(r'基于 (\d+) 个 Java 项目、([\d,]+) 个变异体', readme)
    if m:
        if int(m.group(1)) != len(projects):
            fails.append('README 头部项目数 %s != projects[] 条数 %d' % (m.group(1), len(projects)))
        if int(m.group(2).replace(',', '')) != total:
            fails.append('README 头部变异体数 %s != json total %d' % (m.group(2), total))
    else:
        warns.append('README 头部未找到"基于 X 个项目、Y 个变异体"')

    for label, expect in (('存活模式', actual_p), ('测试模式', actual_tp)):
        m = re.search(r'(\d+) 个(?:已知)?%s' % label, readme)
        if m and int(m.group(1)) != expect:
            fails.append('README 写 %s=%s，实际 %d' % (label, m.group(1), expect))

    for label, expect in (('分析项目数', len(projects)),
                          ('总变异体数', total),
                          ('等价变异体数', md['equivalent_mutants'])):
        m = re.search(r'\| %s \| ([\d,]+) \|' % label, readme)
        if m:
            got = int(m.group(1).replace(',', ''))
            if got != expect:
                fails.append('README 表格 %s = %d，应为 %d' % (label, got, expect))
        else:
            warns.append('README 表格缺 %s 行' % label)

    # ---- 6) SKILL.md Overview：项目数 / 变异体数 / 运算符数 ----------------
    m = re.search(r'analysis of (\d+) Java projects, ([\d,]+)\+? mutants', skill)
    if m:
        if int(m.group(1)) != len(projects):
            fails.append('SKILL.md Overview 项目数 %s != projects[] 条数 %d'
                         % (m.group(1), len(projects)))
        if int(m.group(2).replace(',', '')) != total:
            fails.append('SKILL.md Overview 变异体数 %s != json total %d' % (m.group(2), total))
    else:
        warns.append('SKILL.md Overview 未找到 "N Java projects, M+ mutants"')

    op_count = len(data['mutant_operators']['supported'])
    for pattern in (r'(\d+) mutation operators', r'(\d+) operators,'):
        m = re.search(pattern, skill)
        if m and int(m.group(1)) != op_count:
            fails.append('SKILL.md 运算符数写 %s，mutant_operators.supported 实有 %d'
                         % (m.group(1), op_count))

    # ---- 7) 模式上限引用：P1-P{N} / "all N patterns" ----------------------
    for label in ('SKILL.md', 'references/self-optimization.md'):
        text = read(label)
        for n in re.findall(r'P1-P(\d+)', text):
            if int(n) != actual_p:
                fails.append('%s 引用 P1-P%s，实际存活模式数 %d（新增模式后未连带改引用）'
                             % (label, n, actual_p))
        for n in re.findall(r'all (\d+) patterns', text):
            if int(n) != actual_p:
                fails.append('%s 写 "all %s patterns"，实际 %d' % (label, n, actual_p))

    # ---- 输出 -----------------------------------------------------------
    print('存活模式: SKILL 宣称 %s / 实际 %d' % (claim_p, actual_p))
    print('测试模式: SKILL 宣称 %s / 实际 %d' % (claim_tp, actual_tp))
    print('变异体  : total=%d killed=%d survived=%d equiv=%d'
          % (total, killed, survived, md['equivalent_mutants']))

    if warns:
        print('\n[WARN]')
        for w in warns:
            print(' - ' + w)
    if fails:
        print('\n[FAIL]')
        for f in fails:
            print(' - ' + f)
        return 1
    print('\n[OK] 5 处统计一致')
    return 0


if __name__ == '__main__':
    sys.exit(main())
