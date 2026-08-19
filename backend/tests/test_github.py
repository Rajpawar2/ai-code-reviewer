from app.services.github_service import GitHubService


def test_github_url_validation():
    valid_urls = [
        "https://github.com/torvalds/linux",
        "https://github.com/psf/requests",
        "https://github.com/tiangolo/fastapi.git",
        "http://github.com/user/my-repo/"
    ]
    invalid_urls = [
        "https://gitlab.com/owner/repo",
        "https://github.com/",
        "ftp://github.com/user/repo",
        "not_a_url",
        "https://github.com/user/repo/extra/path"
    ]
    for url in valid_urls:
        assert GitHubService.validate_github_url(url) is True
    for url in invalid_urls:
        assert GitHubService.validate_github_url(url) is False


def test_github_invalid_url_rejected_by_api(client, auth_headers):
    payload = {
        "repository_url": "https://malicious-site.com/repo"
    }
    response = client.post("/api/github/analyze", json=payload, headers=auth_headers)
    assert response.status_code == 400
    data = response.json()
    error_msg = data.get("error", {}).get("message") or data.get("detail", "")
    assert "Invalid GitHub repository URL" in error_msg
