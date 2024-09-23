import requests

from backend.data.block import Block, BlockCategory, BlockOutput, BlockSchema
from backend.data.model import SchemaField

from ._auth import (
    TEST_CREDENTIALS,
    TEST_CREDENTIALS_INPUT,
    GithubCredentials,
    GithubCredentialsField,
    GithubCredentialsInput,
)


class GithubMakePRBlock(Block):
    class Input(BlockSchema):
        credentials: GithubCredentialsInput = GithubCredentialsField("repo")
        repo_url: str = SchemaField(
            description="URL of the GitHub repository",
            placeholder="https://github.com/owner/repo",
        )
        title: str = SchemaField(
            description="Title of the pull request",
            placeholder="Enter the pull request title",
        )
        body: str = SchemaField(
            description="Body of the pull request",
            placeholder="Enter the pull request body",
        )
        head: str = SchemaField(
            description="The name of the branch where your changes are implemented. For cross-repository pull requests in the same network, namespace head with a user like this: username:branch.",
            placeholder="Enter the head branch",
        )
        base: str = SchemaField(
            description="The name of the branch you want the changes pulled into.",
            placeholder="Enter the base branch",
        )

    class Output(BlockSchema):
        status: str = SchemaField(
            description="Status of the pull request creation operation"
        )
        error: str = SchemaField(
            description="Error message if the pull request creation failed"
        )

    def __init__(self):
        super().__init__(
            id="0003q3r4-5678-90ab-1234-567890abcdef",
            description="This block creates a new pull request on a specified GitHub repository using OAuth credentials.",
            categories={BlockCategory.DEVELOPER_TOOLS},
            input_schema=GithubMakePRBlock.Input,
            output_schema=GithubMakePRBlock.Output,
            test_input={
                "repo_url": "https://github.com/owner/repo",
                "title": "Test Pull Request",
                "body": "This is a test pull request.",
                "head": "feature-branch",
                "base": "main",
                "credentials": TEST_CREDENTIALS_INPUT,
            },
            test_credentials=TEST_CREDENTIALS,
            test_output=[("status", "Pull request created successfully")],
            test_mock={
                "create_pr": lambda *args, **kwargs: "Pull request created successfully"
            },
        )

    @staticmethod
    def create_pr(
        credentials: GithubCredentials,
        repo_url: str,
        title: str,
        body: str,
        head: str,
        base: str,
    ) -> str:
        response = None
        try:
            repo_path = repo_url.replace("https://github.com/", "")
            api_url = f"https://api.github.com/repos/{repo_path}/pulls"
            headers = {
                "Authorization": credentials.bearer(),
                "Accept": "application/vnd.github.v3+json",
            }
            data = {"title": title, "body": body, "head": head, "base": base}

            response = requests.post(api_url, headers=headers, json=data)
            response.raise_for_status()

            return "Pull request created successfully"
        except requests.exceptions.HTTPError as http_err:
            if response and response.status_code == 422:
                error_details = response.json()
                return f"Failed to create pull request: {error_details.get('message', 'Unknown error')}"
            return f"Failed to create pull request: {str(http_err)}"
        except Exception as e:
            return f"Failed to create pull request: {str(e)}"

    def run(
        self,
        input_data: Input,
        *,
        credentials: GithubCredentials,
        **kwargs,
    ) -> BlockOutput:
        status = self.create_pr(
            credentials,
            input_data.repo_url,
            input_data.title,
            input_data.body,
            input_data.head,
            input_data.base,
        )
        if "successfully" in status:
            yield "status", status
        else:
            yield "error", status


