"""
Insight Agent - generates narratives and business insights from analytics results.
"""
from datetime import datetime
from .schema import AgentState, Insight


class InsightAgent:
    """
    Transforms raw analytics data into narratives, anomalies, and recommendations.
    """
    
    def __init__(self):
        pass
    
    def process(self, state: AgentState) -> AgentState:
        """Generate insights from analytics output."""
        try:
            if not state.analytics_output or not state.analytics_output.kpis:
                state.error_messages.append("No analytics data to generate insights from.")
                return state
            
            # Build narrative summary
            summary = self._build_summary(state)
            
            # Detect anomalies
            anomalies = self._detect_anomalies(state)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(state, anomalies)
            
            # Build long-form narrative
            narrative = self._build_narrative(state, summary, anomalies)
            
            # Calculate confidence
            confidence = self._calculate_confidence(state)
            
            # Create insight object
            insight = Insight(
                summary=summary,
                narrative=narrative,
                confidence=confidence,
                anomalies=anomalies,
                recommendations=recommendations
            )
            
            state.insights = insight
            state.response_data["insight"] = {
                "summary": summary,
                "narrative": narrative,
                "confidence": confidence,
                "anomalies": anomalies,
                "recommendations": recommendations
            }
            state.updated_at = datetime.utcnow()
            return state
        
        except Exception as e:
            state.error_messages.append(f"Insight Generation Error: {str(e)}")
            return state
    
    def _build_summary(self, state: AgentState) -> str:
        """Build a bullet-point summary of key findings."""
        if not state.analytics_output or not state.analytics_output.kpis:
            return "No summary available."
        
        summary_points = []
        
        for kpi in state.analytics_output.kpis[:5]:  # Top 5 KPIs
            summary_points.append(
                f"• {kpi.metric_name}: {kpi.value:,.0f} {kpi.unit}"
            )
        
        return "\n".join(summary_points) if summary_points else "No key metrics available."
    
    def _detect_anomalies(self, state: AgentState) -> list:
        """Detect anomalies in the data."""
        anomalies = []
        
        if not state.analytics_output:
            return anomalies
        
        # Check for empty/null results
        if not state.analytics_output.raw_data:
            anomalies.append("No data available for analysis.")
            return anomalies
        
        # Check for zero values in key metrics
        for kpi in state.analytics_output.kpis:
            if kpi.value == 0 and "Total" in kpi.metric_name:
                anomalies.append(f"{kpi.metric_name} is zero - possible data gap or business issue.")
        
        # Check time series for drops
        if state.analytics_output.time_series and len(state.analytics_output.time_series) > 1:
            ts = state.analytics_output.time_series
            for i in range(1, len(ts)):
                prev_sales = ts[i-1].get("total_sales", 1)
                curr_sales = ts[i].get("total_sales", 0)
                if prev_sales > 0:
                    drop_pct = ((prev_sales - curr_sales) / prev_sales) * 100
                    if drop_pct > 20:
                        anomalies.append(
                            f"Sales dropped {drop_pct:.1f}% in {ts[i].get('week_start', 'recent period')}"
                        )
        
        # Check for high stockout rates
        for kpi in state.analytics_output.kpis:
            if "stockout" in kpi.metric_name.lower() and kpi.value > 100:
                anomalies.append(f"High stockout count detected: {int(kpi.value)} instances")
        
        return anomalies
    
    def _generate_recommendations(self, state: AgentState, anomalies: list) -> list:
        """Generate actionable recommendations."""
        recommendations = []
        
        if not state.analytics_output:
            return recommendations
        
        # Promo-specific recommendations
        promo_kpi = next(
            (kpi for kpi in state.analytics_output.kpis if "Promotional" in kpi.metric_name),
            None
        )
        if promo_kpi and promo_kpi.value > 0:
            recommendations.append(
                "Promotional units are strong. Consider expanding successful promo types."
            )
        
        # Inventory recommendations
        turn_kpi = next(
            (kpi for kpi in state.analytics_output.kpis if "Inventory" in kpi.metric_name),
            None
        )
        if turn_kpi and turn_kpi.value < 2:
            recommendations.append("Inventory turnover is low. Review stock levels and demand forecasting.")
        
        # Margin recommendations
        margin_kpi = next(
            (kpi for kpi in state.analytics_output.kpis if "Margin" in kpi.metric_name),
            None
        )
        if margin_kpi and margin_kpi.value > 0:
            recommendations.append("Gross margin is healthy. Monitor pricing strategies.")
        
        # Anomaly-driven recommendations
        if any("dropped" in a.lower() for a in anomalies):
            recommendations.append("Sales drop detected. Investigate root causes and market conditions.")
        
        if any("stockout" in a.lower() for a in anomalies):
            recommendations.append("Stockouts impacting revenue. Improve inventory replenishment.")
        
        return recommendations
    
    def _build_narrative(self, state: AgentState, summary: str, anomalies: list) -> str:
        """Build a longer-form narrative explanation."""
        narrative_parts = []
        
        # Opening
        intent = state.structured_intent.intent if state.structured_intent else "Analytics"
        narrative_parts.append(f"## {intent.replace('_', ' ').title()} Analysis\n")
        
        # Summary
        narrative_parts.append(f"**Key Metrics:**\n{summary}\n")
        
        # Anomalies
        if anomalies:
            narrative_parts.append("**Notable Findings:**")
            for anomaly in anomalies[:3]:
                narrative_parts.append(f"- {anomaly}")
            narrative_parts.append("")
        
        # Data context
        if state.analytics_output and state.analytics_output.raw_data:
            narrative_parts.append(
                f"**Data Coverage:** {len(state.analytics_output.raw_data)} records analyzed"
            )
        
        return "\n".join(narrative_parts)
    
    def _calculate_confidence(self, state: AgentState) -> float:
        """Calculate confidence score for insights."""
        confidence = 0.7  # base
        
        if state.analytics_output:
            if state.analytics_output.raw_data:
                # More data = higher confidence
                confidence += min(0.2, len(state.analytics_output.raw_data) / 1000)
            
            if state.analytics_output.kpis:
                confidence += 0.1
        
        if not state.error_messages:
            confidence += 0.1
        else:
            confidence -= 0.1 * len(state.error_messages)
        
        return max(0.0, min(1.0, confidence))  # Clamp to [0, 1]
