from app.erp.demo_adapter import DemoERPAdapter
from app.erp.service import ERPService


def get_erp_service() -> ERPService:
    return ERPService(DemoERPAdapter())