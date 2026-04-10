from features.companies.schemas import CompanyCreateRequest, CompanyUpdateRequest, CompanyResponse
from features.companies.exceptions import CompanyNotFoundError, CompanyAlreadyExistsError, CompanyAccessDeniedError


class CompanyService:
    async def create_company(self, payload: CompanyCreateRequest, owner_id: str) -> CompanyResponse:
        raise NotImplementedError

    async def get_company(self, company_id: str) -> CompanyResponse:
        raise NotImplementedError

    async def update_company(
        self, company_id: str, payload: CompanyUpdateRequest, requester_id: str
    ) -> CompanyResponse:
        raise NotImplementedError

    async def delete_company(self, company_id: str, requester_id: str) -> None:
        raise NotImplementedError

    async def list_companies(self, page: int = 1, page_size: int = 20) -> list[CompanyResponse]:
        raise NotImplementedError
