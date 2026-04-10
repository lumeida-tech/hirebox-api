from litestar import Controller, get, post, patch, delete
from litestar.di import Provide
from litestar.params import Parameter

from features.companies.schemas import CompanyCreateRequest, CompanyUpdateRequest, CompanyResponse
from features.companies.service import CompanyService


def provide_company_service() -> CompanyService:
    return CompanyService()


class CompanyController(Controller):
    path = "/companies"
    tags = ["Companies"]
    dependencies = {"company_service": Provide(provide_company_service, sync_to_thread=False)}

    @get("/")
    async def list_companies(
        self,
        company_service: CompanyService,
        page: int = Parameter(default=1, ge=1),
        page_size: int = Parameter(default=20, ge=1, le=100),
    ) -> list[CompanyResponse]:
        return await company_service.list_companies(page=page, page_size=page_size)

    @get("/{company_id:str}")
    async def get_company(self, company_id: str, company_service: CompanyService) -> CompanyResponse:
        return await company_service.get_company(company_id)

    @post("/")
    async def create_company(self, data: CompanyCreateRequest, company_service: CompanyService) -> CompanyResponse:
        # TODO: extract owner_id from current_user
        return await company_service.create_company(data, owner_id="")

    @patch("/{company_id:str}")
    async def update_company(
        self, company_id: str, data: CompanyUpdateRequest, company_service: CompanyService
    ) -> CompanyResponse:
        # TODO: extract requester_id from current_user
        return await company_service.update_company(company_id, data, requester_id="")

    @delete("/{company_id:str}", status_code=204)
    async def delete_company(self, company_id: str, company_service: CompanyService) -> None:
        # TODO: extract requester_id from current_user
        return await company_service.delete_company(company_id, requester_id="")
