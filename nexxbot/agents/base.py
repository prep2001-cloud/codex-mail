"""
Base Agent class - Foundation for all NEXXBot agents
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from langchain_openai import ChatOpenAI
from ..core.config import settings
from ..core.logger import get_logger
from ..memory.memory_stream import MemoryStream, MemoryType
from ..tools.base import ToolRegistry

logger = get_logger(__name__)


class AgentState(Enum):
    """Agent execution states"""
    IDLE = "idle"
    THINKING = "thinking"
    EXECUTING = "executing"
    WAITING = "waiting"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class AgentTask:
    """Task assigned to an agent"""
    task_id: str
    description: str
    context: Dict[str, Any] = field(default_factory=dict)
    steps: List[Dict] = field(default_factory=list)
    current_step: int = 0
    status: str = "pending"
    result: Optional[Any] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


class BaseAgent(ABC):
    """
    Base Agent Class

    All specialized agents inherit from this class
    Implements the core Agentic Workflow:
    1. Perception - 感知
    2. Planning - 规划
    3. Execution - 执行
    4. Reasoning & Reflection - 推理与反思
    """

    def __init__(
        self,
        agent_id: str,
        role: str,
        description: str,
        tools: Optional[ToolRegistry] = None
    ):
        """
        Initialize base agent

        Args:
            agent_id: Unique agent identifier
            role: Agent role/name
            description: Agent description and capabilities
            tools: Tool registry for this agent
        """
        self.agent_id = agent_id
        self.role = role
        self.description = description
        self.state = AgentState.IDLE

        # Core components
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=settings.OPENAI_TEMPERATURE,
            api_key=settings.OPENAI_API_KEY
        )
        self.memory = MemoryStream(agent_id=agent_id)
        self.tools = tools or ToolRegistry()

        # Task management
        self.current_task: Optional[AgentTask] = None
        self.task_history: List[AgentTask] = []

        logger.info(f"Agent initialized: {self.agent_id} ({self.role})")

    @abstractmethod
    async def perceive(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perceive and understand input

        Args:
            input_data: Raw input data

        Returns:
            Processed perception
        """
        pass

    @abstractmethod
    async def plan(self, perception: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Create execution plan

        Args:
            perception: Processed perception

        Returns:
            List of planned steps
        """
        pass

    @abstractmethod
    async def execute_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single step

        Args:
            step: Step to execute

        Returns:
            Execution result
        """
        pass

    async def reason(
        self,
        observation: str,
        goal: str
    ) -> Dict[str, Any]:
        """
        Reason about observations and determine next action

        Args:
            observation: Current observation
            goal: Current goal

        Returns:
            Reasoning result
        """
        from langchain.prompts import ChatPromptTemplate
        from langchain.schema import HumanMessage, SystemMessage

        context = self.memory.get_context_window(n=5)

        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=f"""You are {self.role}, a specialized AI agent.
Your role: {self.description}

Analyze the current situation and provide reasoning about:
1. What does this observation mean?
2. Are we progressing toward the goal?
3. What should be the next action?
4. Any concerns or issues?"""),
            HumanMessage(content=f"""
Goal: {goal}
Observation: {observation}
Recent Context: {context}

Provide structured reasoning:""")
        ])

        response = await self.llm.ainvoke(prompt.format_messages())

        reasoning = {
            "analysis": response.content,
            "timestamp": datetime.now().isoformat(),
            "confidence": 0.8
        }

        # Store in memory
        self.memory.add(
            f"Reasoning: {response.content}",
            MemoryType.SHORT_TERM,
            importance=0.7
        )

        return reasoning

    async def process_task(self, task: AgentTask) -> Dict[str, Any]:
        """
        Main task processing pipeline

        Args:
            task: Task to process

        Returns:
            Task result
        """
        logger.info(f"[{self.agent_id}] Processing task: {task.task_id}")
        self.current_task = task
        self.state = AgentState.THINKING

        try:
            # Step 1: Perceive
            perception = await self.perceive(task.context)
            self.memory.add(
                f"Task: {task.description}",
                MemoryType.SHORT_TERM,
                importance=0.9
            )

            # Step 2: Plan
            self.state = AgentState.EXECUTING
            steps = await self.plan(perception)
            task.steps = steps

            # Step 3: Execute steps
            results = []
            for i, step in enumerate(steps):
                task.current_step = i
                logger.info(f"[{self.agent_id}] Executing step {i+1}/{len(steps)}")

                result = await self.execute_step(step)
                results.append(result)

                # Reason about result
                if i < len(steps) - 1:  # Not last step
                    reasoning = await self.reason(
                        observation=str(result),
                        goal=task.description
                    )

            # Complete task
            task.status = "completed"
            task.result = results
            task.updated_at = datetime.now()
            self.state = AgentState.COMPLETED

            # Store in history
            self.task_history.append(task)
            self.memory.add(
                f"Completed task: {task.description}",
                MemoryType.LONG_TERM,
                importance=0.8
            )

            logger.info(f"[{self.agent_id}] Task completed: {task.task_id}")

            return {
                "success": True,
                "task_id": task.task_id,
                "results": results,
                "agent_id": self.agent_id
            }

        except Exception as e:
            logger.error(f"[{self.agent_id}] Task failed: {str(e)}")
            self.state = AgentState.ERROR
            task.status = "failed"
            task.result = {"error": str(e)}

            return {
                "success": False,
                "task_id": task.task_id,
                "error": str(e),
                "agent_id": self.agent_id
            }

    def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            "agent_id": self.agent_id,
            "role": self.role,
            "state": self.state.value,
            "current_task": self.current_task.task_id if self.current_task else None,
            "completed_tasks": len(self.task_history),
            "memory_stats": self.memory.get_stats(),
            "available_tools": self.tools.list_tools()
        }
