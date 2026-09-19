import json

from src.creator_service import ReleaseRequest, infrai_client, run_release


if __name__ == "__main__":
    request = ReleaseRequest(creator="Mina", title="Behind the edit", source_text="Three cuts that shape this week's video.", subscribers=["ada@example.com"])
    print(json.dumps(run_release(request, infrai_client()).model_dump(), indent=2))

