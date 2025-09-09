#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工作人天评分逻辑测试 - v2.3版本
测试10人天标准与递增惩罚算法
"""

from scoring import ScoringCalculator, ScoringConfig
import math

def test_work_days_scoring_v23():
    """测试v2.3版本的工作人天评分逻辑"""
    calculator = ScoringCalculator()
    
    print("=== 工作人天评分逻辑测试 - v2.3版本 ===\n")
    
    # 测试用例：涵盖各种工作人天场景
    test_cases = [
        # 低于标准的情况（递增惩罚测试）
        (5.0, "5人天 - 严重不足"),
        (6.0, "6人天 - 明显不足"),  
        (7.0, "7人天 - 不足"),
        (8.0, "8人天 - 接近标准"),
        (9.0, "9人天 - 接近标准"),
        
        # 标准情况
        (10.0, "10人天 - 标准（满分）"),
        
        # 超过标准的情况（加分测试）
        (11.0, "11人天 - 优秀"),
        (12.0, "12人天 - 优秀"),
        (13.0, "13人天 - 优秀"),
        (15.0, "15人天 - 一级加分上限"),
        (18.0, "18人天 - 二级加分区间"),
        (20.0, "20人天 - 二级加分上限"),
        (25.0, "25人天 - 三级加分区间"),
    ]
    
    print("工作人天\t得分\t等级\t说明")
    print("-" * 60)
    
    for days, description in test_cases:
        score = calculator.calculate_work_days_score(days)
        grade = get_grade(score)
        
        # 计算惩罚/奖励详情
        details = get_score_details(days, score, calculator)
        
        print(f"{days:6.1f}人天\t{score:5.1f}\t{grade}\t{description}")
        if details:
            print(f"\t\t\t\t{details}")
    
    print("\n=== 递增惩罚算法验证 ===")
    print("验证惩罚程度随距离标准越远而递增：")
    
    penalty_test_cases = [(9, 8, 7, 6, 5, 4, 3)]
    for cases in penalty_test_cases:
        print("\n工作人天\t惩罚值\t惩罚差异")
        print("-" * 40)
        previous_penalty = 0
        for days in cases:
            score = calculator.calculate_work_days_score(days)
            penalty = 100 - score
            penalty_increase = penalty - previous_penalty if previous_penalty > 0 else 0
            print(f"{days}人天\t\t{penalty:5.1f}\t+{penalty_increase:5.1f}")
            previous_penalty = penalty
    
    print("\n=== 完整评分示例 ===")
    print("展示工作人天评分在综合评分中的应用：")
    
    comprehensive_cases = [
        (15.0, 2.5, 8.0),   # 低逾期比例，低逾期天数，低工作量
        (15.0, 2.5, 12.0),  # 低逾期比例，低逾期天数，高工作量
        (25.0, 4.0, 6.0),   # 高逾期比例，高逾期天数，低工作量
        (25.0, 4.0, 15.0),  # 高逾期比例，高逾期天数，高工作量
    ]
    
    print("\n逾期比例\t逾期天数\t工作人天\t工作人天得分\t综合得分")
    print("-" * 70)
    
    for ratio, days_overdue, work_days in comprehensive_cases:
        work_score = calculator.calculate_work_days_score(work_days)
        comprehensive_scores = calculator.calculate_comprehensive_score(ratio, days_overdue, work_days)
        comprehensive_score = comprehensive_scores["comprehensive_score"]
        
        print(f"{ratio:6.1f}%\t\t{days_overdue:4.1f}天\t\t{work_days:6.1f}人天\t\t{work_score:6.1f}\t\t{comprehensive_score:6.1f}")

def get_grade(score):
    """根据得分获取等级"""
    if score >= 85:
        return "S"
    elif score >= 70:
        return "A"
    elif score >= 55:
        return "B"
    elif score >= 40:
        return "C"
    else:
        return "D"

def get_score_details(days, score, calculator):
    """获取得分详细说明"""
    params = calculator.config.work_days_params
    standard_days = params["standard_days"]
    
    if days < standard_days:
        penalty = calculator.calculate_progressive_penalty(
            days, standard_days, 
            params["base_penalty_rate"], 
            params["progressive_multiplier"]
        )
        return f"递增惩罚: -{penalty:.1f}分"
    elif days == standard_days:
        return "满分标准"
    elif days > standard_days:
        bonus = score - 100
        return f"超标奖励: +{bonus:.1f}分"
    
    return ""

def test_progressive_penalty_formula():
    """测试递增惩罚公式的数学正确性"""
    print("\n=== 递增惩罚公式验证 ===")
    calculator = ScoringCalculator()
    
    # 验证公式：base_penalty * (multiplier)^(gap-1) * gap
    base_penalty = 5.0
    multiplier = 1.2
    standard = 10.0
    
    print("距离标准\t计算惩罚\t预期惩罚\t匹配")
    print("-" * 50)
    
    for days in [9, 8, 7, 6, 5]:
        gap = standard - days
        expected_penalty = base_penalty * (multiplier ** (gap - 1)) * gap
        actual_penalty = calculator.calculate_progressive_penalty(days, standard, base_penalty, multiplier)
        match = "✓" if abs(expected_penalty - actual_penalty) < 0.01 else "✗"
        print(f"{gap}人天\t\t{actual_penalty:6.2f}\t\t{expected_penalty:6.2f}\t\t{match}")

if __name__ == "__main__":
    test_work_days_scoring_v23()
    test_progressive_penalty_formula()