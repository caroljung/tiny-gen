from supabase import create_client
import uuid
import logging
import os
import json
from datetime import datetime
from typing import Optional

QUERIES_TABLE = "diff_queries"
RESPONSES_TABLE = "diff_responses"
    
class DiffQuery:
    def __init__(self,
                 id: uuid.UUID = None, 
                 created_at: datetime = None, 
                 repo_url: Optional[str] = None, 
                 prompt: Optional[str] = None, 
                 gpt_model: Optional[str] = None):
        self.id = id 
        self.created_at = created_at  
        self.repo_url = repo_url
        self.prompt = prompt
        self.gpt_model = gpt_model
        
    def to_dict(self):
        return {
            "repo_url": self.repo_url,
            "prompt": self.prompt,
            "gpt_model": self.gpt_model
        }

    @classmethod
    def from_json(cls, json_data):
        if isinstance(json_data, str):
            data = json.loads(json_data)
        else:
            data = json_data
            
        logger = logging.getLogger(__name__)
        logger.error(json_data)
        logger.error(data)

        return cls(
            id=uuid.UUID(data["id"]) if data.get("id") else None,
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
            repo_url=data.get("repo_url"),
            prompt=data.get("prompt"),
            gpt_model=data.get("gpt_model")
        )

    def __repr__(self):
        return f"<Query(id={self.id}, created_at={self.created_at}, repo_url={self.repo_url}, prompt={self.prompt}, gpt_model={self.gpt_model})>"

class DiffResponse:
    def __init__(self,
                 id: uuid.UUID = None, 
                 created_at: datetime = None, 
                 query_id: Optional[uuid.UUID] = None, 
                 diff: Optional[str] = None, 
                 reflection_count: Optional[int] = None):
      self.id = id
      self.created_at = created_at  
      self.query_id = query_id
      self.diff = diff
      self.reflection_count = reflection_count

    def to_dict(self):
        logger = logging.getLogger(__name__)
        logger.error(self.query_id)
        logger.error(str(self.query_id))
    
        return {
            "query_id": str(self.query_id) if self.query_id is not None else None,
            "diff": self.diff,
            "reflection_count": self.reflection_count
        }

    @classmethod
    def from_json(cls, json_data):
        if isinstance(json_data, str):
            data = json.loads(json_data)
        else:
            data = json_data

        return cls(
            id=uuid.UUID(data["id"]) if data.get("id") else None,
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
            query_id=uuid.UUID(data["query_id"]) if data.get("query_id") else None,
            diff=data.get("diff"),
            reflection_count=data.get("reflection_count")
        )

    def __repr__(self):
        return f"<Output(id={self.id}, created_at={self.created_at}, query_id={self.query_id}, diff={self.diff}, reflection_count={self.reflection_count})>"

class SupabaseClient:
    def __init__(self):
        self.url = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
        self.key = os.environ.get("NEXT_PUBLIC_SUPABASE_SERVICE_KEY")
        self.client = create_client(self.url, self.key)

    def store_diff_query(self, diff_query: DiffQuery) -> DiffQuery:
      response = self.client.table(QUERIES_TABLE).insert(diff_query.to_dict()).execute()
      return DiffQuery.from_json(response.data[0])

    def store_diff_response(self, diff_response: DiffResponse) -> (bool, DiffResponse):
        response = self.client.table(RESPONSES_TABLE).insert(diff_response.to_dict()).execute()
        return DiffResponse.from_json(response.data[0])
