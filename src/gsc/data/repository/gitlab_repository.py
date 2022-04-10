from rx import Observable, operators as ops
from gsc.constants import PAGING_ITEM_NUMBER
from gsc.data.repository.base_repository import BaseRepository
from gsc.data.request.gitlab_request import ProjectRequest, SearchRequest
from gsc.data.response.gitlab_response import ProjectResponse, FileResponse
from gsc.entities.gitlab_model import Project, File


class GitLabProjectRepository(BaseRepository):
    def __init__(self) -> None:
        super().__init__()
        self._request = ProjectRequest()

    def project_info(self, project_id: int) -> Observable:
        return self._request.project_info(project_id).pipe(ops.map(self.__mapping))

    def project_list(self, group_name: str) -> Observable:
        return self._request.project_list(group_name, PAGING_ITEM_NUMBER).pipe(
            ops.map(self.__mapping)
        )

    def __mapping(self, response: ProjectResponse) -> Project:
        project = Project()
        project.id = response.id
        project.name = response.name
        project.url = response.web_url
        return project


class GitLabSearchRepository(BaseRepository):
    def __init__(self) -> None:
        super().__init__()
        self._request = SearchRequest()

    def search(self, project_id: int, keyword: str) -> Observable:
        return self._request.search_in_project(project_id, keyword).pipe(
            ops.distinct(lambda item: item.path), ops.map(self.__mapping)
        )

    def __mapping(self, response: FileResponse) -> File:
        file = File()
        file.name = response.name
        file.path = response.path
        file.ref = response.ref
        file.data_preview = response.data_preview
        return file
