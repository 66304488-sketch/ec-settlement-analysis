# -*- coding: utf-8 -*-
"""
组装19章节的index.html
1. 提取旧章节行范围
2. 插入新章节HTML
3. 重新编号h2标题
4. 更新交叉引用
5. 更新分隔线
"""
import re, sys
sys.path.insert(0, '/Users/linyixin/Desktop/jinhua/ec跟踪分析')
from build_sections import (
    sec_8_scfi_conversion, sec_9_seasonality, sec_12_preposition,
    sec_15_trend_framework, sec_16_trend_backtest,
    sec_18_investment, sec_19_insights
)

import subprocess

# 从git读取与行号匹配的原始index.html（commit 8467581：首次19章重构版本）
result = subprocess.run(
    ['git', '-C', '/Users/linyixin/Desktop/jinhua/ec跟踪分析', 'show', '8467581:index.html'],
    capture_output=True, text=True
)
if result.returncode != 0:
    print("ERROR: 无法从git读取原始index.html")
    sys.exit(1)
lines = result.stdout.splitlines(keepends=True)

print(f"读取 index.html: {len(lines)} 行")

# 章节边界（第几行，1-indexed）
# 每个section从注释行开始
section_ranges = {
    'header':        (1, 73),
    'sec_1':         (74, 86),     # 一、关键统计概览
    'sec_2':         (87, 105),    # 二、三重价格体系说明
    'sec_3':         (106, 211),   # 三、全部14个合约
    'sec_4':         (212, 338),   # 四、P1/P2/P3 明细
    'part1_div':     (339, 345),   # 第一篇分隔线
    'old_5':         (346, 374),   # 五、三重价格对比
    'old_6':         (375, 405),   # 六、盘面定价效率
    'old_7':         (406, 457),   # 七、六大核心规律
    'old_8':         (458, 600),   # 八、交割期震荡规律 → 新十
    'old_9':         (601, 755),   # 九、交割博弈操作指南 → 新十一
    'old_10':        (756, 1158),  # 十、策略计算复核 → 新十三
    'old_11':        (1161, 1191), # 十一、每手偏差金额 → 新十四
    'part2_div':     (1192, 1198), # 第二篇分隔线
    'old_16':        (2411, 2592), # 十六、跨期套保策略 → 新十七
    'footer':        (2626, 2637), # 页脚
}

def get_section(key):
    """获取章节的HTML文本（行列表连接）"""
    if key not in section_ranges:
        return ''
    start, end = section_ranges[key]
    return ''.join(lines[start-1:end])

# 获取新章节HTML
print("生成新章节HTML...")
new_sec_8 = sec_8_scfi_conversion()
new_sec_9 = sec_9_seasonality()
new_sec_12 = sec_12_preposition()
new_sec_15 = sec_15_trend_framework()
new_sec_16 = sec_16_trend_backtest()
new_sec_18 = sec_18_investment()
new_sec_19 = sec_19_insights()

print(f"  新八: {len(new_sec_8)} chars")
print(f"  新九: {len(new_sec_9)} chars")
print(f"  新十二: {len(new_sec_12)} chars")
print(f"  新十五: {len(new_sec_15)} chars")
print(f"  新十六: {len(new_sec_16)} chars")
print(f"  新十八: {len(new_sec_18)} chars")
print(f"  新十九: {len(new_sec_19)} chars")

# ============================================================
# H2 重新编号
# ============================================================
cn_nums = ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十',
           '十一', '十二', '十三', '十四', '十五', '十六', '十七', '十八', '十九']

def renumber_h2(text, new_num_cn):
    """将文本中的第一个 <h2>X、 替换为 <h2>新编号、"""
    # 匹配 <h2>任意中文数字、
    return re.sub(r'<h2>[一二三四五六七八九十]+、', f'<h2>{new_num_cn}、', text, count=1)

# 旧→新中文数字映射（用于交叉引用替换）
# 旧编号 → 新编号
cn_map = {
    '八': '十',     # 旧8→新10
    '九': '十一',   # 旧9→新11
    '十': '十三',   # 旧10→新13
    '十一': '十四', # 旧11→新14
    '十二': '八',   # 旧12→新8
    '十三': '九',   # 旧13→新9
    '十四': '十二', # 旧14→新12
    '十五': '十八', # 旧15→新18
    '十六': '十七', # 旧16→新17
    '十七': '十九', # 旧17→新19
}

def fix_cross_refs(text):
    """修复交叉引用中的章节编号"""
    # 按长度降序排列，避免部分匹配问题
    # 例如"十一"在"十四"之前匹配会导致问题
    sorted_keys = sorted(cn_map.keys(), key=len, reverse=True)

    # 策略：先替换所有"第X章"格式
    for old_cn in sorted_keys:
        new_cn = cn_map[old_cn]
        # 第X章
        text = text.replace(f'第{old_cn}章', f'\x00{new_cn}\x01')
        # （X章）
        text = text.replace(f'（{old_cn}章）', f'（\x00{new_cn}\x01）')
        # 详见X章
        text = text.replace(f'详见{old_cn}章', f'详见\x00{new_cn}\x01')

    # 恢复占位符
    text = text.replace('\x00', '第')
    text = text.replace('\x01', '章')

    # 修正 "第第" 重复 → "第"
    text = text.replace('第第', '第')
    # 修正 "章章" 重复 → "章"
    text = text.replace('章章', '章')

    return text

# ============================================================
# 组装各部分
# ============================================================

