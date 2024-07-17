import pathlib
import re
import time
from typing import *
from cli_user import *

# from PROJECT import PROJECT


# =====================================================================================================================
# VERSION = (0, 0, 1)   # keep russian lang by using utf-8
# VERSION = (0, 0, 2)   # reuse utf8+ del all capitalizing()
# VERSION = (0, 0, 3)   # detach dependence from importing PRJ
# VERSION = (0, 0, 4)   # use LINE_CODE_QUATATION for examples
# VERSION = (0, 0, 5)   # add BADGES block
# VERSION = (0, 0, 6)   # [BADGES] improve
# VERSION = (0, 0, 7)   # [BADGES] separate TestLinWin
# VERSION = (0, 0, 8)   # examples string add docstrings
VERSION = (0, 0, 9)   # add gen requirements_release_freezed


# =====================================================================================================================
class Exx_HistorySameVersionOrNews(Exception):
    pass


# =====================================================================================================================
class ReleaseFileBase:
    # ------------------------------------------------
    FILE_NAME: str = "FILE.md"
    PROJECT: Type['PROJECT'] = None

    # ------------------------------------------------
    LINE_SEPARATOR_MAIN: str = "*" * 80
    LINE_SEPARATOR_PART: str = "-" * 30

    def __init__(self, project: Type['PROJECT']):
        self.PROJECT = project

    @property
    def filepath(self) -> pathlib.Path:
        return pathlib.Path(self.FILE_NAME)

    # FILE WRITE ======================================================================================================
    def _file_clear(self) -> None:
        self.filepath.write_text("")

    def _file_append_lines(self, lines: Optional[Union[str, List[str]]] = None) -> None:
        # LINES ---------------------------------
        if not lines:
            lines = ""
        if isinstance(lines, str):
            lines = [lines, ]

        # WRITE ---------------------------------
        with self.filepath.open("a", encoding="utf8") as fo_append:
            for lines in lines:
                fo_append.write(f"{lines}\n")

    # LINES ===========================================================================================================
    def _lines_create__group(self, lines: List[str], title: Optional[str] = None, nums: bool = True) -> List[str]:
        group: List[str] = []

        if title:
            group.append(title.upper())

        for num, line in enumerate(lines, start=1):
            if nums:
                bullet = f"{num}. "
            else:
                bullet = "- "

            if isinstance(line, list):
                group.append(f"{bullet}{line[0]}:  ")
                for block in line[1:]:
                    group.append(f"\t- {block}  ")
            else:
                group.append(f"{bullet}{line}  ")
        return group

    def generate(self) -> None:
        pass


