from supabase import create_client
import uuid
import logging
import os
import json
from datetime import datetime
from typing import Optional

QUERIES_TABLE = "diff_queries"
RESPONSES_TABLE = "diff_responses"

def to_datetime(timestamp_string):
    # Truncate the fractional seconds to ensure a valid ISO 8601 format
    return datetime.fromisoformat(timestamp_string.split('.')[0]),
    
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
    def from_json(cls, data):
        
        return cls(
            id=uuid.UUID(data["id"]),
            created_at=to_datetime(data["created_at"]),
            repo_url=data["repo_url"],
            prompt=data["prompt"],
            gpt_model=data["gpt_model"]
        )

    def __repr__(self):
        return f"<Query(id={self.id}, created_at={self.created_at}, repo_url={self.repo_url}, prompt={self.prompt}, gpt_model={self.gpt_model})>"

class DiffResponse:
    def __init__(self,
                 id: uuid.UUID = None, 
                 created_at: datetime = None, 
                 query_id: Optional[uuid.UUID] = None, 
                 diff: Optional[str] = None):
      self.id = id
      self.created_at = created_at  
      self.query_id = query_id
      self.diff = diff

    def to_dict(self):    
        return {
            "query_id": str(self.query_id) if self.query_id is not None else None,
            "diff": self.diff
        }

    @classmethod
    def from_json(cls, data):
        return cls(
            id=uuid.UUID(data["id"]),
            created_at=to_datetime(data["created_at"]),
            query_id=uuid.UUID(data["query_id"]),
            diff=data["diff"]
        )

    def __repr__(self):
        return f"<Output(id={self.id}, created_at={self.created_at}, query_id={self.query_id}, diff={self.diff})>"

class SupabaseClient:
    def __init__(self):
        self.url = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
        self.key = os.environ.get("NEXT_PUBLIC_SUPABASE_SERVICE_KEY")
        self.client = create_client(self.url, self.key)

    async def store_diff_query(self, diff_query: DiffQuery) -> DiffQuery:
      response = self.client.table(QUERIES_TABLE).insert(diff_query.to_dict()).execute()
      return DiffQuery.from_json(response.data[0])

    async def store_diff_response(self, diff_response: DiffResponse) -> (bool, DiffResponse):
        response = self.client.table(RESPONSES_TABLE).insert(diff_response.to_dict()).execute()
        return DiffResponse.from_json(response.data[0])
