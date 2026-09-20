import os
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, HttpUrl
from dotenv import load_dotenv
import trafilatura
import json

from x402.http.middleware.fastapi import PaymentMiddlewareASGI
from x402.http import HTTPFacilitatorClient, FacilitatorConfig, PaymentOption
from x402.http.types import RouteConfig
from x402.server import x402ResourceServer
from x402.mechanisms.evm.exact import ExactEvmServerScheme

load_dotenv()

EVM_ADDRESS = os.getenv("EVM_ADDRESS", "0x3FfCEdBE43De60Dcc58ebF5c737F5c47e8De59FD")
FACILITATOR_URL = os.getenv("FACILITATOR_URL", "https://x402.org/facilitator")
PRICE = os.getenv("PRICE", "$0.01")
EVM_NETWORK = os.getenv("EVM_NETWORK", "eip155:84532")

if not EVM_ADDRESS.startswith("0x"):
    raise ValueError("EVM_ADDRESS invalide")

app = FastAPI(
    title="Clean Webpage Reader",
    description="Envoie une URL, recois le contenu principal en texte propre et Markdown.",
    version="0.2.0",
)

facilitator = HTTPFacilitatorClient(FacilitatorConfig(url=FACILITATOR_URL))
server = x402ResourceServer(facilitator)
server.register(EVM_NETWORK, ExactEvmServerScheme())

routes = {
    "GET /read": RouteConfig(
        accepts=[
            PaymentOption(
                scheme="exact",
                price=PRICE,
                network=EVM_NETWORK,
                pay_to=EVM_ADDRESS,
            )
        ],
        mime_type="application/json",
        description="Extract clean text and markdown from a URL",
    )
}
app.add_middleware(PaymentMiddlewareASGI, routes=routes, server=server)

class PageResult(BaseModel):
    url: str
    title: str | None = None
    description: str | None = None
    text: str | None = None
    markdown: str | None = None

@app.get("/health")
def health():
    return {
        "status": "ok",
        "paid_endpoint": "/read",
        "price": PRICE,
        "network": EVM_NETWORK,
        "pay_to": EVM_ADDRESS,
    }

@app.get("/read", response_model=PageResult)
def read_page(url: HttpUrl = Query(..., description="URL de la page a lire")):
    downloaded = trafilatura.fetch_url(str(url))
    if not downloaded:
        raise HTTPException(status_code=400, detail="Impossible de telecharger la page")

    metadata = trafilatura.extract(
        downloaded,
        output_format="json",
        include_comments=False,
        include_tables=True,
        with_metadata=True,
    )
    markdown = trafilatura.extract(
        downloaded,
        output_format="markdown",
        include_comments=False,
        include_tables=True,
    )
    text = trafilatura.extract(
        downloaded,
        output_format="txt",
        include_comments=False,
    )

    if not text and not markdown:
        raise HTTPException(status_code=422, detail="Aucun contenu principal trouve")

    title = None
    description = None
    if metadata:
        try:
            data = json.loads(metadata)
            title = data.get("title")
            description = data.get("description")
        except Exception:
            pass

    return PageResult(
        url=str(url),
        title=title,
        description=description,
        text=text,
        markdown=markdown,
    )
