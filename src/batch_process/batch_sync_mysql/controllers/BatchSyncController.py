from services.BatchSyncService import BatchSyncService

from utils.LogConfig import get_logger
class BatchSyncController:
    def __init__(self) -> None:
        self.__logger = get_logger('BatchSyncController')
        self.__batch_sync_service = BatchSyncService()
        
    def batch_sync(self):
        self.__logger.info('Begin batch sync.')
        tables = ['sales_pipeline', 'accounts', 'products', 'sales_teams']
        
        for table in tables:
            self.__batch_sync_service.batch_sync_service(table)
        
        self.__logger.info('End batch sync.')
        