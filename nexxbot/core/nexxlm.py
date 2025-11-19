"""
NexxLM - The Brain of NEXXBot
Core orchestration layer for multi-agent system
"""

from typing import Dict, List, Any, Optional
from enum import Enum
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from .config import settings
from .logger import get_logger

logger = get_logger(__name__)


class AgentType(Enum):
    """Available agent types in the system"""
    CONNEXX = "connexx"  # Dispatch Agent - 调度中枢
    ANNEXX = "annexx"    # Data Analyst Agent - 数据分析师
    RONNEXX = "ronnexx"  # Operations Agent - 运营助理
    VISIONEXX = "visionexx"  # QC Agent - 视觉质检员
    SALEXX = "salexx"    # Sales Agent - 销售顾问
    ROBO_AGENT = "robo_agent"  # Embodied Control - 具身控制


class TaskIntent(Enum):
    """Task intent categories for routing"""
    DATA_ANALYSIS = "data_analysis"
    OPERATIONS = "operations"
    QUALITY_CONTROL = "quality_control"
    SALES_SERVICE = "sales_service"
    EMBODIED_CONTROL = "embodied_control"
    GENERAL = "general"


class NexxLM:
    """
    NexxLM - Core Brain Module

    Responsibilities:
    1. Intent Recognition - 意图识别
    2. Task Decomposition - 任务拆解
    3. Agent Routing - 智能体路由
    4. Reasoning & Reflection - 推理与反思
    """

    def __init__(self, model_name: Optional[str] = None):
        """
        Initialize NexxLM brain

        Args:
            model_name: LLM model to use (defaults to settings)
        """
        self.model_name = model_name or settings.OPENAI_MODEL
        self.llm = self._initialize_llm()
        logger.info(f"NexxLM initialized with model: {self.model_name}")

    def _initialize_llm(self) -> ChatOpenAI:
        """Initialize the base LLM"""
        return ChatOpenAI(
            model=self.model_name,
            temperature=settings.OPENAI_TEMPERATURE,
            max_tokens=settings.OPENAI_MAX_TOKENS,
            api_key=settings.OPENAI_API_KEY
        )

    async def recognize_intent(self, user_input: str, context: Optional[Dict] = None) -> TaskIntent:
        """
        Recognize user intent from natural language input

        Args:
            user_input: Natural language query from user
            context: Optional context information

        Returns:
            Recognized task intent
        """
        logger.info(f"Recognizing intent for: {user_input[:100]}...")

        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are NexxLM, the intelligent brain of NEXXBot supply chain AI system.
Your task is to analyze user queries and classify them into one of these categories:

1. DATA_ANALYSIS - Queries about statistics, reports, trends, analytics, energy consumption, performance metrics
2. OPERATIONS - Tasks involving order processing, document handling, ASN creation, inventory management
3. QUALITY_CONTROL - Visual inspection, defect detection, quality checks, compliance verification
4. SALES_SERVICE - Customer inquiries, pricing, warehouse rental, service quotations
5. EMBODIED_CONTROL - Robot control, physical manipulation, warehouse automation commands
6. GENERAL - General questions or unclear intent

Respond with ONLY the category name, nothing else."""),
            HumanMessage(content=f"User query: {user_input}\nContext: {context or 'None'}\n\nCategory:")
        ])

        response = await self.llm.ainvoke(prompt.format_messages())
        intent_str = response.content.strip().upper()

        try:
            intent = TaskIntent[intent_str]
            logger.info(f"Intent recognized: {intent.value}")
            return intent
        except KeyError:
            logger.warning(f"Unknown intent '{intent_str}', defaulting to GENERAL")
            return TaskIntent.GENERAL

    def route_to_agent(self, intent: TaskIntent) -> AgentType:
        """
        Route task to appropriate agent based on intent

        Args:
            intent: Recognized task intent

        Returns:
            Target agent type
        """
        routing_map = {
            TaskIntent.DATA_ANALYSIS: AgentType.ANNEXX,
            TaskIntent.OPERATIONS: AgentType.RONNEXX,
            TaskIntent.QUALITY_CONTROL: AgentType.VISIONEXX,
            TaskIntent.SALES_SERVICE: AgentType.SALEXX,
            TaskIntent.EMBODIED_CONTROL: AgentType.ROBO_AGENT,
            TaskIntent.GENERAL: AgentType.CONNEXX
        }

        agent = routing_map.get(intent, AgentType.CONNEXX)
        logger.info(f"Routing {intent.value} to {agent.value}")
        return agent

    async def decompose_task(
        self,
        task: str,
        intent: TaskIntent,
        context: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """
        Decompose complex task into atomic steps

        Args:
            task: Task description
            intent: Task intent
            context: Optional context

        Returns:
            List of atomic task steps
        """
        logger.info(f"Decomposing task: {task[:100]}...")

        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=f"""You are NexxLM, decomposing a {intent.value} task into atomic steps.
