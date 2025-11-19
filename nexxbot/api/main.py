"""
NEXXBot FastAPI Application
Main API endpoints for the multi-agent system
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from datetime import datetime

from ..core.config import settings
from ..core.nexxlm import NexxLM
from ..agents import (
    ConnexxAgent,
    AnnexxAgent,
    RonnexxAgent,
    VisionexxAgent,
    SalexxAgent,
    RoboAgent
)
from ..agents.base import AgentTask
from ..memory.vector_store import VectorStore

# Initialize FastAPI app
app = FastAPI(
    title="NEXXBot Supply Chain AI",
    description="Multi-Agent Agentic Workflow System for Supply Chain Management",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize core components
nexxlm_brain = None
agents_registry = {}
vector_store = None


@app.on_event("startup")
async def startup_event():
    """Initialize system on startup"""
    global nexxlm_brain, agents_registry, vector_store

    # Initialize NexxLM brain
    nexxlm_brain = NexxLM()

    # Initialize vector store
    vector_store = VectorStore(collection_name="nexxbot_knowledge")

    # Initialize all agents
    agents_registry = {
        "connexx": ConnexxAgent(),
        "annexx": AnnexxAgent(),
        "ronnexx": RonnexxAgent(),
        "visionexx": VisionexxAgent(),
        "salexx": SalexxAgent(vector_store=vector_store),
        "robo_agent": RoboAgent()
    }

    # Load sample knowledge base
    sample_sops = [
        {
            "title": "Energy Efficiency SOP",
            "content": "Monitor shuttle energy consumption daily. Investigate if deviation > 20% from average.",
            "category": "operations"
        },
        {
            "title": "Quality Control Standards",
            "content": "All food products must pass visual inspection for labeling, dates, and packaging integrity.",
            "category": "qc"
        }
    ]
    vector_store.add_sop_documents(sample_sops)

    print("NEXXBot system initialized successfully!")


# Request/Response Models
class TaskRequest(BaseModel):
    """User task request"""
    user_input: str
    context: Optional[Dict[str, Any]] = {}
    agent_id: Optional[str] = None


class TaskResponse(BaseModel):
    """Task processing response"""
    success: bool
    task_id: str
    intent: Optional[str] = None
    assigned_agent: str
    result: Any
    timestamp: str


class AgentStatusResponse(BaseModel):
    """Agent status response"""
    agent_id: str
    role: str
    state: str
    current_task: Optional[str]
    completed_tasks: int


# API Endpoints

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "NEXXBot Supply Chain AI System",
        "version": "1.0.0",
        "status": "running",
        "agents": list(agents_registry.keys())
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "agents_count": len(agents_registry)
    }


@app.post("/task", response_model=TaskResponse)
async def process_task(request: TaskRequest):
    """
    Process a task using NEXXBot's multi-agent system

    This is the main entry point for all user requests
    """
    try:
        # Step 1: Use NexxLM brain to analyze and route
        analysis = await nexxlm_brain.process(
            user_input=request.user_input,
            context=request.context
        )

        # Step 2: Get assigned agent
        agent_id = request.agent_id or analysis["assigned_agent"]
        agent = agents_registry.get(agent_id)

        if not agent:
            raise HTTPException(
                status_code=404,
                detail=f"Agent '{agent_id}' not found"
            )

        # Step 3: Create task
        task = AgentTask(
            task_id=f"TASK_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            description=request.user_input,
            context=request.context or {}
        )

        # Step 4: Execute task
        result = await agent.process_task(task)

        return TaskResponse(
            success=result["success"],
            task_id=task.task_id,
            intent=analysis.get("intent"),
            assigned_agent=agent_id,
            result=result,
            timestamp=datetime.now().isoformat()
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/agents")
async def list_agents():
    """List all available agents"""
    return {
        "agents": [
            {
                "id": agent_id,
                "role": agent.role,
                "description": agent.description
            }
            for agent_id, agent in agents_registry.items()
        ]
    }


@app.get("/agents/{agent_id}/status", response_model=AgentStatusResponse)
async def get_agent_status(agent_id: str):
    """Get status of a specific agent"""
    agent = agents_registry.get(agent_id)

    if not agent:
        raise HTTPException(
            status_code=404,
            detail=f"Agent '{agent_id}' not found"
        )

    status = agent.get_status()

    return AgentStatusResponse(
        agent_id=status["agent_id"],
        role=status["role"],
        state=status["state"],
        current_task=status["current_task"],
        completed_tasks=status["completed_tasks"]
    )


@app.post("/knowledge/add")
async def add_knowledge(
    documents: List[str],
    metadata: Optional[List[Dict]] = None
):
    """Add documents to knowledge base"""
    try:
        vector_store.add_documents(documents, metadata)
        return {
            "success": True,
            "message": f"Added {len(documents)} documents to knowledge base"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/knowledge/search")
async def search_knowledge(query: str, n_results: int = 5):
    """Search knowledge base"""
    try:
        results = vector_store.search(query, n_results)
        return {
            "success": True,
            "query": query,
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Example usage endpoints for testing

@app.post("/examples/data-analysis")
async def example_data_analysis():
    """Example: Data analysis task"""
    request = TaskRequest(
        user_input="统计本月设备耗电量，对比每层能耗差异，并分析原因",
        context={"warehouse_id": "WH001", "month": "2024-10"}
    )
    return await process_task(request)


@app.post("/examples/operations")
async def example_operations():
    """Example: Operations task (ASN creation)"""
    request = TaskRequest(
        user_input="创建入库单：供应商DELTA，商品UltraPure Hand Soap，数量8件，交货日期2024-10-05",
        context={"operation_type": "create_asn"}
    )
    return await process_task(request)


@app.post("/examples/sales")
async def example_sales():
    """Example: Sales inquiry"""
    request = TaskRequest(
        user_input="你们有适合存放食品的仓库吗？温度多少？",
        context={"channel": "whatsapp"}
    )
    return await process_task(request)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_DEBUG
    )