class GithubReadPRBlock(Block):
    class Input(BlockSchema):
        credentials: GithubCredentialsInput = GithubCredentialsField("repo")
        pr_url: str = SchemaField(
            description="URL of the GitHub pull request",
            placeholder="https://github.com/owner/repo/pull/1",
        )
        include_pr_changes: bool = SchemaField(
            description="Whether to include the changes made in the pull request",
            default=False,
        )

    class Output(BlockSchema):
        title: str = SchemaField(description="Title of the pull request")
        body: str = SchemaField(description="Body of the pull request")
        user: str = SchemaField(description="User who created the pull request")
        changes: str = SchemaField(description="Changes made in the pull request")
        error: str = SchemaField(
            description="Error message if reading the pull request failed"
        )

    def __init__(self):
        super().__init__(
            id="0005g3h4-5678-90ab-1234-567890abcdeg",
            description="This block reads the body, title, user, and changes of a specified GitHub pull request using OAuth credentials.",
            categories={BlockCategory.DEVELOPER_TOOLS},
            input_schema=GithubReadPRBlock.Input,
            output_schema=GithubReadPRBlock.Output,
            test_input={
                "pr_url": "https://github.com/owner/repo/pull/1",
                "include_pr_changes": True,
                "credentials": TEST_CREDENTIALS_INPUT,
            },
            test_credentials=TEST_CREDENTIALS,
            test_output=[
                ("title", "Title of the pull request"),
                ("body", "This is the body of the pull request."),
                ("user", "username"),
                ("changes", "List of changes made in the pull request."),
            ],
            test_mock={
                "read_pr": lambda *args, **kwargs: (
                    "Title of the pull request",
                    "This is the body of the pull request.",
                    "username",
                ),
                "read_pr_changes": lambda *args, **kwargs: "List of changes made in the pull request.",
            },
        )

    @staticmethod
    def read_pr(credentials: GithubCredentials, pr_url: str) -> tuple[str, str, str]:
        try:
            api_url = pr_url.replace("github.com", "api.github.com/repos").replace(
                "/pull/", "/issues/"
            )

            headers = {
                "Authorization": credentials.bearer(),
                "Accept": "application/vnd.github.v3+json",
            }

            response = requests.get(api_url, headers=headers)
            response.raise_for_status()

            data = response.json()
            title = data.get("title", "No title found")
            body = data.get("body", "No body content found")
            user = data.get("user", {}).get("login", "No user found")

            return title, body, user
        except Exception as e:
            return f"Failed to read pull request: {str(e)}", "", ""

    @staticmethod
    def read_pr_changes(credentials: GithubCredentials, pr_url: str) -> str:
        try:
            api_url = (
                pr_url.replace("github.com", "api.github.com/repos").replace(
                    "/pull/", "/pulls/"
                )
                + "/files"
            )

            headers = {
                "Authorization": credentials.bearer(),
                "Accept": "application/vnd.github.v3+json",
            }

            response = requests.get(api_url, headers=headers)
            response.raise_for_status()

            files = response.json()
            changes = []
            for file in files:
                filename = file.get("filename")
                patch = file.get("patch")
                if filename and patch:
                    changes.append(f"File: {filename}\n{patch}")

            return "\n\n".join(changes)
        except Exception as e:
            return f"Failed to read PR changes: {str(e)}"

    def run(
        self,
        input_data: Input,
        *,
        credentials: GithubCredentials,
        **kwargs,
    ) -> BlockOutput:
        title, body, user = self.read_pr(
            credentials,
            input_data.pr_url,
        )
        if "Failed" in title:
            yield "error", title
        else:
            yield "title", title
            yield "body", body
            yield "user", user

        if input_data.include_pr_changes:
            changes = self.read_pr_changes(
                credentials,
                input_data.pr_url,
            )
            if "Failed" in changes:
                yield "error", changes
            else:
                yield "changes", changes
        else:
            yield "changes", "Changes not included"


