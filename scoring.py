#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
研发团队数据处理和评分计算器 - 优化版
基于业务需求优化的评分方案
版本：2.1 - 优化工作人天评分逻辑（人天越多越好）
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass
import argparse
import re

@dataclass
class ScoringConfig:
    """优化后的评分配置类"""
    
    # 权重配置 - 优化版
    weights = {
        "overdue_ratio": 0.4,      # 逾期比例权重
        "overdue_days": 0.4,       # 逾期天数权重
        "work_days": 0.2           # 工作人天权重
    }
    
    # 逾期比例评分参数 - 优化版
    overdue_ratio_params = {
        "baseline": 20.0,          # 基准线20%
        "multiplier": 2.0,         # 惩罚力度
        "max_score": 100,
        "min_score": 0
    }
    
    # 逾期天数评分参数 - 优化版
    overdue_days_params = {
        "baseline": 2.0,           # 基准线2天
        "multiplier": 15,          # 惩罚力度
        "max_score": 100,
        "min_score": 0
    }
    
    # 工作人天评分参数 - 新优化版（人天越多越好）
    work_days_params = {
        "ideal_min": 8,            # 理想最小人天
        "ideal_max": 10,           # 理想最大人天
        "bonus_tier1_max": 15,     # 一级加分区间上限
        "bonus_tier1_rate": 2,     # 一级加分：每人天+2分
        "bonus_tier2_rate": 1,     # 二级加分：每人天+1分
        "penalty_rate": 10,        # 人天不足惩罚：每人天-10分
        "max_score": 120,          # 最高分120分
        "min_score": 20,           # 最低分20分
        "inflation_threshold": 15   # 人天膨胀提醒阈值
    }
    
    # 等级划分 - 优化版
    grade_thresholds = {
        "S": 85,    # S级门槛
        "A": 70,    # A级门槛
        "B": 55,    # B级门槛
        "C": 40     # C级门槛，低于此为D级
    }

class DataParser:
    """数据解析器"""
    
    @staticmethod
    def parse_overdue_data(file_path: str) -> Dict[str, float]:
        """解析逾期比例数据文件"""
        data = {}
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
        
        # 每3行为一组：姓名、逾期比例、中位数
        for i in range(0, len(lines), 3):
            if i + 2 < len(lines):
                name = lines[i]
                ratio_str = lines[i + 1]
                # 提取百分比数字
                ratio = float(ratio_str.replace('%', ''))
                data[name] = ratio
        
        return data
    
    @staticmethod
    def parse_mean_overdue_data(file_path: str) -> Dict[str, float]:
        """解析逾期天数均值数据文件"""
        data = {}
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
        
        # 每3行为一组：姓名、天数、中位数
        for i in range(0, len(lines), 3):
            if i + 2 < len(lines):
                name = lines[i]
                days = float(lines[i + 1])
                data[name] = days
        
        return data
    
    @staticmethod
    def parse_days_data(file_path: str) -> Dict[str, float]:
        """解析工作人天数据文件"""
        data = {}
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
        
        # 每5行为一组：姓名、实际工时（人天）、估分、实际工时中位数、估分中位数
        for i in range(0, len(lines), 5):
            if i + 4 < len(lines):
                name = lines[i]
                work_days = float(lines[i + 1])  # 直接使用人天数据
                data[name] = work_days
        
        return data
    
    @staticmethod
    def validate_data(overdue_data: Dict[str, float], 
                     mean_overdue_data: Dict[str, float], 
                     days_data: Dict[str, float]) -> Tuple[bool, str]:
        """验证数据的合理性"""
        
        # 检查数据是否为空
        if not overdue_data or not mean_overdue_data or not days_data:
            return False, "存在空数据集"
        
        # 检查是否有交集
        all_names = set(overdue_data.keys()) & set(mean_overdue_data.keys()) & set(days_data.keys())
        if not all_names:
            return False, "三个数据集没有共同的员工姓名"
        
        # 检查数据范围
        for name, ratio in overdue_data.items():
            if ratio < 0 or ratio > 100:
                return False, f"逾期比例数据异常: {name} = {ratio}%"
        
        for name, days in mean_overdue_data.items():
            if days < 0:
                return False, f"逾期天数数据异常: {name} = {days}天"
        
        for name, work_days in days_data.items():
            if work_days < 0:
                return False, f"工作人天数据异常: {name} = {work_days}人天"
        
        return True, "数据验证通过"

