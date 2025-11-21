
from pathlib import Path
import sys

from fastapi import FastAPI,Request
from fastapi import Depends
from datetime import datetime

from fastapi import FastAPI

utils_path = Path.cwd().parent / "src" 
if str(utils_path) not in sys.path:
    sys.path.insert(0, str(utils_path))


from routers import relevant_queries
from routers import search_duckduckgo
from routers import web_data_fetcher
from routers import summarize_news_data
from routers import store_data_in_vector_db
from routers import search_data_in_vector_db
from routers import analysis_search_result
from routers import verifier_search_result
from routers import gemini_competitor_agent



app = FastAPI(
    title="Deep Research API",
    description="Competitor Analysis Project",
    version="1.0.0"
)


logging_path=r'f:\capstone_project2\src\logs'

app = FastAPI()

@app.middleware("http")
async def add_state_to_request(request: Request, call_next):
    url = str(request.url) 
    print(url)
    timestamp = datetime.utcnow().replace(second=0, microsecond=0)
    timestamp = timestamp.strftime("%Y-%m-%d_%H-%M-%S")
    request.state.logging_path = logging_path+'\\'+timestamp+'.log'
    response = await call_next(request)
    return response


app.include_router(relevant_queries.router, prefix="/api", tags=["Relevant Queries"])
app.include_router(search_duckduckgo.router, prefix="/api", tags=["Search News"])
app.include_router(web_data_fetcher.router, prefix="/api", tags=["Fetch data from web"])
app.include_router(store_data_in_vector_db.router, prefix="/api", tags=["Store data In DB "])
app.include_router(search_data_in_vector_db.router, prefix="/api", tags=["search data In DB "])
app.include_router(summarize_news_data.router, prefix="/api", tags=["Summarize News Data "])
app.include_router(analysis_search_result.router, prefix="/api", tags=["Analysis content "])
app.include_router(gemini_competitor_agent.router, prefix="/api", tags=["Verifier content "])