# =====================================================================================================================
class ReleaseReadme(ReleaseFileBase):
    # ------------------------------------------------
    FILE_NAME: str = "README.md"

    # ------------------------------------------------
    DIRNAME_EXAMPLES: str = "EXAMPLES"
    dirpath_examples: pathlib.Path = pathlib.Path(DIRNAME_EXAMPLES)

    SEPARATOR_PATTERN = r'(\**\n+)*## USAGE EXAMPLES'
    LINE_CODE_QUATATION: str = "```"

    # GENERATE ========================================================================================================
    def generate(self) -> None:
        self._file_clear()
        self.append_badges()
        self.append_main()
        self.append_examples()

    def append_badges(self) -> None:
        lines = [
            # VER -------------
            f"![Ver/TestedPython](https://img.shields.io/pypi/pyversions/{self.PROJECT.NAME_IMPORT})",
            f"![Ver/Os](https://img.shields.io/badge/os_development-Windows-blue)  ",

            # -----------------
            f"![repo/Created](https://img.shields.io/github/created-at/{self.PROJECT.AUTHOR_NICKNAME_GITHUB}/{self.PROJECT.NAME_IMPORT})",
            f"![Commit/Last](https://img.shields.io/github/last-commit/{self.PROJECT.AUTHOR_NICKNAME_GITHUB}/{self.PROJECT.NAME_IMPORT})",
            # f"![Tests/GitHubWorkflowStatus](https://img.shields.io/github/actions/workflow/status/{self.PROJECT.AUTHOR_NICKNAME_GITHUB}/{self.PROJECT.NAME_IMPORT}/tests.yml)",
            f"![Tests/GitHubWorkflowStatus](https://github.com/{self.PROJECT.AUTHOR_NICKNAME_GITHUB}/{self.PROJECT.NAME_IMPORT}/actions/workflows/test_linux.yml/badge.svg)",
            f"![Tests/GitHubWorkflowStatus](https://github.com/{self.PROJECT.AUTHOR_NICKNAME_GITHUB}/{self.PROJECT.NAME_IMPORT}/actions/workflows/test_windows.yml/badge.svg)  ",

            # -----------------
            f"![repo/Size](https://img.shields.io/github/repo-size/{self.PROJECT.AUTHOR_NICKNAME_GITHUB}/{self.PROJECT.NAME_IMPORT})",
            *[
                f"![Commit/Count/{period}](https://img.shields.io/github/commit-activity/{period}/{self.PROJECT.AUTHOR_NICKNAME_GITHUB}/{self.PROJECT.NAME_IMPORT})"
                for period in ["t", "y", "m", ]
            ],
            f"",

        ]
        self._file_append_lines(lines)

    def append_main(self) -> None:
        # FEATURES ----------------------------------------------------
        features = [
            f"",
            f"",
            f"## Features",
        ]
        for num, feature in enumerate(self.PROJECT.FEATURES, start=1):
            if isinstance(feature, list):
                features.append(f"{num}. {feature[0]}:  ")
                for block in feature[1:]:
                    features.append(f"\t- {block}  ")
            else:
                features.append(f"{num}. {feature}  ")

        # SUMMARY ----------------------------------------------------
        lines = [
            f"# {self.PROJECT.NAME_IMPORT} (current v{self.PROJECT.VERSION_STR}/![Ver/Pypi Latest](https://img.shields.io/pypi/v/{self.PROJECT.NAME_IMPORT}?label=pypi%20latest))",

            f"",
            f"## DESCRIPTION_SHORT",
            f"{self.PROJECT.DESCRIPTION_SHORT.strip()}",

            f"",
            f"## DESCRIPTION_LONG",
            f"{self.PROJECT.DESCRIPTION_LONG.strip()}",

            *features,

            f"",
            f"",
            self.LINE_SEPARATOR_MAIN,
            f"## License",
            f"See the [LICENSE](LICENSE) file for license rights and limitations (MIT).",

            f"",
            f"",
            f"## Release history",
            f"See the [HISTORY.md](HISTORY.md) file for release history.",

            f"",
            f"",
            f"## Installation",
            f"```commandline",
            f"pip install {self.PROJECT.NAME_INSTALL}",
            f"```",

            f"",
            f"",
            f"## Import",
            f"```python",
            f"from {self.PROJECT.NAME_IMPORT} import *",
            f"```",
        ]
        self._file_append_lines(lines)

    def append_examples(self) -> None:
        """
        NOTE: don't skip none-python files! it could be as part of examples! just name it in appropriate way!
        """
        LINES_EXAMPLES_START: List[str] = [
            f"",
            f"",
            self.LINE_SEPARATOR_MAIN,
            f"## USAGE EXAMPLES",
            f"See tests, sourcecode and docstrings for other examples.  ",
        ]
        self._file_append_lines(LINES_EXAMPLES_START)
        self._file_append_lines()

        files = []
        if self.dirpath_examples.exists():
            files = [item for item in self.dirpath_examples.iterdir() if item.is_file()]

        for index, file in enumerate(files, start=1):
            LINES = [
                self.LINE_SEPARATOR_PART,
                f"### {index}. {file.name}",
                self.LINE_CODE_QUATATION + ('python' if file.name.endswith(".py") else ''),
                file.read_text().strip(),
                self.LINE_CODE_QUATATION,
                f"",
            ]
            self._file_append_lines(LINES)

        self._file_append_lines(self.LINE_SEPARATOR_MAIN)


