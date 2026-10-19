#!/usr/bin/env python3
"""只读校验器：给出唯一合法的下一个版本号。

背景：模型凭印象写版本号会造成跳号（v2.6.1 -> v2.8.0 -> v2.9.0）。
本脚本强制"从文件读、只进一档、一日一版"。

用法：
    python scripts/next_version.py            # 查看当前版本与合法下一版本
    python scripts/next_version.py --verify   # 只做一致性校验（退出码 1 = 不一致）
"""
import json
import io
import re
import sys
import datetime

CHANGELOG = 'CHANGELOG.md'
DATA = 'project-data.json'


def load():
    with open(DATA, encoding='utf-8') as f:
        data = json.load(f)
    text = io.open(CHANGELOG, encoding='utf-8').read()
    heads = re.findall(r'^## \[(v\d+\.\d+\.\d+)\] - (\d{4}-\d{2}-\d{2})', text, re.M)
    return data, heads


def bump(version, part):
    major, minor, patch = (int(x) for x in version.lstrip('v').split('.'))
    if part == 'PATCH':
        return 'v%d.%d.%d' % (major, minor, patch + 1)
    if part == 'MINOR':
        return 'v%d.%d.0' % (major, minor + 1)
    return 'v%d.0.0' % (major + 1)


def main():
    data, heads = load()
    v_json = data['skill_metadata']['version']
    v_log, date_log = heads[0]
    today = datetime.date.today().isoformat()
    errors = []

    if v_json != v_log:
        errors.append('版本不一致: project-data.json=%s, CHANGELOG.md=%s' % (v_json, v_log))
    if not data['skill_metadata']['changelog'][0].startswith(v_json + ':'):
        errors.append('changelog[0] 未以 "%s:" 开头' % v_json)
    if sum(1 for _, d in heads if d == today) > 1:
        errors.append('今天(%s)出现了多个版本条目: %s' % (
            today, [v for v, d in heads if d == today]))

    print('project-data.json : %s' % v_json)
    print('CHANGELOG.md 最新 : %s (%s)' % (v_log, date_log))
    print('今天              : %s' % today)

    if errors:
        print('\n[FAIL]')
        for e in errors:
            print(' - ' + e)
        return 1

    print('\n[OK] 三方一致')
    if date_log == today:
        print('判定: 今日已有条目 -> 不新增版本，改动就地追加进 [%s]' % v_log)
    else:
        print('判定: 跨日 -> 只进一档，二选一')
        print('  PATCH（仅修错/统计）      -> %s' % bump(v_log, 'PATCH'))
        print('  MINOR（新模式/测试/项目） -> %s' % bump(v_log, 'MINOR'))
    print('\n提醒: CHANGELOG.md + version + changelog[0] 三处必须同时写')
    return 0


if __name__ == '__main__':
    sys.exit(main())