class ScoringCalculator:
    """优化版评分计算器"""
    
    def __init__(self, config: ScoringConfig = None):
        self.config = config or ScoringConfig()
    
    def calculate_overdue_ratio_score(self, ratio: float) -> float:
        """计算逾期比例得分"""
        params = self.config.overdue_ratio_params
        score = params["max_score"] - max(0, ratio - params["baseline"]) * params["multiplier"]
        return max(params["min_score"], min(params["max_score"], score))
    
    def calculate_overdue_days_score(self, days: float) -> float:
        """计算逾期天数得分"""
        params = self.config.overdue_days_params
        score = params["max_score"] - max(0, days - params["baseline"]) * params["multiplier"]
        return max(params["min_score"], score)
    
    def calculate_work_days_score(self, days: float) -> float:
        """计算工作人天得分 - 新优化版（人天越多越好）"""
        params = self.config.work_days_params
        
        if days < params["ideal_min"]:
            # 人天不足：每少1天扣10分
            score = 100 - (params["ideal_min"] - days) * params["penalty_rate"]
            return max(params["min_score"], score)
        elif params["ideal_min"] <= days <= params["ideal_max"]:
            # 理想区间：8-10人天满分100分
            return 100
        elif params["ideal_max"] < days <= params["bonus_tier1_max"]:
            # 一级加分区间：10-15人天，每增加1人天加2分
            bonus_days = days - params["ideal_max"]
            score = 100 + bonus_days * params["bonus_tier1_rate"]
            return min(params["max_score"], score)
        else:
            # 二级加分区间：>15人天，每增加1人天加1分
            tier1_bonus = (params["bonus_tier1_max"] - params["ideal_max"]) * params["bonus_tier1_rate"]
            tier2_bonus = (days - params["bonus_tier1_max"]) * params["bonus_tier2_rate"]
            score = 100 + tier1_bonus + tier2_bonus
            return min(params["max_score"], score)
    
    def calculate_comprehensive_score(self, overdue_ratio: float, 
                                    overdue_days: float, 
                                    work_days: float) -> Dict[str, float]:
        """计算综合得分"""
        
        # 计算各项得分
        ratio_score = self.calculate_overdue_ratio_score(overdue_ratio)
        days_score = self.calculate_overdue_days_score(overdue_days)
        work_days_score = self.calculate_work_days_score(work_days)
        
        # 加权综合得分
        weights = self.config.weights
        comprehensive_score = (
            ratio_score * weights["overdue_ratio"] +
            days_score * weights["overdue_days"] +
            work_days_score * weights["work_days"]
        )
        
        return {
            "overdue_ratio_score": round(ratio_score, 2),
            "overdue_days_score": round(days_score, 2),
            "work_days_score": round(work_days_score, 2),
            "comprehensive_score": round(comprehensive_score, 2)
        }
    
    def get_grade(self, score: float) -> str:
        """根据得分获取等级"""
        thresholds = self.config.grade_thresholds
        
        if score >= thresholds["S"]:
            return "S"
        elif score >= thresholds["A"]:
            return "A"
        elif score >= thresholds["B"]:
            return "B"
        elif score >= thresholds["C"]:
            return "C"
        else:
            return "D"
    
    def explain_score(self, overdue_ratio: float, overdue_days: float, 
                     work_days: float) -> str:
        """解释评分详情"""
        scores = self.calculate_comprehensive_score(overdue_ratio, overdue_days, work_days)
        params = self.config.work_days_params
        
        explanation = []
        
        # 逾期比例分析
        if overdue_ratio <= 20:
            explanation.append(f"✅ 逾期比例{overdue_ratio:.1f}%表现良好")
        else:
            explanation.append(f"⚠️ 逾期比例{overdue_ratio:.1f}%超出基准(20%)")
        
        # 逾期天数分析
        if overdue_days <= 2:
            explanation.append(f"✅ 逾期天数{overdue_days:.1f}天控制良好")
        else:
            explanation.append(f"⚠️ 逾期天数{overdue_days:.1f}天超出基准(2天)")
        
        # 工作量分析 - 新逻辑
        if work_days < params["ideal_min"]:
            explanation.append(f"📉 工作量{work_days:.1f}人天不足")
        elif params["ideal_min"] <= work_days <= params["ideal_max"]:
            explanation.append(f"✅ 工作量{work_days:.1f}人天理想")
        elif params["ideal_max"] < work_days <= params["bonus_tier1_max"]:
            explanation.append(f"💪 工作量{work_days:.1f}人天优秀")
        else:
            if work_days > params["inflation_threshold"]:
                explanation.append(f"🔥 工作量{work_days:.1f}人天超高⚠️需核实人天记录")
            else:
                explanation.append(f"🔥 工作量{work_days:.1f}人天超高")
        
        return " | ".join(explanation)
    
    def needs_review(self, work_days: float) -> bool:
        """判断是否需要核实人天记录"""
        return work_days > self.config.work_days_params["inflation_threshold"]

