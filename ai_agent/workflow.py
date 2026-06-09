"""
LangGraph Workflow - orchestrates multi-agent execution.
"""
from typing import Callable
from datetime import datetime
from langgraph.graph import StateGraph

from .schema import AgentState
from .query_agent import QueryUnderstandingAgent
from .sql_agent import SQLGenerationAgent
from .analytics_agent import AnalyticsAgent
from .insight_agent import InsightAgent
from .visualization_agent import VisualizationAgent
from .report_agent import ReportAgent
from .memory import MemoryManager, ConversationTurn


class FMCGAgentWorkflow:
    """
    LangGraph-based multi-agent orchestrator for FMCG BI.
    """
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or "architecture/fmcg_analytics.db"
        
        # Initialize agents
        self.query_agent = QueryUnderstandingAgent()
        self.sql_agent = SQLGenerationAgent()
        self.analytics_agent = AnalyticsAgent(db_path=self.db_path)
        self.insight_agent = InsightAgent()
        self.visualization_agent = VisualizationAgent()
        self.report_agent = ReportAgent()
        
        # Initialize memory
        self.memory = MemoryManager()
        
        # Build LangGraph
        self.graph = self._build_graph()
    
    def _build_graph(self):
        """Construct the LangGraph workflow."""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("query_understanding", self._node_query_understanding)
        workflow.add_node("clarification", self._node_clarification)
        workflow.add_node("sql_generation", self._node_sql_generation)
        workflow.add_node("sql_validation", self._node_sql_validation)
        workflow.add_node("analytics_execution", self._node_analytics_execution)
        workflow.add_node("insight_generation", self._node_insight_generation)
        workflow.add_node("visualization_generation", self._node_visualization_generation)
        workflow.add_node("report_generation", self._node_report_generation)
        workflow.add_node("response_assembly", self._node_response_assembly)
        
        # Set entry point
        workflow.set_entry_point("query_understanding")
        
        # Define edges (sequential flow)
        workflow.add_conditional_edges(
            "query_understanding",
            self._route_after_query_understanding,
            {
                "clarification": "clarification",
                "sql_generation": "sql_generation"
            }
        )
        
        workflow.add_edge("clarification", "response_assembly")
        workflow.add_edge("sql_generation", "sql_validation")
        
        workflow.add_conditional_edges(
            "sql_validation",
            self._route_after_sql_validation,
            {
                "fallback": "response_assembly",
                "analytics": "analytics_execution"
            }
        )
        
        # Sequential: analytics -> insight -> viz -> report -> response
        workflow.add_edge("analytics_execution", "insight_generation")
        workflow.add_edge("insight_generation", "visualization_generation")
        workflow.add_edge("visualization_generation", "report_generation")
        workflow.add_edge("report_generation", "response_assembly")
        
        # End point
        workflow.set_finish_point("response_assembly")
        
        return workflow.compile()
    
    def _node_query_understanding(self, state: AgentState) -> AgentState:
        """Query Understanding node."""
        return self.query_agent.process(state)
    
    def _node_clarification(self, state: AgentState) -> AgentState:
        """Clarification node - ask user for more info."""
        state.response_text = (
            f"I need more information:\n{state.clarification_question}\n\n"
            "Please provide the missing details."
        )
        return state
    
    def _node_sql_generation(self, state: AgentState) -> AgentState:
        """SQL Generation node."""
        return self.sql_agent.process(state)
    
    def _node_sql_validation(self, state: AgentState) -> AgentState:
        """SQL validation and cost checking."""
        # This is handled in sql_agent, but we can add additional validation here
        if state.sql_query and state.sql_query.estimated_cost > 10:
            state.error_messages.append(
                f"Query cost is high ({state.sql_query.estimated_cost:.1f}). "
                "Consider narrowing the scope."
            )
        return state
    
    def _node_analytics_execution(self, state: AgentState) -> AgentState:
        """Analytics execution node."""
        return self.analytics_agent.process(state)
    
    def _node_insight_generation(self, state: AgentState) -> AgentState:
        """Insight generation node."""
        return self.insight_agent.process(state)
    
    def _node_visualization_generation(self, state: AgentState) -> AgentState:
        """Visualization generation node."""
        return self.visualization_agent.process(state)
    
    def _node_report_generation(self, state: AgentState) -> AgentState:
        """Report generation node."""
        return self.report_agent.process(state)
    
    def _node_response_assembly(self, state: AgentState) -> AgentState:
        """Assemble final response."""
        state.response_text = self._assemble_response(state)
        state.updated_at = datetime.utcnow()
        
        # Store in conversation memory
        turn = ConversationTurn(
            turn_id=state.turn_id,
            session_id=state.session_id,
            user_message=state.user_message,
            intent=state.structured_intent.intent if state.structured_intent else None,
            sql_query=state.sql_query.text if state.sql_query else None,
            result_summary=state.response_text[:200] if state.response_text else "",
            kpis={
                kpi.metric_name: kpi.value
                for kpi in (state.analytics_output.kpis if state.analytics_output else [])
            },
            generated_report_id=state.report_id
        )
        self.memory.add_conversation_turn(state.session_id, turn)
        
        return state
    
    def _assemble_response(self, state: AgentState) -> str:
        """Build final response text."""
        parts = []
        
        # Errors
        if state.error_messages:
            parts.append(f"⚠️ Issues: {'; '.join(state.error_messages[:2])}\n")
        
        # Insights
        if state.insights:
            parts.append(f"📊 **Insights:**\n{state.insights.summary}\n")
        
        # KPIs
        if state.analytics_output and state.analytics_output.kpis:
            parts.append("📈 **Key Metrics:**")
            for kpi in state.analytics_output.kpis[:5]:
                parts.append(f"  • {kpi.metric_name}: {kpi.value:,.0f} {kpi.unit}")
            parts.append("")
        
        # Recommendations
        if state.insights and state.insights.recommendations:
            parts.append("💡 **Recommended Actions:**")
            for rec in state.insights.recommendations[:3]:
                parts.append(f"  • {rec}")
        
        # Report ID
        if state.report_id:
            parts.append(f"\n📄 Report ID: {state.report_id}")
        
        return "\n".join(parts) if parts else "No data available for this query."
    
    def _route_after_query_understanding(self, state: AgentState) -> str:
        """Route based on query understanding result."""
        if state.requires_clarification:
            return "clarification"
        return "sql_generation"
    
    def _route_after_sql_validation(self, state: AgentState) -> str:
        """Route based on SQL validation result."""
        if state.sql_query and not state.sql_query.safe:
            return "fallback"
        return "analytics"
    
    def process(self, user_message: str, session_id: str = None, user_id: str = None) -> AgentState:
        """
        Main entry point - process a user message through the workflow.
        
        Args:
            user_message: User query
            session_id: Session identifier (auto-generated if None)
            user_id: User identifier
        
        Returns:
            Final AgentState with all processing results
        """
        # Create or retrieve session
        if session_id:
            session = self.memory.get_session(session_id)
        else:
            session = None
        
        if not session:
            session_id = session_id or str(__import__('uuid').uuid4())
            self.memory.create_session(session_id, user_id)
        
        # Initialize state
        state = AgentState(
            session_id=session_id,
            user_id=user_id,
            user_message=user_message,
            conversation_history=[],
        )
        
        # Execute workflow
        try:
            result = self.graph.invoke(state)
            
            # Handle result - could be dict or AgentState
            if isinstance(result, dict):
                # Reconstruct state from dict
                final_state = AgentState(**result)
            else:
                final_state = result
            
            return final_state
        except Exception as e:
            state.error_messages.append(f"Workflow Error: {str(e)}")
            state.response_text = f"An error occurred: {str(e)}"
            return state