class GithubAssignReviewerBlock(Block):
    class Input(BlockSchema):
        credentials: GithubCredentialsInput = GithubCredentialsField("repo")
        pr_url: str = SchemaField(
            description="URL of the GitHub pull request",
            placeholder="https://github.com/owner/repo/pull/1",
        )
        reviewer: str = SchemaField(
            description="Username of the reviewer to assign",
            placeholder="Enter the reviewer's username",
        )

    class Output(BlockSchema):
        status: str = SchemaField(
            description="Status of the reviewer assignment operation"
        )
        error: str = SchemaField(
            description="Error message if the reviewer assignment failed"
        )

    def __init__(self):
        super().__init__(
            id="0014o3p4-5678-90ab-1234-567890abcdef",
            description="This block assigns a reviewer to a specified GitHub pull request using OAuth credentials.",
            categories={BlockCategory.DEVELOPER_TOOLS},
            input_schema=GithubAssignReviewerBlock.Input,
            output_schema=GithubAssignReviewerBlock.Output,
            test_input={
                "pr_url": "https://github.com/owner/repo/pull/1",
                "reviewer": "reviewer_username",
                "credentials": TEST_CREDENTIALS_INPUT,
            },
            test_credentials=TEST_CREDENTIALS,
            test_output=[("status", "Reviewer assigned successfully")],
            test_mock={
                "assign_reviewer": lambda *args, **kwargs: "Reviewer assigned successfully"
            },
        )

    @staticmethod
    def assign_reviewer(
        credentials: GithubCredentials, pr_url: str, reviewer: str
    ) -> str:
        try:
            # Convert the PR URL to the appropriate API endpoint
            api_url = (
                pr_url.replace("github.com", "api.github.com/repos").replace(
                    "/pull/", "/pulls/"
                )
                + "/requested_reviewers"
            )

            # Log the constructed API URL for debugging
            print(f"Constructed API URL: {api_url}")

            headers = {
                "Authorization": credentials.bearer(),
                "Accept": "application/vnd.github.v3+json",
            }
            data = {"reviewers": [reviewer]}

            # Log the request data for debugging
            print(f"Request data: {data}")

            response = requests.post(api_url, headers=headers, json=data)
            response.raise_for_status()

            return "Reviewer assigned successfully"
        except requests.exceptions.HTTPError as http_err:
            if http_err.response.status_code == 422:
                return f"Failed to assign reviewer: The reviewer '{reviewer}' may not have permission or the pull request is not in a valid state. Detailed error: {http_err.response.text}"
            else:
                return f"HTTP error occurred: {http_err} - {http_err.response.text}"
        except Exception as e:
            return f"Failed to assign reviewer: {str(e)}"

    def run(
        self,
        input_data: Input,
        *,
        credentials: GithubCredentials,
        **kwargs,
    ) -> BlockOutput:
        status = self.assign_reviewer(
            credentials,
            input_data.pr_url,
            input_data.reviewer,
        )
        if "successfully" in status:
            yield "status", status
        else:
            yield "error", status


class GithubUnassignReviewerBlock(Block):
    class Input(BlockSchema):
        credentials: GithubCredentialsInput = GithubCredentialsField("repo")
        pr_url: str = SchemaField(
            description="URL of the GitHub pull request",
            placeholder="https://github.com/owner/repo/pull/1",
        )
        reviewer: str = SchemaField(
            description="Username of the reviewer to unassign",
            placeholder="Enter the reviewer's username",
        )

    class Output(BlockSchema):
        status: str = SchemaField(
            description="Status of the reviewer unassignment operation"
        )
        error: str = SchemaField(
            description="Error message if the reviewer unassignment failed"
        )

    def __init__(self):
        super().__init__(
            id="0015p3q4-5678-90ab-1234-567890abcdef",
            description="This block unassigns a reviewer from a specified GitHub pull request using OAuth credentials.",
            categories={BlockCategory.DEVELOPER_TOOLS},
            input_schema=GithubUnassignReviewerBlock.Input,
            output_schema=GithubUnassignReviewerBlock.Output,
            test_input={
                "pr_url": "https://github.com/owner/repo/pull/1",
                "reviewer": "reviewer_username",
                "credentials": TEST_CREDENTIALS_INPUT,
            },
            test_credentials=TEST_CREDENTIALS,
            test_output=[("status", "Reviewer unassigned successfully")],
            test_mock={
                "unassign_reviewer": lambda *args, **kwargs: "Reviewer unassigned successfully"
            },
        )

    @staticmethod
    def unassign_reviewer(
        credentials: GithubCredentials, pr_url: str, reviewer: str
    ) -> str:
        try:
            api_url = (
                pr_url.replace("github.com", "api.github.com/repos").replace(
                    "/pull/", "/pulls/"
                )
                + "/requested_reviewers"
            )
            headers = {
                "Authorization": credentials.bearer(),
                "Accept": "application/vnd.github.v3+json",
            }
            data = {"reviewers": [reviewer]}

            response = requests.delete(api_url, headers=headers, json=data)
            response.raise_for_status()

            return "Reviewer unassigned successfully"
        except Exception as e:
            return f"Failed to unassign reviewer: {str(e)}"

    def run(
        self,
        input_data: Input,
        *,
        credentials: GithubCredentials,
        **kwargs,
    ) -> BlockOutput:
        status = self.unassign_reviewer(
            credentials,
            input_data.pr_url,
            input_data.reviewer,
        )
        if "successfully" in status:
            yield "status", status
        else:
            yield "error", status


