from rx.core import Observable
from rx.subject import ReplaySubject
from rx import operators as ops
from gsc.data.response.project import Project
from gsc.data.response.search_result import SearchResult
from gsc.request.rx_task import rx_pool_scheduler
from gsc.data.repository.gitlab_search_repository import GitLabSearchRepository
from gsc.data.repository.gitlab_project_repository import GitLabProjectRepository


class GitLabSearchGroupUseCase:
    def __init__(self) -> None:
        self._project_repo = GitLabProjectRepository()
        self._on_searching = ReplaySubject()

    def on_searching(self) -> Observable:
        return self._on_searching

    def search(self, group_name: str, keyword: str) -> Observable:
        # Get all projects in group
        self._project_repo.project_list(group_name).pipe(
            ops.subscribe_on(rx_pool_scheduler()),
            ops.group_by(lambda proj: proj),
            ops.flat_map(
                lambda group: group.pipe(
                    ops.observe_on(rx_pool_scheduler()),
                    # Search in each project
                    ops.map(
                        lambda project: self.__do_search_in_project(project, keyword)
                    ),
                    # Ignore empty list
                    ops.filter(lambda item: item),
                )
            ),
            ops.flat_map(lambda item: item),
        ).subscribe(self._on_searching)

    def __do_search_in_project(self, project: Project, keyword: str):
        response = GitLabSearchRepository().do_search(project.id, keyword)
        if response:
            response.insert(0, project)
        return response


# TEMP : remove it later
if __name__ == "__main__":

    def print_console(item):
        if isinstance(item, Project):
            print(f"{[item.id]} {item.name}")
        elif isinstance(item, SearchResult):
            str_line = ", ".join(map(str, item.start_lines))
            print(f"{item.path} (line {str_line})")
        else:
            pass

    import multiprocessing

    event = multiprocessing.Event()

    usecase = GitLabSearchGroupUseCase()
    usecase.on_searching().subscribe(
        on_next=print_console,
        on_completed=lambda: (print("completed"), event.set()),
        on_error=print,
    )

    usecase.search("android", "chuck")
    event.wait()