# =====================================================================================================================
class ReleaseHistory(ReleaseFileBase):
    # ------------------------------------------------
    FILE_NAME: str = "HISTORY.md"

    # ------------------------------------------------
    PATTERN_SEPARATOR_NEWS = r'#+ NEWS\s*'
    PATTERN_NEWS = r'#+ NEWS\s*(.+)\s*\*{10,}\s*'
    # PATTERN_NEWS = r'\n((?:\d+\.?){3} \((?:\d{2,4}[/:\s]?){6}\).*)\s*\*{10,}'

    LAST_NEWS: str = ""

    # PREPARE =========================================================================================================
    def load_last_news(self) -> None:
        string = self.filepath.read_text()

        # # VAR 1 --------------------------------
        # match = re.search(self.PATTERN_NEWS, string)
        # if match:
        #     self.LAST_NEWS = match[1]
        # # VAR 1 --------------------------------

        # VAR 2 --------------------------------
        splits = re.split(self.PATTERN_SEPARATOR_NEWS, string)
        if len(splits) > 1:
            self.LAST_NEWS = splits[-1]

            splits = re.split(r'\s*\*{10,}\s*', self.LAST_NEWS)
            self.LAST_NEWS = splits[0]

            splits = re.split(r'\s*0\.0\.0 \(', self.LAST_NEWS)
            self.LAST_NEWS = splits[0]

        else:
            self.LAST_NEWS = splits[0]

        # print(f"{string=}")
        # print(f"{self.LAST_NEWS=}")

    def check_new_release__is_correct(self) -> bool:
        # ----------------------------
        if self.LAST_NEWS.startswith(f"{self.PROJECT.VERSION_STR} ("):
            msg = f"exists_version"
            print(msg)
            return False

        # ----------------------------
        for news_item in self.PROJECT.NEWS:
            if isinstance(news_item, list):
                news_item = news_item[0]

            if re.search(r'- ' + str(news_item) + r'\s*\n', self.LAST_NEWS):
                msg = f"exists_news"
                print(msg)
                return False

        # ----------------------------
        return True

    # WORK ============================================================================================================
    def lines_create__news(self) -> List[str]:
        group: List[str] = [
            f"## NEWS",
            "",
            f"{self.PROJECT.VERSION_STR} ({time.strftime('%Y/%m/%d %H:%M:%S')})",
            self.LINE_SEPARATOR_PART,
        ]
        news_new = self._lines_create__group(self.PROJECT.NEWS, nums=False)
        group.extend(news_new)
        return group

    def generate(self) -> None:
        # PREPARE --------------------------------------
        self.load_last_news()
        if not self.check_new_release__is_correct():
            msg = f"[ERROR] Incorrect new data (INCREASE VERSION or CHANGE NEWS)"
            raise Exx_HistorySameVersionOrNews(msg)

        # WRITE ----------------------------------------
        self._file_clear()
        self.append_main()

    def append_main(self):
        lines = [
            f"# RELEASE HISTORY",
            f"",
            self.LINE_SEPARATOR_MAIN,
            *self._lines_create__group(self.PROJECT.TODO, "## TODO"),
            f"",
            self.LINE_SEPARATOR_MAIN,
            *self._lines_create__group(self.PROJECT.FIXME, "## FIXME"),
            f"",
            self.LINE_SEPARATOR_MAIN,
            *self.lines_create__news(),
            f"",
            self.LAST_NEWS,
            f"",
            self.LINE_SEPARATOR_MAIN,
        ]
        self._file_append_lines(lines)


# =====================================================================================================================
def release_files_update(project: Type['PROJECT']):
    CliUser().send("python -m pip freeze > requirements_release_freezed.txt")
    ReleaseReadme(project).generate()
    ReleaseHistory(project).generate()


# =====================================================================================================================
if __name__ == '__main__':
    pass


# =====================================================================================================================