class GithubListReviewersBlock(Block):
    class Input(BlockSchema):
        credentials: GithubCredentialsInput = GithubCredentialsField("repo")
        pr_url: str = SchemaField(
            description="URL of the GitHub pull request",
            placeholder="https://github.com/owner/repo/pull/1",
        )

    class Output(BlockSchema):
        reviewers: list[dict[str, str]] = SchemaField(
            description="List of reviewers with their usernames and URLs"
        )
        error: str = SchemaField(
            description="Error message if listing reviewers failed"
        )

    def __init__(self):
        super().__init__(
            id="0016q3r4-5678-90ab-1234-567890abcdef",
            description="This block lists all reviewers for a specified GitHub pull request using OAuth credentials.",
            categories={BlockCategory.DEVELOPER_TOOLS},
            input_schema=GithubListReviewersBlock.Input,
            output_schema=GithubListReviewersBlock.Output,
            test_input={
                "pr_url": "https://github.com/owner/repo/pull/1",
                "credentials": TEST_CREDENTIALS_INPUT,
            },
            test_credentials=TEST_CREDENTIALS,
            test_output=[
                (
                    "reviewers",
                    [
                        {
                            "username": "reviewer1",
                            "url": "https://github.com/reviewer1",
                        }
                    ],
                )
            ],
            test_mock={
                "list_reviewers": lambda *args, **kwargs: [
                    {
                        "username": "reviewer1",
                        "url": "https://github.com/reviewer1",
                    }
                ]
            },
        )

    @staticmethod
    def list_reviewers(
        credentials: GithubCredentials, pr_url: str
    ) -> list[dict[str, str]]:
        try:
            api_url = (
                pr_url.replace("github.com", "api.github.com/repos").replace(
                    "/pull/", "/pulls/"
                )
                + "/requested_reviewers"
            )
            headers = {
                "Authorization": credentials.bearer(),
                "Accept": "application/vnd.github.v3+json",
            }

            response = requests.get(api_url, headers=headers)
            response.raise_for_status()

            data = response.json()
            reviewers = [
                {"username": reviewer["login"], "url": reviewer["html_url"]}
                for reviewer in data.get("users", [])
            ]

            return reviewers
        except Exception as e:
            return [{"username": "Error", "url": f"Failed to list reviewers: {str(e)}"}]

    def run(
        self,
        input_data: Input,
        *,
        credentials: GithubCredentials,
        **kwargs,
    ) -> BlockOutput:
        reviewers = self.list_reviewers(
            credentials,
            input_data.pr_url,
        )
        if any("Failed" in reviewer["url"] for reviewer in reviewers):
            yield "error", reviewers[0]["url"]
        else:
            yield "reviewers", reviewers
