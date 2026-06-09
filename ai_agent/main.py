"""
Main entry point and example usage of the FMCG BI multi-agent system.
"""
import os
from .workflow import FMCGAgentWorkflow


def main():
    """
    Run example queries through the multi-agent system.
    """
    # Resolve database path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    db_path = os.path.join(project_root, "architecture", "fmcg_analytics.db")
    
    # Initialize workflow
    workflow = FMCGAgentWorkflow(db_path=db_path)
    
    print("=" * 80)
    print("FMCG BI Multi-Agent System")
    print("=" * 80)
    print()
    
    # Example queries
    test_queries = [
        "What was the promotional performance last week?",
        "Show me regional sales comparison for the last quarter.",
        "How is inventory turnover across our stores?",
        "What's the campaign impact for our promotions?",
        "Give me a dashboard snapshot of key metrics.",
    ]
    
    for query in test_queries:
        print(f"[USER] {query}")
        print()
        
        result = workflow.process(
            user_message=query,
            user_id="analyst_001"
        )
        
        print(f"[ASSISTANT]\n{result.response_text}")
        print()
        
        # Show report if generated
        if result.report_id:
            report = workflow.report_agent.get_report(result.report_id)
            if report:
                print(f"[REPORT SUMMARY]\n{report.get('summary', 'N/A')}")
        
        print("-" * 80)
        print()


def interactive_mode():
    """
    Interactive mode - accept user input and process queries.
    """
    # Resolve database path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    db_path = os.path.join(project_root, "architecture", "fmcg_analytics.db")
    
    workflow = FMCGAgentWorkflow(db_path=db_path)
    
    print("=" * 80)
    print("FMCG BI Assistant - Interactive Mode")
    print("Type 'quit' to exit, 'history' to see conversation history")
    print("=" * 80)
    print()
    
    session_id = None
    conversation_count = 0
    
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() == "quit":
            print("Goodbye!")
            break
        
        if user_input.lower() == "history" and session_id:
            history = workflow.memory.get_conversation_history(session_id)
            print("\n[CONVERSATION HISTORY]")
            for turn in history:
                print(f"  Q: {turn.user_message[:50]}...")
                print(f"  Intent: {turn.intent}")
            print()
            continue
        
        if not user_input:
            continue
        
        # Process query
        result = workflow.process(
            user_message=user_input,
            session_id=session_id,
            user_id="interactive_user"
        )
        
        # Update session ID
        if not session_id:
            session_id = result.session_id
        
        conversation_count += 1
        
        # Display response
        print(f"\nAssistant:\n{result.response_text}\n")
        
        # Show additional context on first query
        if conversation_count == 1:
            print("Tip: Ask follow-up questions or try different queries.\n")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        interactive_mode()
    else:
        main()
