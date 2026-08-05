from services.analysis_service import AnalysisService

service = AnalysisService()

analysis = service.analyze(
    "The salary is great but management is poor."
)

print(analysis.model_dump_json(indent=4))

print(service.review_count())