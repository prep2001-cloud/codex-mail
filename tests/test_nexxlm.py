"""
Test NexxLM core brain module
"""

import pytest
from nexxbot.core.nexxlm import NexxLM, TaskIntent, AgentType


@pytest.mark.asyncio
async def test_intent_recognition():
    """Test intent recognition"""
    brain = NexxLM()

    # Test data analysis intent
    intent = await brain.recognize_intent(
        "统计本月设备耗电量",
        context={}
    )
    assert intent in [TaskIntent.DATA_ANALYSIS, TaskIntent.GENERAL]


@pytest.mark.asyncio
async def test_agent_routing():
    """Test agent routing"""
    brain = NexxLM()

    # Test routing for different intents
    agent = brain.route_to_agent(TaskIntent.DATA_ANALYSIS)
    assert agent == AgentType.ANNEXX

    agent = brain.route_to_agent(TaskIntent.SALES_SERVICE)
    assert agent == AgentType.SALEXX


@pytest.mark.asyncio
async def test_task_decomposition():
    """Test task decomposition"""
    brain = NexxLM()

    steps = await brain.decompose_task(
        task="分析设备能耗",
        intent=TaskIntent.DATA_ANALYSIS
    )

    assert isinstance(steps, list)
    assert len(steps) > 0