class DataProcessor:
    """数据处理器"""
    
    def __init__(self, config: ScoringConfig = None):
        self.calculator = ScoringCalculator(config)
        self.parser = DataParser()
    
    def process_files(self, overdue_file: str, mean_overdue_file: str, 
                     days_file: str) -> pd.DataFrame:
        """处理三个数据文件并生成评分结果"""
        
        # 解析三个文件
        overdue_data = self.parser.parse_overdue_data(overdue_file)
        mean_overdue_data = self.parser.parse_mean_overdue_data(mean_overdue_file)
        days_data = self.parser.parse_days_data(days_file)
        
        # 验证数据
        is_valid, message = self.parser.validate_data(overdue_data, mean_overdue_data, days_data)
        if not is_valid:
            raise ValueError(f"数据验证失败: {message}")
        
        print(f"数据验证: {message}")
        
        # 获取所有员工名单（取交集）
        all_names = set(overdue_data.keys()) & set(mean_overdue_data.keys()) & set(days_data.keys())
        
        results = []
        for name in all_names:
            # 获取每个员工的三项数据
            overdue_ratio = overdue_data[name]
            overdue_days = mean_overdue_data[name]
            work_days = days_data[name]
            
            # 计算得分
            scores = self.calculator.calculate_comprehensive_score(
                overdue_ratio, overdue_days, work_days
            )
            
            grade = self.calculator.get_grade(scores["comprehensive_score"])
            explanation = self.calculator.explain_score(overdue_ratio, overdue_days, work_days)
            needs_review = self.calculator.needs_review(work_days)
            
            result = {
                "name": name,
                "overdue_ratio": overdue_ratio,
                "overdue_days": overdue_days,
                "work_days": work_days,
                **scores,
                "grade": grade,
                "explanation": explanation,
                "needs_review": needs_review
            }
            results.append(result)
        
        # 转换为DataFrame并排序
        df = pd.DataFrame(results)
        df = df.sort_values("comprehensive_score", ascending=False).reset_index(drop=True)
        df.index += 1  # 排名从1开始
        
        return df
    
    def analyze_statistics(self, df: pd.DataFrame) -> Dict:
        """分析统计信息"""
        stats = {
            "总人数": len(df),
            "平均综合得分": round(df["comprehensive_score"].mean(), 2),
            "得分中位数": round(df["comprehensive_score"].median(), 2),
            "最高分": df["comprehensive_score"].max(),
            "最低分": df["comprehensive_score"].min(),
            "等级分布": df["grade"].value_counts().to_dict(),
            "Highlight候选": df[df["grade"] == "S"]["name"].tolist(),
            "Lowlight需关注": df[df["grade"] == "D"]["name"].tolist(),
            "需核实人天": df[df["needs_review"] == True]["name"].tolist(),
            "逾期分析": {
                "平均逾期比例": round(df["overdue_ratio"].mean(), 2),
                "平均逾期天数": round(df["overdue_days"].mean(), 2),
                "逾期比例>50%": len(df[df["overdue_ratio"] > 50]),
                "逾期天数>5天": len(df[df["overdue_days"] > 5])
            },
            "工作量分析": {
                "平均人天": round(df["work_days"].mean(), 2),
                "人天中位数": round(df["work_days"].median(), 2),
                "工作量不足(<8人天)": len(df[df["work_days"] < 8]),
                "理想区间(8-10人天)": len(df[(df["work_days"] >= 8) & (df["work_days"] <= 10)]),
                "优秀表现(10-15人天)": len(df[(df["work_days"] > 10) & (df["work_days"] <= 15)]),
                "超高产出(>15人天)": len(df[df["work_days"] > 15]),
                "需核实记录(>15人天)": len(df[df["needs_review"] == True])
            }
        }
        return stats
    
    def print_detailed_analysis(self, df: pd.DataFrame):
        """打印详细分析报告"""
        stats = self.analyze_statistics(df)
        
        print("\n" + "="*60)
        print("           研发团队效能评分分析报告 (优化版v2.1)")
        print("="*60)
        
        print(f"\n📊 基础统计:")
        print(f"   总评估人数: {stats['总人数']}人")
        print(f"   平均综合得分: {stats['平均综合得分']}分")
        print(f"   得分中位数: {stats['得分中位数']}分")
        print(f"   分数区间: {stats['最低分']} - {stats['最高分']}分")
        
        print(f"\n🏆 等级分布 (S≥85, A≥70, B≥55, C≥40):")
        grade_order = ['S', 'A', 'B', 'C', 'D']
        for grade in grade_order:
            count = stats['等级分布'].get(grade, 0)
            percentage = round(count / stats['总人数'] * 100, 1) if stats['总人数'] > 0 else 0
            print(f"   {grade}级: {count}人 ({percentage}%)")
        
        print(f"\n⏰ 逾期问题分析:")
        overdue_stats = stats['逾期分析']
        print(f"   平均逾期比例: {overdue_stats['平均逾期比例']}% (基准: 20%)")
        print(f"   平均逾期天数: {overdue_stats['平均逾期天数']}天 (基准: 2天)")
        print(f"   严重逾期(>50%): {overdue_stats['逾期比例>50%']}人")
        print(f"   长期逾期(>5天): {overdue_stats['逾期天数>5天']}人")
        
        print(f"\n💼 工作量分析 (新评分标准：人天越多越好):")
        work_stats = stats['工作量分析']
        print(f"   平均工作人天: {work_stats['平均人天']}人天")
        print(f"   人天中位数: {work_stats['人天中位数']}人天")
        print(f"   工作量不足(<8人天): {work_stats['工作量不足(<8人天)']}人")
        print(f"   理想区间(8-10人天): {work_stats['理想区间(8-10人天)']}人")
        print(f"   优秀表现(10-15人天): {work_stats['优秀表现(10-15人天)']}人")
        print(f"   超高产出(>15人天): {work_stats['超高产出(>15人天)']}人")
        
        if stats['Highlight候选']:
            print(f"\n🌟 Highlight候选 (S级 ≥85分):")
            for name in stats['Highlight候选']:
                row = df[df['name'] == name].iloc[0]
                print(f"   • {name:<8}: {row['comprehensive_score']:>6.2f}分")
                print(f"     └─ {row['explanation']}")
        
        if stats['Lowlight需关注']:
            print(f"\n⚠️  Lowlight需关注 (D级 <40分):")
            for name in stats['Lowlight需关注']:
                row = df[df['name'] == name].iloc[0]
                print(f"   • {name:<8}: {row['comprehensive_score']:>6.2f}分")
                print(f"     └─ {row['explanation']}")
        
        if stats['需核实人天']:
            print(f"\n🔍 需核实人天记录 (>15人天):")
            review_df = df[df['needs_review'] == True].sort_values('work_days', ascending=False)
            for _, row in review_df.iterrows():
                print(f"   • {row['name']:<8}: {row['work_days']:>6.1f}人天 ({row['comprehensive_score']:.1f}分)")
                print(f"     └─ 建议核实：是否存在人天记录膨胀或重复统计")
        
        # 改进建议
        print(f"\n💡 团队改进建议:")
        if overdue_stats['平均逾期比例'] > 30:
            print("   🎯 优先解决逾期问题：平均逾期比例过高，需要优化任务规划和执行")
        if overdue_stats['平均逾期天数'] > 3:
            print("   ⚡ 加强进度管控：逾期天数偏长，建议增加里程碑检查")
        if work_stats['工作量不足(<8人天)'] > stats['总人数'] * 0.2:
            print("   📈 提升工作饱和度：部分人员工作量不足，可增加任务分配")
        if work_stats['需核实记录(>15人天)'] > 0:
            print("   🔍 核实高人天记录：建议检查超高人天的统计准确性，避免重复计算")
        if work_stats['优秀表现(10-15人天)'] > 0:
            print("   👏 表彰优秀表现：有多名同事展现出色的工作产出，值得认可")

