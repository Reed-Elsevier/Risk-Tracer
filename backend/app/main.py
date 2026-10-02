"""FastAPI application for deterministic RiskTracer investigations."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from app.config import Settings
from app.data import DataStore
from app.decisions import DecisionRepository
from app.investigation import InvestigationNotFound, build_investigation
from app.llm import explain_investigation
from app.models import (
    DecisionRequest,
    ExplainResponse,
    HealthResponse,
    Investigation,
    InvestigationRequest,
    InvoiceRecord,
    InvoiceSearchResult,
    ReviewDecision,
    SupplierRecord,
)


def create_app(settings: Settings | None = None, store: DataStore | None = None) -> FastAPI:
    configured_settings = settings or Settings()

    @asynccontextmanager
    async def lifespan(application: FastAPI):
        if application.state.store is None:
            application.state.store = DataStore(
                configured_settings.data_dir,
                configured_settings.db_path,
            )
            application.state.owns_store = True
        application.state.decisions = DecisionRepository(application.state.store.connection)
        yield
        if application.state.owns_store:
            application.state.store.close()

    application = FastAPI(title="RiskTracer API", version="0.1.0", lifespan=lifespan)
    application.state.settings = configured_settings
    application.state.store = store
    application.state.owns_store = False
    if store is not None:
        application.state.decisions = DecisionRepository(store.connection)

    application.add_middleware(
        CORSMiddleware,
        allow_origins=configured_settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    def current_store() -> DataStore:
        if application.state.store is None:
            application.state.store = DataStore(
                configured_settings.data_dir,
                configured_settings.db_path,
            )
            application.state.owns_store = True
        return application.state.store

    def current_decisions() -> DecisionRepository:
        if not hasattr(application.state, "decisions"):
            application.state.decisions = DecisionRepository(current_store().connection)
        return application.state.decisions

    def investigation_or_404(invoice_id: str) -> Investigation:
        try:
            return build_investigation(
                invoice_id,
                current_store(),
                current_decisions(),
                llm_available=bool(configured_settings.openai_api_key),
            )
        except InvestigationNotFound as error:
            raise HTTPException(status_code=404, detail=str(error)) from error

    @application.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        store_now = current_store()
        return HealthResponse(status="ok", invoices=len(store_now.frames["invoices"]))

    @application.post("/investigate", response_model=Investigation)
    def investigate(request: InvestigationRequest) -> Investigation:
        return investigation_or_404(request.invoice_id)

    @application.post("/investigate/explain", response_model=ExplainResponse)
    def explain(request: InvestigationRequest) -> ExplainResponse:
        if not configured_settings.openai_api_key:
            raise HTTPException(
                status_code=503,
                detail="LLM explanations are unavailable because OPENAI_API_KEY is not set.",
            )
        investigation = investigation_or_404(request.invoice_id)
        try:
            return explain_investigation(
                investigation,
                api_key=configured_settings.openai_api_key,
                model=configured_settings.openai_model,
            )
        except Exception as error:  # pragma: no cover - provider errors are environment-specific
            raise HTTPException(status_code=503, detail=f"LLM explanation failed: {error}") from error

    @application.get("/invoices", response_model=list[InvoiceSearchResult])
    def search_invoices(
        q: Annotated[str, Query(max_length=120)] = "",
        limit: Annotated[int, Query(ge=1, le=100)] = 20,
    ) -> list[InvoiceSearchResult]:
        rows = current_store().search_invoices(q, limit)
        return [InvoiceSearchResult.model_validate(row) for row in rows]

    @application.get("/suppliers/{supplier_id}")
    def supplier_profile(supplier_id: str) -> dict[str, object]:
        store_now = current_store()
        supplier_raw = store_now.supplier(supplier_id)
        if supplier_raw is None:
            raise HTTPException(status_code=404, detail=f"Supplier {supplier_id} not found")
        return {
            "supplier": SupplierRecord.model_validate(supplier_raw),
            "invoices": [
                InvoiceRecord.model_validate(row)
                for row in store_now.supplier_invoices(supplier_id)
            ],
        }

    @application.post(
        "/investigations/{invoice_id}/decisions",
        response_model=ReviewDecision,
    )
    def record_decision(invoice_id: str, request: DecisionRequest) -> ReviewDecision:
        investigation = investigation_or_404(invoice_id)
        if request.priority_override and not request.override_reason:
            raise HTTPException(status_code=422, detail="A priority override requires a reason")
        try:
            return current_decisions().create(invoice_id, request, investigation)
        except ValueError as error:
            raise HTTPException(status_code=422, detail=str(error)) from error

    @application.get(
        "/investigations/{invoice_id}/decisions",
        response_model=list[ReviewDecision],
    )
    def decision_history(invoice_id: str) -> list[ReviewDecision]:
        if current_store().invoice(invoice_id) is None:
            raise HTTPException(status_code=404, detail=f"Invoice {invoice_id} not found")
        return current_decisions().history(invoice_id)

    return application


app = create_app()
