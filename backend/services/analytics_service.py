"""
Analytics service - handles data queries and analysis.
"""
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from sqlalchemy.orm import Session
import json

from database.models import CacheModel, SessionModel
from schemas.schemas import AnalyticsRequest, AnalyticsResponse, KPIResult

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service for analytics queries and caching."""
    
    @staticmethod
    def get_cached_result(
        db: Session,
        user_id: str,
        cache_key: str
    ) -> Optional[Dict]:
        """Retrieve cached analytics result if not expired."""
        
        cache = db.query(CacheModel).filter(
            CacheModel.cache_key == cache_key,
            CacheModel.user_id == user_id,
            CacheModel.expires_at > datetime.utcnow()
        ).first()
        
        if cache:
            # Update hit count
            cache.hit_count += 1
            db.commit()
            logger.info(f"Cache hit for {cache_key}")
            return cache.result
        
        return None
    
    @staticmethod
    def cache_result(
        db: Session,
        user_id: str,
        cache_key: str,
        result: Dict,
        ttl_seconds: int = 3600
    ) -> None:
        """Cache analytics result."""
        
        from datetime import timedelta
        
        expires_at = datetime.utcnow() + timedelta(seconds=ttl_seconds)
        
        cache = CacheModel(
            cache_key=cache_key,
            user_id=user_id,
            result=result,
            expires_at=expires_at
        )
        
        db.add(cache)
        db.commit()
        logger.info(f"Cached result for {cache_key}")
    
    @staticmethod
    def generate_cache_key(
        query: str,
        time_range: Optional[Dict] = None,
        filters: Optional[Dict] = None
    ) -> str:
        """Generate deterministic cache key."""
        
        import hashlib
        
        key_parts = [query]
        if time_range:
            key_parts.append(json.dumps(time_range, sort_keys=True))
        if filters:
            key_parts.append(json.dumps(filters, sort_keys=True))
        
        key_str = "|".join(key_parts)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    @staticmethod
    def execute_analytics(
        db: Session,
        user_id: str,
        request: AnalyticsRequest,
        workflow: Any  # FMCGAgentWorkflow
    ) -> AnalyticsResponse:
        """
        Execute analytics query through AI workflow or cache.
        """
        
        # Generate cache key
        cache_key = AnalyticsService.generate_cache_key(
            request.query,
            request.time_range,
            request.filters
        )
        
        # Check cache
        cached_result = AnalyticsService.get_cached_result(db, user_id, cache_key)
        if cached_result:
            return AnalyticsResponse(**cached_result)
        
        # Execute through AI workflow
        try:
            ai_result = workflow.process(
                user_message=request.query,
                user_id=user_id
            )
            
            if not ai_result:
                return AnalyticsResponse(
                    query=request.query,
                    kpis=[],
                    error="AI workflow failed"
                )
            
            # Extract KPIs
            kpis = []
            if ai_result.response_data.get("kpis"):
                for k in ai_result.response_data["kpis"]:
                    kpis.append(KPIResult(
                        metric_name=k.get("metric_name", ""),
                        value=k.get("value"),
                        unit=k.get("unit"),
                        dimensions=k.get("dimensions")
                    ))
            
            # Build response
            response = AnalyticsResponse(
                query=request.query,
                kpis=kpis,
                time_series=ai_result.response_data.get("time_series"),
                aggregations=ai_result.response_data.get("aggregations"),
                raw_data=ai_result.response_data.get("raw_data"),
                error=None
            )
            
            # Cache result
            AnalyticsService.cache_result(
                db, user_id, cache_key,
                response.dict(),
                ttl_seconds=3600
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Analytics execution error: {str(e)}")
            return AnalyticsResponse(
                query=request.query,
                kpis=[],
                error=str(e)
            )
    
    @staticmethod
    def get_dashboard_snapshot(
        db: Session,
        user_id: str,
        session_id: Optional[str] = None,
        workflow: Optional[Any] = None
    ) -> Dict:
        """
        Get overall dashboard metrics snapshot.
        """
        
        try:
            if workflow:
                # Use AI workflow for latest data
                result = workflow.process(
                    user_message="Give me a dashboard snapshot of key metrics.",
                    user_id=user_id,
                    session_id=session_id
                )
                
                kpis = result.response_data.get("kpis", [])
            else:
                kpis = []
            
            dashboard = {
                "total_queries": db.query(CacheModel).filter(
                    CacheModel.user_id == user_id
                ).count(),
                "cache_hits": sum(
                    c.hit_count for c in db.query(CacheModel).filter(
                        CacheModel.user_id == user_id
                    ).all()
                ),
                "kpis": kpis,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return dashboard
            
        except Exception as e:
            logger.error(f"Dashboard snapshot error: {str(e)}")
            return {
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    @staticmethod
    def get_trends(
        db: Session,
        user_id: str,
        metric_name: str,
        days: int = 30
    ) -> List[Dict]:
        """
        Get historical trends for a metric from cache.
        """
        
        # This would require storing time-series data
        # For now, return empty
        return []