Break down the task into clear, executable steps. Each step should:
1. Have a clear action verb (query, analyze, create, send, etc.)
2. Specify required tools or APIs
3. Define expected output

Format your response as a numbered list of steps."""),
            HumanMessage(content=f"Task: {task}\nContext: {context or 'None'}\n\nDecomposed steps:")
        ])

        response = await self.llm.ainvoke(prompt.format_messages())
        steps_text = response.content.strip()

        # Parse steps (simplified version)
        steps = []
        for line in steps_text.split('\n'):
            line = line.strip()
            if line and line[0].isdigit():
                steps.append({
                    "description": line,
                    "status": "pending"
                })

        logger.info(f"Task decomposed into {len(steps)} steps")
        return steps

    async def reason_and_reflect(
        self,
        observation: str,
        history: List[Dict],
        goal: str
    ) -> Dict[str, Any]:
        """
        Perform reasoning and reflection on observations

        Args:
            observation: Current observation or result
            history: Execution history
            goal: Original goal

        Returns:
            Reasoning result with next action recommendation
        """
        logger.info("Performing reasoning and reflection...")

        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are NexxLM, analyzing execution results and reasoning about next steps.
Consider:
1. What does this observation tell us?
2. Are we making progress toward the goal?
3. What anomalies or issues exist?
4. What should be the next action?
5. Do we need to adjust our approach?

Provide structured reasoning."""),
            HumanMessage(content=f"""
Goal: {goal}
Current Observation: {observation}
Execution History: {history}

Analysis:""")
        ])

        response = await self.llm.ainvoke(prompt.format_messages())

        return {
            "reasoning": response.content,
            "confidence": 0.8,  # Could be calculated from response
            "next_action": "continue"  # continue, adjust, or complete
        }

    async def process(
        self,
        user_input: str,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Main processing pipeline

        Args:
            user_input: User's natural language input
            context: Optional context (local warehouse data, etc.)

        Returns:
            Processing result with agent assignment and task breakdown
        """
        logger.info("=" * 80)
        logger.info(f"NexxLM processing: {user_input}")
        logger.info("=" * 80)

        # Step 1: Recognize Intent
        intent = await self.recognize_intent(user_input, context)

        # Step 2: Route to Agent
        agent = self.route_to_agent(intent)

        # Step 3: Decompose Task
        steps = await self.decompose_task(user_input, intent, context)

        result = {
            "user_input": user_input,
            "intent": intent.value,
            "assigned_agent": agent.value,
            "task_steps": steps,
            "context": context or {},
            "status": "ready_for_execution"
        }

        logger.info(f"Task prepared for agent: {agent.value}")
        return result


# Example usage and testing
if __name__ == "__main__":
    import asyncio

    async def test_nexxlm():
        brain = NexxLM()

        # Test 1: Data Analysis Intent
        result = await brain.process(
            "统计本月设备耗电量，对比每层能耗差异，并分析原因",
            context={"warehouse_id": "WH001", "month": "2024-10"}
        )
        print("\nTest 1 - Data Analysis:")
        print(f"Intent: {result['intent']}")
        print(f"Agent: {result['assigned_agent']}")
        print(f"Steps: {len(result['task_steps'])}")

        # Test 2: Operations Intent
        result = await brain.process(
            "处理这份订单图片，创建ASN入库单",
            context={"document_type": "order_image"}
        )
        print("\nTest 2 - Operations:")
        print(f"Intent: {result['intent']}")
        print(f"Agent: {result['assigned_agent']}")

    asyncio.run(test_nexxlm())
