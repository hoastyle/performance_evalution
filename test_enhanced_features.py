#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试增强版评分系统的新功能
"""

import sys
sys.path.append('.')
from scoring import ScoringCalculator, ScoringConfig

def test_enhanced_features():
    """测试所有新的增强功能"""
    print("=" * 60)
    print("测试增强版评分系统新功能")
    print("=" * 60)

    calculator = ScoringCalculator()

    # 测试数据
    test_cases = [
        {
            "name": "李宇来",
            "overdue_ratio": 83.3,
            "overdue_days": 18.3,
            "work_days": 7.0,
            "complexity": "中等"
        },
        {
            "name": "石剑锋",
            "overdue_ratio": 18.8,
            "overdue_days": 0.8,
            "work_days": 13.0,
            "complexity": "中等"
        },
        {
            "name": "陈蕴",
            "overdue_ratio": 70.0,
            "overdue_days": 13.6,
            "work_days": 21.0,
            "complexity": "复杂"
        }
    ]

    for case in test_cases:
        print(f"\n{'='*20} {case['name']} {'='*20}")

        # 1. 测试目标1：逾期趋势分析和任务复杂度调整
        print("\n📊 目标1：逾期趋势分析和任务复杂度调整")

        # 逾期趋势分析
        previous_ratios = [75.0, 80.0] if case['name'] == "李宇来" else [20.0, 19.0]
        trend_score = calculator.calculate_overdue_trend_score(case['overdue_ratio'], previous_ratios)
        print(f"   逾期趋势得分: {trend_score:.2f}")

        # 任务复杂度调整
        adjusted_ratio = calculator.calculate_complexity_adjusted_score(case['overdue_ratio'], case['complexity'])
        print(f"   原始逾期比例: {case['overdue_ratio']}%")
        print(f"   调整后逾期比例: {adjusted_ratio:.2f}%")

        # 逾期模式分析
        patterns = calculator.analyze_overdue_patterns(case['overdue_ratio'], case['overdue_days'], case['work_days'])
        print(f"   根本原因: {patterns['root_cause']}")
        print(f"   改进建议: {patterns['suggestion']}")

        # 2. 测试目标2：任务分配合理性检测和排期准确性评估
        print("\n🔍 目标2：任务分配合理性检测和排期准确性评估")

        # 任务分配问题检测
        assignment_issues = calculator.detect_task_assignment_issues(case['work_days'], case['overdue_ratio'])
        if assignment_issues:
            print(f"   任务分配问题: {assignment_issues['assignment_issue']}")
            print(f"   严重程度: {assignment_issues['severity']}")
            print(f"   建议行动: {assignment_issues['action']}")
        else:
            print("   任务分配正常")

        # 排期准确性评估
        estimated_days = case['work_days'] * 0.8  # 假设估算是实际人天的80%
        estimation_result = calculator.evaluate_estimation_accuracy(estimated_days, case['work_days'])
        print(f"   排期准确性: {estimation_result['accuracy']}")
        print(f"   误差率: {estimation_result['error_rate']:.2%}")

        # 工作量异常检测
        team_average = 12.0  # 假设团队平均人天
        workload_anomalies = calculator.detect_workload_anomalies(case['work_days'], team_average)
        if workload_anomalies:
            print(f"   工作量异常: {workload_anomalies['anomaly_type']}")
            print(f"   异常描述: {workload_anomalies['description']}")
        else:
            print("   工作量正常")

        # 3. 测试目标3：稳定性指标和紧急任务处理能力评估
        print("\n🏆 目标3：稳定性指标和紧急任务处理能力评估")

        # 稳定性评估
        if case['name'] == "石剑锋":
            historical_scores = [98.0, 102.0, 100.0]  # 优秀员工的历史分数
        elif case['name'] == "李宇来":
            historical_scores = [25.0, 20.0, 15.0]  # 问题员工的历史分数
        else:
            historical_scores = [45.0, 50.0, 55.0]  # 中等员工的历史分数

        stability_result = calculator.calculate_performance_stability(historical_scores)
        print(f"   绩效稳定性: {stability_result['stability']}")
        print(f"   稳定性得分: {stability_result['stability_score']:.2f}")
        print(f"   标准差: {stability_result['std_dev']:.2f}")

        # 紧急任务处理能力
        urgent_tasks_completed = 8 if case['name'] == "石剑锋" else 3
        urgent_tasks_total = 10
        urgency_result = calculator.evaluate_urgency_handling(urgent_tasks_completed, urgent_tasks_total)
        print(f"   紧急任务处理: {urgency_result['urgency_performance']}")
        print(f"   完成率: {urgency_result['completion_rate']:.2%}")
        print(f"   紧急任务得分: {urgency_result['urgency_score']:.2f}")

        # 4. 测试增强版综合评分
        print("\n🎯 增强版综合评分")

        enhanced_scores = calculator.calculate_enhanced_comprehensive_score(
            case['overdue_ratio'],
            case['overdue_days'],
            case['work_days'],
            case['complexity'],
            previous_ratios,
            historical_scores,
            urgent_tasks_completed,
            urgent_tasks_total
        )

        print(f"   基础综合得分: {enhanced_scores['comprehensive_score']}")
        print(f"   增强版综合得分: {enhanced_scores['enhanced_score']}")
        print(f"   趋势得分: {enhanced_scores['trend_score']}")
        print(f"   稳定性得分: {enhanced_scores['stability_score']}")
        print(f"   紧急任务得分: {enhanced_scores['urgency_score']}")

        # 5. 过载检测
        print(f"\n⚠️  状态检测")
        print(f"   需要核实人天记录: {'是' if calculator.needs_review(case['work_days']) else '否'}")
        print(f"   工作过载: {'是' if calculator.is_overloaded(case['work_days']) else '否'}")

if __name__ == "__main__":
    test_enhanced_features()