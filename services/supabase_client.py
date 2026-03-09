import logging
import datetime
from typing import Dict, Any, Optional
from core.config import settings

# Guard the supabase import — the package is optional for local/stateless mode
try:
    from supabase import create_client, Client
    HAS_SUPABASE = True
except ImportError:
    HAS_SUPABASE = False
    Client = None  # type: ignore

logger = logging.getLogger(__name__)

class SupabaseClient:
    def __init__(self):
        self.client: Optional[Any] = None
        self.enabled = False
        
        if not HAS_SUPABASE:
            logger.warning("Supabase package not installed. Running in stateless mode (no DB saving).")
            return
        
        url = settings.supabase_url
        key = settings.supabase_key
        
        if url and key:
            try:
                self.client = create_client(url, key)
                self.enabled = True
                logger.info("Supabase client initialized successfully.")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase client: {e}")
        else:
            logger.warning("Supabase URL or Key not set. Running in stateless mode (no DB saving).")

    def save_raw_json(self, sku_id: str, payload: Dict[str, Any], processed_data: Dict[str, Any] = None) -> bool:
        """
        Saves the raw JSON payload and the structured processed data to Supabase.
        Returns True if successful, False otherwise.
        """
        if not self.enabled or not self.client:
            return False
            
        try:
            timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
            
            data_to_insert = {
                "sku_id": sku_id,
                "created_at": timestamp,
                "raw_payload": payload,
                "processed_data": processed_data or {}
            }
            
            # Assuming a table named 'sku_history' exists. 
            response = self.client.table("sku_history").insert(data_to_insert).execute()
            logger.info(f"Successfully saved tracking data for SKU: {sku_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving data to Supabase for SKU {sku_id}: {e}", exc_info=True)
            return False