# 需要重新编号的保留章节
old_8_renumbered = renumber_h2(fix_cross_refs(get_section('old_8')), '十')
old_9_renumbered = renumber_h2(fix_cross_refs(get_section('old_9')), '十一')
old_10_renumbered = renumber_h2(fix_cross_refs(get_section('old_10')), '十三')
old_11_renumbered = renumber_h2(fix_cross_refs(get_section('old_11')), '十四')
old_16_renumbered = renumber_h2(fix_cross_refs(get_section('old_16')), '十七')

# 不需要重新编号的保留章节（编号不变）
# 但内部交叉引用需要更新
sec_1 = fix_cross_refs(get_section('sec_1'))
sec_2 = fix_cross_refs(get_section('sec_2'))
sec_3 = fix_cross_refs(get_section('sec_3'))
sec_4 = fix_cross_refs(get_section('sec_4'))
old_5 = fix_cross_refs(get_section('old_5'))
old_6 = fix_cross_refs(get_section('old_6'))
old_7 = fix_cross_refs(get_section('old_7'))

# 更新分隔线
part1_div = get_section('part1_div')
part2_div = get_section('part2_div')
# 更新第二篇分隔线的副标题
part2_div = part2_div.replace(
    '趋势跟踪与提前布局 —— SCFI 信号驱动的中长期策略',
    '纯趋势跟踪 —— 不依赖交割结算价的独立策略'
)

# ============================================================
# 组装最终文件
# ============================================================

final_parts = [
    get_section('header'),
    # 基础篇（一~四）
    sec_1,
    sec_2,
    sec_3,
    sec_4,
    # 第一篇分隔线
    part1_div,
    # 第一篇：交割期操作（五~十四）
    old_5,                    # 五、三重价格对比
    old_6,                    # 六、盘面定价效率
    old_7,                    # 七、六大核心规律
    new_sec_8,                # 八、SCFI→SCFIS精确换算（新）
    new_sec_9,                # 九、SCFI淡旺季与交割预判（新）
    old_8_renumbered,         # 十、交割期震荡规律
    old_9_renumbered,         # 十一、交割博弈操作指南
    new_sec_12,               # 十二、提前建仓回测（新）
    old_10_renumbered,        # 十三、策略计算复核
    old_11_renumbered,        # 十四、每手偏差金额分布
    # 第二篇分隔线
    part2_div,
    # 第二篇：非交割期操作（十五~十九）
    new_sec_15,               # 十五、趋势跟踪框架（新）
    new_sec_16,               # 十六、趋势交易回测（新）
    old_16_renumbered,        # 十七、跨期套保策略
    new_sec_18,               # 十八、投资逻辑与策略建议（新）
    new_sec_19,               # 十九、实操启示（新）
    get_section('footer'),
]

final_html = ''.join(final_parts)

# 全局交叉引用修复（在已经被处理过的部分之上再做一次）
# 修复 build_sections 中可能的旧引用
final_html = final_html.replace('第九章', '第第九章')  # dummy to avoid double-replace
# 清理可能的双重引用残留
final_html = re.sub(r'第第([一二三四五六七八九十]+)章', r'第\1章', final_html)
final_html = re.sub(r'章章', '章', final_html)

# 更新标题中的年份注释
final_html = final_html.replace(
    '报告生成：2026年5月26日',
    '报告生成：2026年5月28日'
)

with open('/Users/linyixin/Desktop/jinhua/ec跟踪分析/index.html', 'w', encoding='utf-8') as f:
    f.write(final_html)

print(f"\n写入 index.html: {len(final_html)} 字符, {final_html.count(chr(10))} 行")

# ============================================================
# 验证
# ============================================================
print("\n=== 验证 ===")

# 1. 检查19个章节的h2编号
h2_matches = re.findall(r'<h2>([一二三四五六七八九十]+)、', final_html)
print(f"H2 章节数: {len(h2_matches)}")
for i, cn in enumerate(h2_matches, 1):
    expected = cn_nums[i-1]
    status = '✓' if cn == expected else f'✗ (期望{expected})'
    print(f"  {i:2d}. {cn} {status}")

# 2. 检查分隔线
part1_count = final_html.count('第一篇：交割期操作')
part2_count = final_html.count('第二篇：非交割期操作')
print(f"\n第一篇分隔线: {part1_count}个 (期望1)")
print(f"第二篇分隔线: {part2_count}个 (期望1)")

# 3. 检查 cross-reference 引用
refs = re.findall(r'第[一二三四五六七八九十]+章', final_html)
print(f"\n交叉引用数: {len(refs)}")
# 去重统计
from collections import Counter
ref_counts = Counter(refs)
for ref, count in sorted(ref_counts.items()):
    print(f"  {ref}: {count}次")

# 4. 检查是否还有旧编号引用（可能未修复的）
old_refs_12 = final_html.count('第十二章')
old_refs_13 = final_html.count('第十三章')
old_refs_14 = final_html.count('第十四章')
old_refs_15 = final_html.count('第十五章')
old_refs_17 = final_html.count('第十七章')
print(f"\n旧引用残留检查:")
print(f"  第十二章: {old_refs_12}次 (新系统中 十二=提前建仓回测)")
print(f"  第十三章: {old_refs_13}次 (新系统中 十三=策略计算复核)")
print(f"  第十四章: {old_refs_14}次 (新系统中 十四=每手偏差金额)")
print(f"  第十五章: {old_refs_15}次 (新系统中 十五=趋势跟踪框架)")
print(f"  第十七章: {old_refs_17}次 (新系统中 十七=跨期套保)")

print("\n组装完成！")
