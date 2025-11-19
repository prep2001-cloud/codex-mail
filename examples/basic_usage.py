"""
NEXXBot 基础使用示例
演示如何使用各个智能体完成不同任务
"""

import asyncio
from nexxbot.core.nexxlm import NexxLM
from nexxbot.agents import AnnexxAgent, RonnexxAgent, SalexxAgent
from nexxbot.agents.base import AgentTask
from datetime import datetime


async def example_1_data_analysis():
    """
    示例 1: 数据分析
    场景：分析设备能耗，检测异常，给出优化建议
    """
    print("\n" + "="*80)
    print("示例 1: 智能化数据分析")
    print("="*80)

    # 初始化 Annexx 数据分析师
    annexx = AnnexxAgent()

    # 创建任务
    task = AgentTask(
        task_id="TASK_001",
        description="统计本月设备耗电量，对比每层能耗差异，并分析原因",
        context={
            "warehouse_id": "WH001",
            "month": "2024-10",
            "user_input": "统计本月设备耗电量，对比每层能耗差异，并分析原因"
        }
    )

    # 执行任务
    result = await annexx.process_task(task)

    print(f"\n✅ 任务完成！")
    print(f"任务ID: {result['task_id']}")
    print(f"执行结果:")
    for i, step_result in enumerate(result['results'], 1):
        print(f"  步骤 {i}: {step_result}")


async def example_2_operations():
    """
    示例 2: 运营自动化
    场景：处理订单文档，自动创建 ASN
    """
    print("\n" + "="*80)
    print("示例 2: 运营自动化（ASN 创建）")
    print("="*80)

    # 初始化 Ronnexx 运营助理
    ronnexx = RonnexxAgent()

    # 创建任务
    task = AgentTask(
        task_id="TASK_002",
        description="处理订单文档，创建ASN入库单",
        context={
            "operation_type": "create_asn",
            "document": "order_image.jpg",
            "user_input": "处理这份订单图片，创建ASN入库单"
        }
    )

    # 执行任务
    result = await ronnexx.process_task(task)

    print(f"\n✅ 任务完成！")
    print(f"任务ID: {result['task_id']}")
    print(f"执行结果:")
    for i, step_result in enumerate(result['results'], 1):
        print(f"  步骤 {i}: {step_result}")


async def example_3_sales():
    """
    示例 3: 客户服务
    场景：回答客户咨询，提供仓库信息和报价
    """
    print("\n" + "="*80)
    print("示例 3: 客户服务与销售")
    print("="*80)

    # 初始化 Salexx 销售顾问
    salexx = SalexxAgent()

    # 创建任务
    task = AgentTask(
        task_id="TASK_003",
        description="回答客户关于仓库的咨询",
        context={
            "channel": "whatsapp",
            "customer_id": "CUST001",
            "user_input": "你们有适合存放食品的仓库吗？温度多少？"
        }
    )

    # 执行任务
    result = await salexx.process_task(task)

    print(f"\n✅ 任务完成！")
    print(f"任务ID: {result['task_id']}")
    print(f"执行结果:")
    for i, step_result in enumerate(result['results'], 1):
        print(f"  步骤 {i}:")
        if isinstance(step_result, dict) and 'response' in step_result:
            print(f"  客户回复:\n{step_result['response']}")


async def example_4_nexxlm_orchestration():
    """
    示例 4: NexxLM 智能编排
    场景：使用核心大脑自动识别意图并路由到合适的智能体
    """
    print("\n" + "="*80)
    print("示例 4: NexxLM 智能编排")
    print("="*80)

    # 初始化 NexxLM 大脑
    brain = NexxLM()

    # 测试不同类型的请求
    test_cases = [
        {
            "input": "分析上周的出库效率",
            "context": {"warehouse_id": "WH001"}
        },
        {
            "input": "处理这份入库单据",
            "context": {"document": "asn_doc.pdf"}
        },
        {
            "input": "客户询问冷链仓储价格",
            "context": {"channel": "wechat"}
        }
    ]

    for i, test in enumerate(test_cases, 1):
        print(f"\n测试案例 {i}: {test['input']}")
        result = await brain.process(
            user_input=test['input'],
            context=test['context']
        )

        print(f"  识别意图: {result['intent']}")
        print(f"  分配智能体: {result['assigned_agent']}")
        print(f"  任务步骤: {len(result['task_steps'])} 步")


async def example_5_memory_system():
    """
    示例 5: 记忆系统
    场景：演示智能体如何使用记忆系统
    """
    print("\n" + "="*80)
    print("示例 5: 记忆系统")
    print("="*80)

    from nexxbot.memory.memory_stream import MemoryStream, MemoryType

    # 创建记忆流
    memory = MemoryStream(agent_id="test_agent")

    # 添加短期记忆
    memory.add("用户询问能耗数据", MemoryType.SHORT_TERM, importance=0.8)
    memory.add("查询数据库获取10月数据", MemoryType.SHORT_TERM, importance=0.7)
    memory.add("发现异常：1704号车能耗高23%", MemoryType.SHORT_TERM, importance=0.9)

    # 添加长期记忆（SOP）
    memory.add(
        "SOP: 能耗偏差超过20%需要调查",
        MemoryType.LONG_TERM,
        importance=0.95
    )

    # 获取最近的记忆
    recent = memory.get_recent(n=3)
    print("\n最近的记忆:")
    for mem in recent:
        print(f"  [{mem.memory_type.value}] {mem.content} (重要性: {mem.importance})")

    # 搜索记忆
    search_results = memory.search("能耗", n=2)
    print("\n搜索'能耗'的结果:")
    for mem in search_results:
        print(f"  - {mem.content}")

    # 获取上下文窗口
    context = memory.get_context_window(n=5)
    print("\n上下文窗口:")
    print(context)

    # 统计信息
    stats = memory.get_stats()
    print(f"\n记忆统计:")
    print(f"  短期记忆: {stats['short_term_count']}")
    print(f"  长期记忆: {stats['long_term_count']}")
    print(f"  平均重要性: {stats['avg_importance']:.2f}")


async def main():
    """运行所有示例"""
    print("\n" + "🚀"*40)
    print("NEXXBot 供应链 AI 系统 - 使用示例")
    print("🚀"*40)

    try:
        # 运行示例
        await example_1_data_analysis()
        await example_2_operations()
        await example_3_sales()
        await example_4_nexxlm_orchestration()
        await example_5_memory_system()

        print("\n" + "✅"*40)
        print("所有示例执行完成！")
        print("✅"*40 + "\n")

    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