def main():
    import os
    
    parser = argparse.ArgumentParser(description="研发团队数据处理和评分计算器 - 优化版v2.1")
    parser.add_argument("--overdue", help="逾期比例数据文件路径 (默认: data/overdue.data)")
    parser.add_argument("--mean-overdue", help="逾期天数均值数据文件路径 (默认: data/mean_overdue.data)")
    parser.add_argument("--days", help="工作人天数据文件路径 (默认: data/days.data)")
    parser.add_argument("--output", help="输出结果文件路径")
    parser.add_argument("--stats", action="store_true", help="显示统计信息")
    parser.add_argument("--detailed", action="store_true", help="显示详细分析报告")
    parser.add_argument("--explain", action="store_true", help="显示每人得分解释")
    
    args = parser.parse_args()
    
    # 设置默认数据文件路径
    data_dir = os.getenv('DATA_DIR', 'data')
    overdue_file = args.overdue or os.path.join(data_dir, 'overdue.data')
    mean_overdue_file = args.mean_overdue or os.path.join(data_dir, 'mean_overdue.data')
    days_file = args.days or os.path.join(data_dir, 'days.data')
    
    # 检查数据文件是否存在
    for file_path, name in [(overdue_file, '逾期比例'), (mean_overdue_file, '逾期天数'), (days_file, '工作人天')]:
        if not os.path.exists(file_path):
            print(f"❌ {name}数据文件不存在: {file_path}")
            print(f"💡 请将数据文件放在 {data_dir}/ 目录下，或使用 --{name.split('_')[0]} 参数指定路径")
            return
    
    try:
        # 创建数据处理器
        processor = DataProcessor()
        
        # 处理文件
        print("正在处理数据文件...")
        print("📌 使用优化版v2.1评分方案（人天越多越好）：")
        print("   • 权重：逾期比例40% + 逾期天数40% + 工作人天20%")
        print("   • 逾期比例基准：20%，超出每1%扣2分")
        print("   • 逾期天数基准：2天，超出每天扣15分")
        print("   • 工作人天评分：")
        print("     - 8-10人天：满分100分")
        print("     - 10-15人天：加分区间，每增加1人天+2分，最高110分")
        print("     - >15人天：继续加分每人天+1分，最高120分，但需核实记录")
        print("     - <8人天：减分，每少1人天-10分")
        print()
        
        result_df = processor.process_files(overdue_file, mean_overdue_file, days_file)
        
        # 显示结果
        print(f"\n=== 评分结果 (共{len(result_df)}人) ===")
        
        # 格式化输出
        display_df = result_df.copy()
        display_df["overdue_ratio"] = display_df["overdue_ratio"].apply(lambda x: f"{x:.1f}%")
        display_df["overdue_days"] = display_df["overdue_days"].apply(lambda x: f"{x:.1f}天")
        display_df["work_days"] = display_df["work_days"].apply(lambda x: f"{x:.1f}人天")
        
        # 选择要显示的列
        if args.explain:
            display_columns = ["name", "overdue_ratio", "overdue_days", "work_days", 
                             "comprehensive_score", "grade", "explanation"]
            print(display_df[display_columns].to_string(index=True, index_names=["排名"]))
        else:
            display_columns = ["name", "overdue_ratio", "overdue_days", "work_days", 
                             "comprehensive_score", "grade"]
            print(display_df[display_columns].to_string(index=True, index_names=["排名"]))
        
        # 显示详细分析
        if args.detailed:
            processor.print_detailed_analysis(result_df)
        
        # 显示统计信息
        elif args.stats:
            stats = processor.analyze_statistics(result_df)
            print(f"\n=== 统计信息 ===")
            print(f"总人数: {stats['总人数']}")
            print(f"平均得分: {stats['平均综合得分']}")
            print(f"得分中位数: {stats['得分中位数']}")
            print(f"分数区间: {stats['最低分']} - {stats['最高分']}")
            
            print(f"\n等级分布:")
            for grade, count in sorted(stats['等级分布'].items()):
                print(f"  {grade}级: {count}人")
            
            if stats['Highlight候选']:
                print(f"\nHighlight候选 (S级): {', '.join(stats['Highlight候选'])}")
            
            if stats['Lowlight需关注']:
                print(f"Lowlight需关注 (D级): {', '.join(stats['Lowlight需关注'])}")
            
            if stats['需核实人天']:
                print(f"需核实人天记录: {', '.join(stats['需核实人天'])}")
        
        # 保存结果
        if args.output:
            result_df.to_csv(args.output, index=True, index_label="排名", encoding='utf-8-sig')
            print(f"\n结果已保存到: {args.output}")
        
        # 显示前3名和后3名
        print(f"\n=== Top 3 (优秀表现) ===")
        top3 = result_df.head(3)
        for idx, row in top3.iterrows():
            review_flag = " 🔍需核实" if row['needs_review'] else ""
            print(f"{idx}. {row['name']} - {row['comprehensive_score']}分 ({row['grade']}级){review_flag}")
        
        print(f"\n=== Bottom 3 (需要改进) ===")
        bottom3 = result_df.tail(3)
        for idx, row in bottom3.iterrows():
            print(f"{idx}. {row['name']} - {row['comprehensive_score']}分 ({row['grade']}级)")
            
    except FileNotFoundError as e:
        print(f"❌ 文件未找到: {e}")
    except ValueError as e:
        print(f"❌ 数据错误: {e}")
    except Exception as e:
        print(f"❌ 处理过程中出错: {e}")

if __name__ == "__main__":
    main()
